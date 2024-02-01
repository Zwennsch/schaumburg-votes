from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from voting.db import get_db
from voting.helpers import is_username_taken, add_user_to_database, get_query_for_nth_vote, calculate_courses
from voting.auth import login_required, admin_required
from voting.models import get_courses_list
from voting.cache import get_cached_classes, get_cache
from datetime import datetime, timedelta, timezone

bp = Blueprint('views', __name__)

cache = get_cache()

@bp.route('/')
def index():
    user = None
    if g.user:
        user = g.user
        user_id = g.user['id']
        if g.user['vote_passed'] == 1:
            db = get_db()
            vote = db.execute(
                "SELECT * FROM vote WHERE user_id = ?", (user_id,)).fetchone()
            return render_template('views/voted.html', vote=vote)
    return render_template('views/index.html', user=user, active_page='index')


@bp.route('/vote', methods=('GET', 'POST'))
@login_required
def vote():
    grade = int(g.user['class'][:-1])
    if request.method == 'GET':
        return render_template('views/vote.html', active_page='vote', grade=grade, courses = get_courses_list())

    # case for POST
    else:
        wahl_1 = request.form.get("wahl1")
        wahl_2 = request.form.get("wahl2")
        wahl_3 = request.form.get("wahl3")
        error = None

        votes_list = [wahl_1, wahl_2, wahl_3]
        # check that a vote for every choice has been made:
        if None in votes_list:
            error = "Mindestens ein Kurs nicht ausgewählt. Bitte wiederholen"

        # check for no duplicates
        elif len(votes_list) != len(set(votes_list)):
            error = "Mindestens ein Kurs doppelt gewählt"

        # check that only courses that contains users class are in vote
        if error is None:
            for course in get_courses_list():
                if course.name in votes_list:
                    if grade not in course.classes:
                        error = "Mindestens ein Kurs ist nicht für deinen Jahrgang vorgesehen."
                        break

        if error is None:
            db = get_db()
            id = g.user['id']
            # update if vote already passed
            if g.user['vote_passed'] == 1:
                db.execute(
                    "UPDATE vote SET first_vote = ?, second_vote = ?, third_vote = ?,"
                    "date_created = datetime('now', 'localtime')"
                    "WHERE user_id = ?",
                    (wahl_1, wahl_2, wahl_3, id)
                )
                flash("Deine Wahl wurde aktualisiert", "success")

            # save first votes into vote-table in db
            else:
                db.execute(
                    "INSERT INTO vote (user_id, date_created, first_vote, second_vote, third_vote)"
                    "VALUES (?,datetime('now', 'localtime'),?,?,?)",
                    (id, wahl_1, wahl_2, wahl_3)
                )
                # update vote_passed for user
                db.execute(
                    "UPDATE user SET vote_passed = 1 WHERE id = ?",
                    (id,)
                )
                flash("Deine Wahl wurde gespeichert", "success")

            db.commit()
            return redirect(url_for('views.index'))
        flash(error, "warning")
        return render_template('views/vote.html')


@bp.route("/course-overview")
@cache.cached(timeout=50)
def overview():
    return render_template('views/courses.html', active_page='overview', courses = get_courses_list())


# Admin pages

@bp.route("/admin",)
@admin_required
def admin_page():
    return render_template('views/admin/admin.html')


@bp.route("/admin/add-student", methods=('GET', 'POST'))
@admin_required
def add_student():
    # case for adding a new student:
    classes = get_cached_classes()
    if request.method == 'POST':
        error = None
        student_class = request.form.get('class')
        if student_class != None:
            student_class = student_class.replace("('", "")
            student_class = student_class.replace("',)", "")

        entries = {'first_name': request.form.get('first_name'),
                   'last_name': request.form.get('last_name'),
                   'username': request.form.get('username'),
                   'password': request.form.get('password'),
                   'password_check': request.form.get('password_check'),
                   'class': student_class
                   }
        for entry in entries:
            if entries[entry] is None:
                error = 'Mindestens ein Eintrag nicht ausgefüllt'
                break
            else:
                entries[entry] = entries[entry].strip()  # type: ignore

        db = get_db()
        if error is None and entries['password']:
            if entries['password'] != entries['password_check']:
                error = 'Fehler bei der Wiederholung des Passworts'
            elif len(entries['password']) < 5:
                error = 'Passwort muss mindestens 5 Zeichen lang sein. Bitte wiederholen'
            # check that 'class' is valid
            elif is_username_taken(entries['username'], db):
                error = 'Benutzername bereits vergeben'

            if error is None:
                if any(student_class in value for value in classes):
                    error = None
                else:
                    error = 'Klasse ungültig'

        # add user to database
        if error is None:
            add_user_to_database(entries['first_name'], entries['last_name'],
                                 entries['username'], entries['password'], entries['class'], db)
            flash('Neuer Schüler erfolgreich hinzugefügt', 'success')
            return redirect(url_for('views.admin_page'))

        else:
            flash(error, 'warning')
            return redirect(url_for('views.add_student'))

    # case for 'GET'
    return render_template('views/admin/add_student.html', active_page='add-student', classes=classes)


@bp.route("/admin/delete-student/all-students", methods=('GET', 'POST'))
@admin_required
def delete_student_from_class():
    if request.method == 'POST':
        selected_students_ids = request.form.getlist('selected_students')
        if len(selected_students_ids) != 0:
            db = get_db()
            for id in selected_students_ids:
                db.execute("DELETE FROM user WHERE id = ?", (id,))
            db.commit()
            if len(selected_students_ids) <= 1:
                flash('Schüler wurde erfolgreich aus Datenbank gelöscht', 'info')
            else:
                flash('Schüler wurden erfolgreich aus Datenbank gelöscht', 'info')
        else:
            flash('No user selected', 'info')
        return redirect(url_for('views.admin_page'))

    # GET
    db = get_db()
    student_class = request.args['student_class']
    students = db.execute(
        "SELECT id, first_name, last_name, class FROM user WHERE class = ? ORDER BY last_name ASC", (student_class,)).fetchall()

    return render_template('views/admin/students_by_class_delete.html', active_page='delete-student', student_class=student_class, students=students)


@bp.route("/admin/delete-student", methods=('GET', 'POST'))
@admin_required
def delete_student():
    if request.method == 'POST':
        student_class = request.form.get('class')
        if student_class != None:
            student_class = student_class.replace("('", "")
            student_class = student_class.replace("',)", "")
        else:
            flash('No class selected or class not in database' 'error')
            return redirect(url_for('views.admin_page'))
        return redirect(url_for('views.delete_student_from_class', active_page='delete-student', student_class=student_class))
    return render_template('views/admin/delete_student.html', active_page='delete-student', classes=get_cached_classes())


@bp.route("/admin/class-results", methods=('GET', 'POST'))
@admin_required
def class_results():
    if request.method == 'POST':
        selected_class = request.form.get('selected_class')
        db = get_db()
        class_results = db.execute(
            "SELECT first_name, last_name, vote_passed, first_vote, second_vote, third_vote from user INNER JOIN vote ON user.id = vote.user_id WHERE class = ? AND vote_passed = 1 ORDER BY last_name", (selected_class,)).fetchall()
        return render_template('views/admin/show_results_per_class.html', active_page='class-results', class_results=class_results, selected_class=selected_class)
    # case for 'GET'
    return render_template('views/admin/choose_class.html', active_page='class-results', classes=get_cached_classes())


@bp.route("/admin/course-results", methods=('GET', 'POST'))
@admin_required
def course_results():
    if request.method == 'POST':
        selected_course = request.form.get('selected_course')
        # Fetch data from the database based on the selected course
        db = get_db()
        # First_vote-query
        query_first = get_query_for_nth_vote('first_vote')
        results_first = db.execute(query_first, (selected_course,)).fetchall()
        query_second = get_query_for_nth_vote('second_vote')
        results_second = db.execute(
            query_second, (selected_course,)).fetchall()
        query_third = get_query_for_nth_vote('third_vote')
        results_third = db.execute(query_third, (selected_course,)).fetchall()
        return render_template('views/admin/show_results_per_course.html', active_page='course-results', selected_course=selected_course, results_first=results_first, results_second=results_second, results_third=results_third)
    # case for 'GET'
    return render_template('views/admin/get_results_per_course.html', active_page='course-results', courses = get_courses_list())


@bp.route("/admin/course-proposal", methods=('GET', 'POST'))
@admin_required
def course_proposal():
    if request.method == 'POST':
        selected_course = request.form.get('selected_course')
        if not selected_course:
            flash('Bitte Kurs auswählen', category='warning')
            return redirect(url_for('views.course_proposal'))
        course_proposal = get_db().execute("SELECT * FROM user WHERE final_course = ?", (selected_course,)).fetchall()
        if (len(course_proposal)) == 0:
            if (selected_course == 'unfulfilled_wish'):
                flash('Alle Wünsche erfüllt!', category='info')
            else:
                flash('Kein Vorschlag für diesen Kurs gefunden')
            return redirect(url_for('views.admin_page'))
        return render_template('views/admin/course-proposal.html', active_page='course-proposal', selected_course=selected_course, course_proposal=course_proposal)
    return render_template('views/admin/calculated.html', active_page='course-proposal', courses = get_courses_list())


@bp.route("/admin/course-calculation")
@admin_required
def calculate_cs():
    # TODO: I have to somehow make sure, that everyone voted... 
    # otherwise the admin should be redirected to views.admin    
    calculate_courses(get_db())
    flash('Kurse wurden berechnet', category='info')
    return redirect(url_for('views.course_proposal', active_page='course-proposal'))


@bp.before_app_request
def init_admin_status():
    g.admin = False  # Initialize g.admin to False for each request
    if session.get('admin'):
        g.admin = True  # Set g.admin based on session data if user is an admin


@bp.before_request
def track_admin_activity():
    if g.admin:  # Check if user is an admin
        last_activity = session.get('last_activity')
        now = datetime.now(timezone.utc)

        if not last_activity:
            session['last_activity'] = now
        else:
            elapsed_time = now - last_activity
            if elapsed_time >= timedelta(minutes=10):  # Timeout period
                session.clear()
                g.admin = False  # Clear session to log out admin user
            else:
                session['last_activity'] = now
