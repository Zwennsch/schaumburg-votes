import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash

from voting.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        error = None
        category = ''
        if request.form.get('username') == '':
            error = "Bitte Benutzernamen eingeben!"
            category = 'error'

        if request.form.get('password') == '':
            error = "Bitte Passwort eingeben!"
            category = 'error'

        # neither username or password are empty
        if error is None:
            # TODO: I might have to change the default value, actually there shouldn't be one.
            password = request.form.get('password', default='')
            username = request.form.get('username')
            db = get_db()

            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            # case for not signed in successfully, error is set to value
            if user is None:
                error = 'Falscher Benutzername'
                category = 'danger'
            elif not check_password_hash(user['password_hash'], password):
                error = 'Falsches Passwort'
                category = 'danger'

            # case that a user is successfully logged_in
            if error is None:
                session.clear()
                # set the session['user_id'] value correct:
                session['user_id'] = user['id']
                flash("Erfolgreich eingeloggt", 'success')
                return redirect(url_for('views.index'))

        flash(error, category=category)

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
            flash("Bitte erst einloggen.", category="info")
            return redirect(url_for('auth.login'))
        # return original view, if user id logged in
        return view(**kwargs)

    return wrapped_view
