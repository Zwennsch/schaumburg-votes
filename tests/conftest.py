import os
import tempfile

import pytest
from voting import create_app
from voting.db import get_db, init_db
from voting.models import Course

with open(os.path.join(os.path.dirname(__file__),'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

class AuthActions(object):
    def __init__(self, client) -> None:
        self._client = client

    def login(self, username='test_username', password='trsvv'):
        return self._client.post(
            '/auth/login',
            data={'username' : username, 'password' : password}
        )
    
    def logout(self):
        self._client.get('auth/logout')

class CoursesCreator(object):
    def __init__(self, app) -> None:
        self._app = app
    
    def getCourses(self):
        courses = []
        for i in range(4):
            courses.append(Course('test_name'.join(str(i)),i, 'test_teacher'.join(str(i)), 'test_description'.join(str(i)), 'test_image_source'.join(str(i))))
        return courses
    
@pytest.fixture
def courses(app):
    return CoursesCreator(app)

@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING' : True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()



