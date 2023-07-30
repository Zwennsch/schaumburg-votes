import sqlite3
import pytest
from voting.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    # print('in test_init_db_command')

    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    assert Recorder.called is False
    monkeypatch.setattr('voting.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called


# should run the create-admin-command with a selected username and password
@pytest.mark.parametrize(('username', 'password', 'message'),
                         (
    ('trsvv', 'cd', '5 characters'),
    ('test_username', 'kfjdshf', 'admin-user for test_username'),
))
def test_create_admin_user_command(runner, monkeypatch, app, username, password, message):
    class Recorder(object):
        called = False
    
    def fake_create_admin_db(*args, **kwargs):
        Recorder.called = True

    with app.app_context():
        assert Recorder.called is False
        monkeypatch.setattr('voting.db.create_admin_db', fake_create_admin_db)
        result = runner.invoke(args=['create-admin', username, password])
        assert message in result.output
        if len(password) >= 5:
            assert Recorder.called

def test_create_admin_user_command_missing_arguments(runner, app):
    with app.app_context():
        result = runner.invoke(args=['create-admin', 'username'])
        assert 'Missing' in result.output
        
    

def test_fill_user_db_command(runner, monkeypatch, app):
    class Recorder(object):
        called = False

    def fake_fill_user_db(*args, **kwargs):
        Recorder.called = True

    with app.app_context():
        assert Recorder.called is False
        monkeypatch.setattr('voting.db.fill_user_db', fake_fill_user_db)
        result = runner.invoke(args=['fill-user-db'])
        assert 'user-db initialized' in result.output
        assert Recorder.called

def test_fill_user_db_no_students_file(runner, monkeypatch, app):
    with app.app_context():
        app.config['STUDENTS'] = ' '
        result = runner.invoke(args=['fill-user-db'])
        assert 'no students.csv' in result.output




