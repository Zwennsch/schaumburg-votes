from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from voting.db import get_db
from voting.auth import login_required

bp = Blueprint('views', __name__)

@bp.route('/vote', methods=('GET', 'POST'))
@login_required
def vote():
    if request.method == 'GET':
        if g.user['vote_passed'] == 1:
            flash("already voted, you can change your vote now")
        return render_template('views/vote2.html')
    # case for POST
    else:
        wahl_1 = request.form.get("wahl1")
        wahl_2 = request.form.get("wahl2")
        wahl_3 = request.form.get("wahl3")

        # save votes into vote-table in db 
        id = g.user['id']
        db = get_db()

        db.execute(
            "INSERT INTO vote (user_id, date_created, first_vote, second_vote, third_vote)"
            "VALUES (?,datetime('now', 'localtime'),?,?,?)",
            (id, wahl_1, wahl_2, wahl_3)
        )
        flash("your vote has been saved!")

        # update vote passed for user
        db.execute(
            "UPDATE user SET vote_passed = 1 WHERE id = ?",
            (id,)
        )
        db.commit()

    return redirect(url_for('views.index'))

            


@bp.route('/')
def index():

    user = None
    # get username if g.user is not None:
    if g.user:
        user = g.user
    return render_template('views/index.html', user = user )