# import pytest
from flask import session
import pytest


# should redirect to '/auth/login' when user is not logged in
def test_login_required_logged_out(client, auth):
    with client:
        auth.logout()
        response = client.get("/vote")
        assert session.get('user_id') is None
        assert response.headers["Location"] == "/auth/login"


def test_login_required_in(client, auth):
    with client:
        auth.login()
        assert session['user_id'] == 1
        response = client.get("/vote")
        assert b'Kurs1' in response.data
        assert b'Vote' in response.data
        assert b'Jetzt' in response.data


@pytest.mark.parametrize(('wahl1', 'wahl2', 'wahl3', 'message'), (
    (None, 'Kurs1', 'Kurs2', b'Mindestens ein Kurs nicht'),
    ('Kurs1', 'Kurs1', 'Kurs2', b'Kurs doppelt'),
))
def test_valid_vote(client, auth, wahl1, wahl2, wahl3, message):
    # with client:
    auth.login()
    response = client.post('/vote', data={
        "wahl1": wahl1,
        "wahl2": wahl2,
        "wahl3": wahl3,
    })
    assert message in response.data


# def test_commit_valid_vote(client, auth, app):
#     auth.login()
#     response = client.post("/vote", data={
#         "wahl1": "Kurs1",
#         "wahl2": "Kurs2",
#         "wahl2": "Kurs2",
#         }
#     )
#     # shoud be saved to db:
#     with app.app
#     assert
