import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from voting.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        if not request.form.get('username'):
            flash("must enter username", 'error')
            return redirect(url_for('/login'))
        username = request.form.get('username')

        if not request.form.get('password'):
            flash("must enter password", 'error')
            return redirect(url_for('/login'))
        password = request.form.get('password')

        db = get_db
        error = None
            
        user = db.execute(
            'SELECT FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            # TODO: I am not sure of how to provide the 'endpoint string' for the 'url_for' function. Have to check when implementing 
            return redirect(url_for('vote_now'))
        
        flash(error)
        # TODO: Why can't I use redirect('/login') ??
        return render_template('auth/login.html')

