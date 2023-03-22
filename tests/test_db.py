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
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True
    
    assert Recorder.called is False
    monkeypatch.setattr('voting.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

# TODO: this test isn't working so far: Result RuntimeError but I don't know why..
# def test_fill_user_db_command(runner, monkeypatch):
#     class Recorder(object):
#         called = False

#     def fake_fill_user_db():
#         Recorder.called = True

#     assert Recorder.called is False
#     monkeypatch.setattr('voting.helpers.fill_user_db', fake_fill_user_db)
#     result = runner.invoke(args=['fill-user-db'])
#     print('result of runner.invoke: ', result)
#     # assert 'user-db' in result.output
#     assert Recorder.called
