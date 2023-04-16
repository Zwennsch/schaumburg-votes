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


def test_fill_user_db_command(runner, monkeypatch, app):
    class Recorder(object):
        called = False

    def fake_fill_user_db(*args, **kwargs):
        print('in fake fill_user_db')
        Recorder.called = True

    with app.app_context():
        assert Recorder.called is False
        monkeypatch.setattr('voting.db.fill_user_db', fake_fill_user_db)
        result = runner.invoke(args=['fill-user-db'])
        # print('result of runner.invoke: ', result.output)
        assert 'user-db initialized' in result.output
        assert Recorder.called
