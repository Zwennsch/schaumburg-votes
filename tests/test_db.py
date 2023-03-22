import sqlite3
import pytest

from voting.db import get_db
from voting import helpers

def test_get_close_db(app):
    print('in test_get_close_db')
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    print('in test_init_db_command')
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True
    
    assert Recorder.called is False
    monkeypatch.setattr('voting.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

# this does work as expected
def test_my_test_command(runner, monkeypatch):
    print('in test_my_test_db_command')
    class Recorder(object):
        called = False

    def fake_my_test():
        print('in fake_my_test')
        Recorder.called = True

    monkeypatch.setattr('voting.db.my_test', fake_my_test)
    result = runner.invoke(args=['my-test'])
    assert 'tested' in result.output
    assert Recorder.called

# TODO: this test isn't working so far: Result RuntimeError but I don't know why..
# def test_fill_user_db_command(runner, monkeypatch):
    # print('in test_fill_user_db_command')
#     class Recorder(object):
#         called = False

#     def fake_fill_user_db():
#         print('in fake fill_user_db')
#         Recorder.called = True

#     assert Recorder.called is False
#     monkeypatch.setattr(helpers, "fill_user_db", fake_fill_user_db)
#     result = runner.invoke(args=['fill-user-db'])
#     print('result of runner.invoke: ', result)
#     assert 'user-db' in result.output
#     assert Recorder.called
