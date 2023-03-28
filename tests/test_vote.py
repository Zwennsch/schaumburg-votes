import pytest
from flask import session, g
# from voting.models import get_courses


# should redirect to '/auth/login' when user is not logged in
def test_login_required(client, auth, courses, monkeypatch):
    # TODO: needs to be fixed: Does not make get request to '/vote' if user is logged in
    # this might be because of no courses being loaded inside th g- object

    # with client:
    #     auth.login()
    #     assert session['user_id'] == 1
    #     course_list = courses.get_courses()
    #     g.courses = courses.get_courses()
    #     response = client.get("/vote")
    #     print('headers response from /vote: ', response.headers)
    #     assert response.headers["Location"] == "/vote"

    with client:
        auth.logout()
        response = client.get("/vote")
        assert session.get('user_id') is None
        print('response from /vote when logged out: ', response.headers)
        assert response.headers["Location"] == "/auth/login"



    
