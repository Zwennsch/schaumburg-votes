import pytest
from flask import g, session
from voting.db import get_db
from voting.models import get_courses_list


def test_login(client, auth):
    assert client.get('auth/login').status_code == 200
    #  user is logged out
    with client:
        client.get("/")
        assert session.get('user_id') is None

    # user logs in correctly
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test_username'

def test_should_load_courses_before_first_request(app):
    # should not be any courses before first request:
    with app.app_context():
        courses = get_courses_list()
        assert len(courses) == 7





@pytest.mark.parametrize(('username', 'password', 'message'),
                         (
    ('', 'trsvv', b'Bitte Benutzernamen eingeben'),
    ('test_username', '', b'Bitte Passwort eingeben'),
    ('test_username', 'kfjdshf', b'Falsches Passwort'),
    ('test', 'trsvv', b'Falscher Benutzername'),
))
def test_login_valid_input(client, username, password, message):
    response = client.post('auth/login',
                           data={'username': username, 'password': password})
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
