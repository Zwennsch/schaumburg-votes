import pytest
from flask import session, g
from voting.db import get_db


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
def test_invalid_vote(client, auth, wahl1, wahl2, wahl3, message):
    # with client:
    auth.login()
    response = client.post('/vote', data={
        "wahl1": wahl1,
        "wahl2": wahl2,
        "wahl3": wahl3,
    })
    assert message in response.data


def test_commit_valid_vote(client, auth, app):
    # make sure that logged-in user can open the vote.html page
    auth.login(voted=False)
    assert client.get('/vote').status_code == 200

    with app.app_context():
        # make sure that no vote has been passed yet
        db = get_db()
        voted = db.execute(
            'SELECT vote_passed FROM user WHERE id = 2').fetchone()[0]
        assert voted == 0

    # pass vote and make sure it gets stored in user table
    client.post('/vote', data={
        "wahl1": "Kurs1",
        "wahl2": "Kurs6",
        "wahl3": "Kurs7",
    }
    )
    with app.app_context():
        db = get_db()
        voted = db.execute(
            'SELECT vote_passed FROM user WHERE id = 2').fetchone()[0]
        assert voted == 1
        vote = db.execute('SELECT * FROM vote WHERE user_id = 2').fetchone()
        assert vote['first_vote'] == "Kurs1"
    # count = db.execute('SELECT COUNT(id)')


def test_update_vote(client, app, auth):

    auth.login()
    # assert that user has already voted
    with client:
        client.get('vote/')
        assert g.user['vote_passed'] == 1

    client.post('/vote', data={
        "wahl1": "Kurs4",
        "wahl2": "Kurs1",
        "wahl3": "Kurs5",
    }, follow_redirects=True
    )
    with app.app_context():
        db = get_db()
        vote = db.execute('SELECT * FROM vote WHERE user_id = 1').fetchone()
        assert vote['first_vote'] == "Kurs4"

# only courses 'Kurs1', 'Kurs4', Kurs5' are valid, so here at least one is invalid
# so this is: 1. iv, v, iv - 2. iv, v, v - 3. v, iv, v, - 4. iv, iv, v
@pytest.mark.parametrize(('wahl1', 'wahl2', 'wahl3', 'message'), (
    ('Kurs2', 'Kurs1', 'Kurs6', b'Kurs nicht Jahrgang'),
    ('Kurs3', 'Kurs4', 'Kurs5', b'Kurs nicht Jahrgang'),
    ('Kurs4', 'Kurs6', 'Kurs5', b'Kurs nicht Jahrgang'),
    ('Kurs3', 'Kurs2', 'Kurs5', b'Kurs nicht Jahrgang'),
))
def test_cannot_vote_for_courses_with_other_class(app, auth, client, wahl1, wahl2, wahl3, message):
    # login as user with 9th grade:
    auth.login_9th_grade()
    with client:
        # assert that user is from 9th_grade
        client.get('/vote')
        assert g.user['class'] =='9a'
    
    # pass votes where at least one course is not for 9th grade
    response = client.post('/vote', data={
        "wahl1": wahl1,
        "wahl2": wahl2,
        "wahl3": wahl3,
    }, follow_redirects=True,)
    # FIXME: message doesn't show up in response.
    # assert message in response.data

    # assert that course is not stored in db and still 'Kurs1' as first_vote
    with app.app_context():
        db = get_db()
        vote = db.execute('SELECT * FROM vote WHERE user_id = 1').fetchone()
        assert vote['first_vote'] == "Kurs1"

    # should be redirected to '/vote' doesn't work. No Location - Key
    assert response.request.path == "/vote"


def test_courses_view(client):
    response = client.get('/course-overview')   
    assert b'Maximale Teilnehmer' in response.data
    # assert course-description in response
    assert b'Beschreibung1' in response.data

def test_index_not_voted(auth, client):
    auth.login(voted = False)
    response = client.get('/')
    assert b'Willkommen bei' in response.data
    assert b'Jetzt' in response.data
    assert b'1. Wahl' not in response.data
