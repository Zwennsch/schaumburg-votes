from flask import (
    Blueprint, flash, g, redirect, render_template, request, current_app, url_for
)
from voting.db import get_db
from voting.auth import login_required
from voting.models import get_courses

bp = Blueprint('views', __name__)

@bp.route('/vote', methods=('GET', 'POST'))
@login_required
def vote():
    if request.method == 'GET':
        courses = get_courses(current_app)
        return render_template('views/vote2.html', courses = courses)

    # case for POST
    else:
        wahl_1 = request.form.get("wahl1")
        wahl_2 = request.form.get("wahl2")
        wahl_3 = request.form.get("wahl3")

        # check that a vote for every choice has been made:
        if None in (wahl_1, wahl_2, wahl_3):
            flash("Invalid vote. Please vote again.", "warning")
            return redirect(url_for('views.vote'))

        db = get_db()
        id = g.user['id']
        #update if vote already passed
        if g.user['vote_passed'] == 1:
           db.execute(
                "UPDATE vote SET first_vote = ?, second_vote = ?, third_vote = ?,"
                "date_created = datetime('now', 'localtime')"
                "WHERE user_id = ?", 
                (wahl_1, wahl_2, wahl_3, id)
           )
        #    print('vote already passed')
           flash("your vote has been updated", "success")

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
            flash("Your Vote has been saved!", "success")
        db.commit()

    return redirect(url_for('views.index'))

            


@bp.route('/')
def index():
    user = None
    # get username if g.user is not None:
    if g.user:
        user = g.user
    return render_template('views/index.html', user = user )