from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, current_app, url_for
)
from voting.db import get_db
from voting.auth import login_required
from voting.models import load_courses
from datetime import datetime, timedelta, timezone

# from voting.models import get_courses

bp = Blueprint('views', __name__)

@bp.before_app_request
def init_admin_status():
    print('in init_admin_status')
    g.admin = False  # Initialize g.admin to False for each request
    if session.get('admin'):
        g.admin = True  # Set g.admin based on session data if user is an admin



@bp.route('/vote', methods=('GET', 'POST'))
@login_required
def vote():
    if request.method == 'GET':
        return render_template('views/vote.html', active_page='vote')

    # case for POST
    else:
        wahl_1 = request.form.get("wahl1")
        wahl_2 = request.form.get("wahl2")
        wahl_3 = request.form.get("wahl3")
        error = None

        votes_list = [wahl_1, wahl_2, wahl_3]
        # check that a vote for every choice has been made:
        if None in votes_list:
            error = ("Mindestens ein Kurs nicht ausgewählt. Bitte wiederholen")

        # check for no duplicates
        elif len(votes_list) != len(set(votes_list)):
            error = ("Mindestens ein Kurs doppelt gewählt")

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


@bp.before_app_request
def load_course_list():
    g.courses = load_courses(current_app)

@bp.before_request
def track_admin_activity():
    if g.admin:  # Check if user is an admin (adjust as needed)
        last_activity = session.get('last_activity')
        now = datetime.now(timezone.utc)

        if not last_activity:
            session['last_activity'] = now
        else:
            elapsed_time = now - last_activity
            if elapsed_time >= timedelta(minutes=1):  # Timeout period
                session.clear()  # Clear session to log out admin user
            else:
                session['last_activity'] = now


@bp.route("/admin", methods=('GET', 'POST'))
def admin_page():
    g.admin = session.get('admin')
    if not session.get('admin'):
        flash('Permission denied. Log in as admin user', category='warning')
        return redirect(url_for('views.index'))
    if request.method == 'POST':
        # TODO: 
        pass
    return render_template('views/admin.html')
        

@bp.route("/course-overview")
def overview():
    return render_template('views/courses.html', active_page='overview')


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
