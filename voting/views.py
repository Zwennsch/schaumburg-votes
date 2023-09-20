from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, current_app, url_for
)
from voting.db import get_db
from voting.auth import login_required, admin_required
from voting.models import load_courses
from voting.cache import get_cached_classes, get_cache
from datetime import datetime, timedelta, timezone

# from voting.models import get_courses

bp = Blueprint('views', __name__)

cache = get_cache()

@bp.before_app_request
def init_admin_status():
    g.admin = False  # Initialize g.admin to False for each request
    if session.get('admin'):
        g.admin = True  # Set g.admin based on session data if user is an admin


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
        return render_template('views/vote.html', active_page='vote', grade=grade)

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
        print('grade', grade)
        if error is None:
            for course in g.courses:
                if course.name in votes_list:
                    if grade not in course.classes:
                        # print('gewählter Kurs:', course.name)
                        # print('grades_list des Kurses: ', course.classes)
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
                #    print('vote already passed')
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
@cache.cached()
def overview():
    return render_template('views/courses.html', active_page='overview')


# Admin pages

@bp.route("/admin",)
@admin_required
def admin_page():
    return render_template('views/admin.html')


@bp.route("/admin/add-student", methods=('GET', 'POST'))
@admin_required
def add_student():
    # case for adding a new student:
    classes = get_cached_classes()
    if request.method == 'POST':
        pass
    return render_template('views/add_student.html', active_page='add-student', classes=classes)


@bp.route("/admin/delete-student", methods=('GET', 'POST'))
@admin_required
def delete_student():
    # case for deleting a new student:
    if request.method == 'POST':
        pass
    return render_template('views/delete_student.html', active_page='delete-student')


@bp.route("/admin/class-results", methods=('GET', 'POST'))
@admin_required
def class_results():
    # case for deleting a new student:
    if request.method == 'POST':
        pass
    # case for 'GET'
    return render_template('views/class_results.html', active_page='class-results')


@bp.route("/admin/course-results", methods=('GET', 'POST'))
@admin_required
def course_results():
    if request.method == 'POST':
        selected_course = request.form.get('selected_course')

        # Fetch data from the database based on the selected course
        db = get_db()

        query = "SELECT first_name, last_name, class, first_vote " \
            "FROM user "\
            "INNER JOIN vote ON user.id = vote.user_id " \
            "WHERE vote.first_vote = ?"
        results = db.execute(query, (selected_course,)).fetchall()
        print(results)
        return render_template('views/course_results.html', selected_course=selected_course, results=results,)
    # case for 'GET'
    return render_template('views/choose_per_course.html', active_page='course-results')

@bp.before_request
def load_course_list():
    g.courses = load_courses(current_app)


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
                session.clear()  # Clear session to log out admin user
            else:
                session['last_activity'] = now
