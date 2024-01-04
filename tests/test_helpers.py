import voting.helpers as helpers
from voting.db import get_db
import os
import tempfile
import csv
import pytest
from flask import g
# from werkzeug.security import check_password_hash

students = os.path.join('./tests/', 'students_data.csv')
courses = os.path.join('./tests/', 'courses_data.csv')
test_data_add_user = [("user1", True),
                      ("test_username", False),
                      ("other_username", False)
                      ]


@pytest.mark.parametrize(('username', 'expected_result'), test_data_add_user)
def test_add_user_to_database(app, username, expected_result):
    with app.app_context():
        db = get_db()
        result = helpers.add_user_to_database(
            'Hans', 'Meier', username, 'Password123', '9a', db)
        assert result == expected_result


def test_generate_password(app):
    # should generate a random password of length 5
    pw = helpers._generate_password(5)
    assert len(pw) == 5
    assert type(pw) is str

    pw2 = helpers._generate_password(5)

    assert pw2 != pw


def test_create_password_list():
    # should create a list of 5 random words
    words = helpers._create_password_list(3, 5)
    assert len(words) == 5
    assert words[0] != words[1]


def test_get_num_students():
    # should return 2 for 2 students:
    assert helpers._get_num_students(students) == 2


def test_add_column_in_csv():
    input = students
    # output = './tests/output.csv'
    output_fd, output_path = tempfile.mkstemp()

    helpers._add_column_in_csv(
        input, output_path, 'new_column', ['test1', 'test2'])

    with open(output_fd, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for idx, row in enumerate(csv_reader):
            if idx == 0:
                assert row['new_column'] == 'test1'
            if idx == 1:
                assert row['new_column'] == 'test2'

    os.unlink(output_path)


def test_fill_user_db(app):
    output_fd, output_path = tempfile.mkstemp()
    with app.app_context():
        db = get_db()
        helpers.fill_user_db(students, output_path, db)
        pw = ''

        # there should be a password for each user in the output_file:
        with open(output_fd, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for idx, row in enumerate(csv_reader):
                if idx == 0:
                    pw = row['password']
                    assert len(pw) == 5

        # both students should have a random password
        pw_hash = db.execute(
            "SELECT password_hash FROM user WHERE id = 1").fetchone()[0]
        assert len(pw_hash) > 5

    os.unlink(output_path)


def test_add_new_admin_into_admin_db(app):
    with app.app_context():
        db = get_db()
        # add the admin-user into the db
        helpers.add_new_admin_into_admin_db('hans', 'password123', db)

        # check that user is in db:
        admin = db.execute(
            "SELECT * FROM admin WHERE username = 'hans'").fetchone()
        assert admin['username'] == 'hans'


# should not create a new admin when username exists
@pytest.mark.parametrize(('username', 'password', 'message'),
                         (
    ('test_username', 'password', 'username already'),
    ('test_admin', 'password', 'username already'),
))
def test_create_admin_user_username_exists(runner, app, username, password, message):

    with app.app_context():
        db = get_db()
        assert helpers.is_username_taken('test_username', db) == True
        result = runner.invoke(args=['create-admin', username, password])
        assert message in result.output


def test_get_query_for_nth_vote():
    assert helpers.get_query_for_nth_vote('first_vote') == "SELECT first_name, last_name, class, first_vote, second_vote, third_vote " \
        "FROM user "\
        "INNER JOIN vote ON user.id = vote.user_id " \
        "WHERE vote.first_vote = ? ORDER BY class, last_name"


def test_get_all_grades(app, auth, client):

    with app.app_context():
        response = client.get('/course-overview')
        assert response.status_code == 200
        assert helpers.get_all_grades() == {7, 8, 9, 10}


def test_calculate_courses(app_predefined_db, client_real_data):
    with app_predefined_db.app_context():
        with client_real_data:
            client_real_data.get('/course-overview')
            db = get_db()
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


# TODO: cProfile for testing performance issues.
# def test_performance_fill_user_db():
    # input_csv = ""
