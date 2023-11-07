from datetime import datetime, timedelta, timezone
from flask import g, session
from voting.db import get_db
import pytest


# should redirect to '/' and flash message 'Permission denied'
def test_admin_unauthorized(client, auth):
    # Should get 'Permission denied when not logged in as any user'
    auth.logout()
    response = client.get('/admin', follow_redirects=True)
    assert b'Permission denied' in response.data

    # should redirect to '/' when logged in as normal user:
    auth.login()
    response = client.get('/admin', follow_redirects=True)
    assert b'Permission denied' in response.data
    assert response.request.path == '/'

# should allow access to /admin page when logged in as admin user


def test_admin_authorized_login(client, auth):
    auth.admin_login()
    response = client.get('/admin')
    assert b'ADMIN' in response.data


# remember that only classes '9a' and '8c' are valid
test_admin_add_user = [('Hans', 'Mueller', 'user123', 'password123', 'password123', '9a', 'Neuer Schüler'),
                       ('Hans', 'Mueller', 'user123', 'password123',
                        'password123', None, 'Mindestens ein Eintrag'),
                       ('Hans', 'Mueller', 'user123', 'password123',
                        'password', '9a', 'Fehler bei der Wiederholung'),
                       ('Hans', 'Mueller', 'user123', 'pass',
                        'pass', '9a', 'mindestens 5 Zeichen'),
                       ('Hans', 'Mueller', 'test_username', 'password123',
                        'password123', '9a', 'Benutzername bereits vergeben'),
                       ('Hans', 'Mueller', 'user123', 'password123',
                        'password123', '6', 'Klasse ungültig'),
                       ]


@pytest.mark.parametrize(('first_name', 'last_name', 'username', 'password', 'password_check', 'class_name', 'message'), test_admin_add_user)
def test_add_student_view_post(auth, client, first_name, last_name,
                               username, password, password_check, class_name, message):
    auth.admin_login()
    response = client.post('/admin/add-student', data={'first_name': first_name,
                                                       'last_name': last_name,
                                                       'username': username,
                                                       'password': password,
                                                       'password_check': password_check,
                                                       'class': class_name}, follow_redirects=True)
    assert message in response.get_data(as_text=True)


# TODO: whitespaces in username, password ...
# @pytest.mark.parametrize()
def test_remove_whitespaces_when_adding_student(client, app, auth):
    # login as admin
    auth.admin_login()
    assert client.get('/admin').status_code == 200
    # add new student with whitespace:
    client.post('/admin/add-student', data={'first_name': 'Hans ',
                                            'last_name': 'Mueller',
                                            'username': 'user123',
                                            'password': 'password123',
                                            'password_check': 'password123',
                                            'class': '9a'})
    with app.app_context():
        db = get_db()
        name = db.execute(
            "SELECT first_name FROM user WHERE username = 'user123'",).fetchone()['first_name']
        assert name == 'Hans'
        assert not name == 'Hans '


def test_add_student_view_get(auth, client):
    auth.admin_login()
    response = client.get('/admin/add-student')
    assert 'Bitte Schüler hinzufügen' in response.get_data(as_text=True)


def test_delete_student_successfully(client, auth):
    # login as admin
    auth.admin_login()
    response = client.get('/admin/delete-student')
    # verify view for 'GET'
    assert response.status_code == 200
    assert 'Bitte Klasse wählen' in response.get_data(as_text=True)
    assert '9a' in response.get_data(as_text=True)

    # verify 'POST
    response = client.post('/admin/delete-student',
                           data={'class': "('9a',)"}, follow_redirects=True)
    assert response.status_code == 200
    assert 'test_first_name' in response.get_data(as_text=True)


delete_students_from_list_data = [
    ([1], 1, 'Schüler wurde'), ([1, 2], 0, 'Schüler wurden')]


@pytest.mark.parametrize(('ids_list', 'no_user_remaining', 'message'), delete_students_from_list_data)
def test_delete_student_from_list(client, auth, app, ids_list, no_user_remaining, message):
    with app.app_context():
        db = get_db()
        # make sure that user with id = 1 exists
        assert db.execute("SELECT first_name FROM user WHERE id = '1'",).fetchone()[
            'first_name'] == 'test_first_name'
        # there should be 2 users in db before deletion
        assert db.execute("SELECT COUNT(*) FROM user",).fetchone()[0] == 2
        # login as admin
        auth.admin_login()
        # delete student with id = 1
        response = client.post('/admin/delete-student/all-students',
                               data={'selected_students': ids_list}, follow_redirects=True)
        # number of users in db should be less
        assert no_user_remaining == db.execute(
            "SELECT COUNT(*) FROM user").fetchone()[0]
        assert message in response.get_data(as_text=True)


def test_admin_course_results(client, auth):
    auth.admin_login()
    # GET should render view to select course
    response = client.get('/admin/course-results', follow_redirects=True)
    assert response.status_code == 200
    assert 'Kurs1' in response.get_data(as_text=True)

    # POST
    response = client.post('/admin/course-results',
                           data={'selected_course': 'Kurs1'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Erstwahlen für Kurs1' in response.get_data(as_text=True)
    assert 'test_first_name' in response.get_data(as_text=True)


def test_admin_class_results(client, auth):
    auth.admin_login()
    # GET should render view of class to select:
    response = client.get('/admin/class-results', follow_redirects=True)
    assert response.status_code == 200
    assert 'Klasse wählen' in response.get_data(as_text=True)

    # POST
    response = client.post('/admin/class-results', data={'selected_class' : '9a'}, follow_redirects=True)
    assert 'test_first_name' in response.get_data(as_text=True)
    # Show only those who voted:
    response = client.post('/admin/class-results', data={'selected_class' : '8c'}, follow_redirects=True)
    assert 'other_first_name' not in response.get_data(as_text=True)


# FIXME: This isn't working:
# def test_track_admin_activity(client):
#     with client:
#         with client.session_transaction() as sess:
#             sess['admin'] = True  # Set session data for admin user

#         # Simulate a request to trigger the before_request function
#         response = client.get('/auth/admin')  # Replace with actual route

#         assert response.status_code == 200  # Replace with expected status code

#         # Assert that session data was updated correctly
#         assert 'last_activity' in client.session
#         assert isinstance(client.session['last_activity'], datetime)

#         # Assert that g.admin was updated correctly
#         assert hasattr(g, 'admin')
#         assert g.admin is True  # Assuming the user is an admin

#         # Simulate passing time by using UTC-aware datetime
#         now = datetime.now(timezone.utc)
#         elapsed_time = now - client.session['last_activity']

#         # Assert that the elapsed time was calculated correctly
#         assert elapsed_time >= timedelta(minutes=15)  # Replace with expected timeout

#         # Simulate another request after elapsed time
#         response = client.get('/auth/admin')  # Replace with actual route

#         # Assert that session data was cleared due to timeout
#         assert 'last_activity' not in client.session
#         assert not hasattr(g, 'admin')
