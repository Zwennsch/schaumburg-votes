import os
import tempfile

import pytest
from voting import create_app
from voting.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__),'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    print("in app.fixture")
    app = create_app({
        'TESTING' : True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    print("before yielding the app")
    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

