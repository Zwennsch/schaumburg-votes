from flask import (
    Blueprint, flash, g, redirect, render_template
)
from voting.db import get_db

bp = Blueprint('vote', __name__)

@bp.route('/vote', methods=('GET', 'POST'))
def vote():
    return render_template('views/vote.html')
