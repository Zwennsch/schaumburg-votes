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
        return render_template('views/vote2.html')
    # case for POST
    else:
        # TODO: implement POST case for vote:
        wahl_1 = request.form.get("wahl1")
        wahl_2 = request.form.get("wahl2")
        wahl_3 = request.form.get("wahl3")
        # save votes to db 

        print('in POST for vote')

    return redirect(url_for('views.index'))

            


@bp.route('/')
def index():
    # get db
    db = get_db()
    username = None
    # get username if g.user is not None:
    if g.user:
        
        username = g.user['username']
    return render_template('views/index.html', username = username )