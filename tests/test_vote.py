# import pytest
from flask import session


# should redirect to '/auth/login' when user is not logged in
def test_login_required_logged_out(client, auth):
    with client:
        auth.logout()
        response = client.get("/vote")
        assert session.get('user_id') is None
        # print('response from /vote when logged out: ', response.headers)
        assert response.headers["Location"] == "/auth/login"

# def test_login_required_in(client, auth):
#     # FIXME: needs to be fixed: Does not make get request to '/vote' if user is logged in
#      with client:
#         auth.login()
#         assert session['user_id'] == 1py
#         response = client.get("/vote")
#         print('headers response from /vote: ', response.headers)
#         assert response.headers["Location"] == "/vote"