from datetime import datetime, timedelta, timezone
from flask import g, session

# should redirect to '/' and flash message 'Permission denied'
def test_admin_unauthorized(client, auth):
    with client:
        auth.logout()
        response = client.get('/admin', follow_redirects=True)
        assert b'Permission denied' in response.data

    # should redirect to '/' when logged in as normal user:
    auth.login()
    response = client.get('/admin', follow_redirects=True)
    assert response.request.path == '/'

# should allow access to /admin page when logged in as admin user
def test_admin_authorized_login(client, auth):
    with client:
        auth.admin_login()
        response = client.get('/admin')
        assert b'ADMIN' in response.data


def test_add_student_view(auth, client):
    auth.admin_login()
    response = client.get('/admin/add-student')
    assert 'Bitte Schüler hinzufügen' in response.get_data(as_text=True)



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

