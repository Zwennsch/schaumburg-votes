from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from voting.db import get_db

bp = Blueprint('views', __name__)

@bp.route('/vote', methods=('GET', 'POST'))
def vote():
    if request.method == 'GET':
        # make sure a user is logged in, otherwise redirect use flash and redirect to login
        if session.get('user_id') == None:
            flash("Please Login First", category="info")
            redirect(url_for('auth.login'))
        else:
            return render_template('views/vote.html')
   
    # case for POST
    else:
        # TODO: implement POST case for vote:

        print('in POST for vote')

    return redirect(url_for('views.index'))

            


@bp.route('/')
def index():
    # get db
    db = get_db()
    username = None
    # get username if g.user is not None:
    if g.user:
        id = g.user['id']
        ##TODO:needs to be fixed because db command doesn't work.
        username = db.execute('SELECT username FROM user WHERE id = ?', id)
        
    return render_template('views/index.html', username = username )