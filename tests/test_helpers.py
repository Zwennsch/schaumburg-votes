import voting.helpers as m
from voting.db import get_db
import os
import tempfile
import csv
from werkzeug.security import check_password_hash

students = os.path.join('./tests/', 'students_data.csv')
courses = os.path.join('./tests/', 'courses_data.csv')

def test_generate_password(app):
    # should generate a random password of length 5
    pw = m._generate_password(5)
    assert len(pw) == 5
    assert type(pw) is str

    pw2 = m._generate_password(5)

    assert pw2 != pw

def test_create_password_list():
    # should create a list of 5 random words
    words = m._create_password_list(3, 5)
    assert len(words) == 5
    assert words[0] != words[1]

def test_get_num_students():
    # should return 2 for 2 students:
    assert m._get_num_students(students) == 2

def test_add_column_in_csv():
    input = students
    # output = './tests/output.csv'
    output_fd, output_path = tempfile.mkstemp()

    m._add_column_in_csv(input,output_path,'new_column',['test1', 'test2'])

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
        m.fill_user_db(students, output_path, db)
        pw = ''

        # there should be a password for each user in the output_file:
        with open(output_fd, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for idx, row in enumerate(csv_reader):
                if idx == 0:
                    pw = row['password']
                    assert len(pw) == 5
        
        # both students should have a random password
        pw_hash = db.execute("SELECT password_hash FROM user WHERE id = 1").fetchone()[0]
        assert len(pw_hash) > 5

    os.unlink(output_path)
    