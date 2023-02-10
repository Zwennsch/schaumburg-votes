from flask import (
    Blueprint, flash, g, redirect, render_template
)
from voting.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    # get db
    db = get_db()
    username = None
    # get username if g.user is not None:
    if g.user:
        username = db.execute('SELECT username FROM user WHERE id = ?', (g.user['id']))
        
    return render_template('views/index.html', username = username )
