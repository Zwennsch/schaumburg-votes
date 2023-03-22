import sqlite3

import click
from flask import current_app, g
from voting.helpers import fill_user_db


def get_db():
    """Returns the database for the 'g' object.

    Sets db to the actual ['DATABASE'] from current_app.config if there isn't any db in the g object
    """

    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory=sqlite3.Row

    return g.db

def close_db(e=None):
    # the pop method on the g object gets and removes the given attribute by name
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def my_test():
    print("in my_test")   



@click.command('my-test')
def my_test_command():
    my_test()
    click.echo('tested')

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')

@click.command('fill-user-db')
def fill_user_db_command():
    """Fills up the user-db and uses a student.csv file in instance folder to do so.
    Provides each user with a predefined 5 character password. 
    The passwords gets stored in a student_pwd.csv file in the instance folder
    """
    fill_user_db(current_app.config['STUDENTS'], get_db())
    click.echo('user-db initialized')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(fill_user_db_command)
    app.cli.add_command(my_test_command)