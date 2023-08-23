import pytest
from flask import g, session
from voting.db import get_db


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

# should redirect to '/' and flash message 'Permission denied'
def test_admin_unauthorized(client, auth):
    # FIXME: should return 403 error but than I will not be redirected properly by flask redirect
    # doesn't redirect to '/' in test but does when actual app is running. Maybe because of test client?
    with client:
        auth.logout()
        response = client.get('/admin')
        assert b'Redirect' in response.data

    # should redirect when logged in as normal user:
    auth.login()
    response = client.get('/admin')
    assert b'Redirect' in response.data

# should allow access to /admin page when logged in as admin user
def test_admin_authorized_login(client, auth):
    with client:
        auth.admin_login()
        response = client.get('/admin')
        assert b'ADMIN' in response.data


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
