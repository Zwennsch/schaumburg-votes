import os
import tempfile

import pytest
from voting import create_app
from voting.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


class AuthActions(object):
    def __init__(self, client) -> None:
        self._client = client

    def admin_login(self):
        return self._client.post('/auth/login', data={'username': 'test_admin', 'password': '12345'})
    
    def real_admin(self):
        return self._client.post('/auth/login', data={'username': 'admin', 'password': '12345'})

    def login(self, username='test_username', password='trsvv', voted=True):
        if voted:
            return self._client.post(
                '/auth/login',
                data={'username': username, 'password': password}
            )
        else:
            return self._client.post('auth/login',
                                     data={'username': 'other_username', 'password': password})
    def login_9th_grade(self):
        return self.login()
    
    def login_8th_grade(self):
        return self.login(voted=False)
       
    def logout(self):
        self._client.get('auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)

@pytest.fixture
def real_auth(client_real_data):
    return AuthActions(client_real_data)

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    # creates an app with 4 courses : Kurs1... Kurs4 as name, 11 to 14 as participants, Teacher1 to Teacher4 as teachers
    # Beschreibung1 to Beschreibung4 as description, kurs1.img to kurs4.img as img_name
    course_path = os.path.join('./tests/', 'courses_data.csv')
    students_path = os.path.join('./tests/', 'students_data.csv')
    students_pwd_path = os.path.join('./tests/', 'students_pwd_data.csv')

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'COURSES': course_path,
        'STUDENTS': students_path,
        'STUDENTS_PWD': students_pwd_path
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def app_predefined_db():
    db_path = os.path.join('./tests/', 'real_data.sqlite')


    course_path = os.path.join('./tests/', 'real_courses.csv')
    # students_path = os.path.join('./tests/', 'students_data.csv')
    # students_pwd_path = os.path.join('./tests/', 'students_pwd_data.csv')

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'COURSES': course_path,
        # 'STUDENTS': students_path,
        # 'STUDENTS_PWD': students_pwd_path
    })

    # with app.app_context():
    #     # init_db()
        # get_db()
    yield app

    # os.close(db_fd)
    # os.unlink(db_path)




@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def client_real_data(app_predefined_db):
    return app_predefined_db.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
