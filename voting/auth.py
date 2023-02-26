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
        if request.form.get('username') is None:
            flash("must enter username", 'error')
            return render_template('auth/login.html')
        username = request.form.get('username')

        if request.form.get('password') is None:
            flash("must enter password", 'error')
            return render_template('auth/login.html')
            # TODO: I might have to change the default value, actually there shouldn't be one.
        password = request.form.get('password', default= '')

        db = get_db()
        error = None
            
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # case for not signed in successfully, error is set to value
        if user is None:
            error = 'Incorrect username'
        # TODO:just for testing purpose, has to be switched to check_password_hash later
        elif not password == user['password']:
       # elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        # case that a user us successfully logged_in
        if error is None:
            session.clear()
            # set the session['user_id'] value correct:
            session['user_id'] = user['id']
            flash("successfully logged in", 'info')
            return redirect(url_for('views.index'))
        
        flash(error)
        
    # case for request.method == 'GET'
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.index'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# decorator for each view, that requires a login. 
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # redirect to login if user is not loaded
            flash("Please Login First", category="info")
            return redirect(url_for('auth.login'))
        # return original view, if user id logged in
        return view(**kwargs)

    return wrapped_view
