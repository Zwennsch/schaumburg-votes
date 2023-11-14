import sqlite3
import click
from flask import current_app, g
from voting.helpers import fill_user_db, add_new_admin_into_admin_db, is_username_taken, calculate_courses


def get_db():
    """Returns the database for the 'g' object.

    Sets db to the actual ['DATABASE'] from current_app.config if there isn't any db in the g object
    """

    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

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


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')


@click.command('fill-user-db')
def fill_user_db_command():
    try:
        fill_user_db(user_input_csv_file=current_app.config['STUDENTS'],
                     user_output_psw_csv=current_app.config['STUDENTS_PWD'], db=get_db())
    except:
        click.echo('no students.csv file found.')
        return
    click.echo('user-db initialized')


@click.command('create-admin')
@click.argument('name')
@click.argument('password')
def create_admin_command(name, password):
    if len(password) < 5:
        click.echo('password must be at least 5 characters long. Try again')
        return
    # check if username already exists:
    db = get_db()
    if is_username_taken(name, db):
        click.echo('username already exists. Please choose another one')
        return
    try:
        add_new_admin_into_admin_db(name, password, db=get_db())
    except:
        click.echo('error while accessing database')
        return
    click.echo(f'admin-user for {name} added to database')

@click.command('calculate-courses')
def calculate_courses_command():
    calculate_courses()
    click.echo('calculating courses')
    


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(fill_user_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(calculate_courses_command)
