import voting.helpers as helpers
from voting.db import get_db
from flask import session


def test_calculate_courses(app_predefined_db, client_real_data):
    with app_predefined_db.app_context():
        with client_real_data:
            db = get_db()
            # make basic HTTP-request to get access to session object
            client_real_data.get('/admin/course-results')
            result = helpers.calculate_courses(db)
            # assert that all students are distributed
            total_sum = 0
            for course in result:
                total_sum += len(result[course])
            assert total_sum == 151
            assert type(result) == type(dict())
            # assert that there aren't too many students in a course:
            assert len(result['Sport - JG 8']) <= 20
            assert len(result['Gendern - JG 8']) <= 20
            assert len(result['Schulzeitung - JG 8']) <= 16


def test_calculate_cs_view(auth, client, monkeypatch):
    class Recorder(object):
        called = False

    def fake_calculate_courses(*args):
        Recorder.called = True

    auth.admin_login()
    assert Recorder.called == False
    monkeypatch.setattr('voting.views.calculate_courses',
                        fake_calculate_courses)
    response = client.get('/admin/course-calculation', follow_redirects=True)
    assert response.status_code == 200
    assert Recorder.called == True
    assert 'Kurse wurden berechnet' in response.get_data(as_text=True)


def test_should_set_session_courses_calculated(app_empty_final_courses_db, client_empty_final_courses, empty_final_courses_auth):
    with app_empty_final_courses_db.app_context():
        with client_empty_final_courses:
            # login as admin
            empty_final_courses_auth.real_admin()
            # make arbitrary HTTP request 
            client_empty_final_courses.get('/admin/course-results')
            # should be false, before calculating course
            assert session['courses_calculated'] == False
            # course calculation
            client_empty_final_courses.get('/admin/course-calculation')
            # should be True, after calculating courses
            assert session['courses_calculated'] == True


def test_should_add_final_courses_into_user_db(app_empty_final_courses_db, client_empty_final_courses, empty_final_courses_auth):
    with app_empty_final_courses_db.app_context():
        # should not be any data before adding
        db = get_db()
        final_course_before = db.execute(
            "SELECT final_course FROM user WHERE id = 1").fetchone()[0]
        assert final_course_before == 'LEER'
        # should be a final course after course_calculation:
        empty_final_courses_auth.real_admin()
        client_empty_final_courses.get('/admin/course-calculation')
        # app_predefined_db.test_client().get('/admin/course-calculation')
        final_course_before = db.execute(
            "SELECT final_course FROM user WHERE id = 1").fetchone()[0]
        assert final_course_before != 'LEER'
