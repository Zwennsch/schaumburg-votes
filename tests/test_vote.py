import pytest
from flask import session
from voting.models import get_courses


# should redirect to '/auth/login' when user is not logged in
def test_login_required(client, auth, courses):
    # TODO: needs courses to be loaded!
    with client:
        auth.login()
        assert session['user_id'] == 1
        course_list = courses.get_courses
        response = client.get("/vote")
        print('headers response from /vote: ', response.headers)
        # assert response.headers["Location"] == "/vote"

    with client:
        auth.logout()
        response = client.get("/vote")
        assert session.get('user_id') is None
        print('response from /vote when logged out: ', response.headers)
        assert response.headers["Location"] == "/auth/login"



    
