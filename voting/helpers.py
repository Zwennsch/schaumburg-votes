import secrets
import string
import csv
import sqlite3
from werkzeug.security import generate_password_hash
from typing import List
from flask import g, session
from random import shuffle
from voting.cache import get_cache


def _generate_password(length: int) -> str:
    """Generates and returns a password of a given length.
    The password contains ascii_letters and digits

    :param length: The length of the password
    """
    alphabet = string.ascii_letters + string.digits

    return ''.join(secrets.choice(alphabet) for i in range(length))


def fill_user_db(user_input_csv_file, user_output_psw_csv,  db: sqlite3.Connection):
    """Fills up the user-db and uses a student.csv file in the instance folder to do so.
    Provides each user with a predefined 5 character password. 
    The passwords gets stored in a user_output_psw_csv file in the instance folder
    """
    num_students = _get_num_students(user_input_csv_file)
    password_list = _create_password_list(5, num_students)
    _add_column_in_csv(user_input_csv_file,
                       user_output_psw_csv, 'password', password_list)
    with open(user_output_psw_csv, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        print('filling up db..')
        print('please wait')
        for row in csv_reader:
            #  TODO: the generated hash takes a long time to either create or input and looks not right
            # print('pw in actual method: ', row['password'])
            password_hash = generate_password_hash(row['password'])
            db.execute(
                "INSERT INTO user (first_name, last_name, username, password_hash, class)"
                " VALUES (?,?,?,?,?)",
                (row['Vorname'], row['Nachname'],
                 row['LogIn'], password_hash, row['Klasse'])
            )
        db.commit()
        print('db ready!')


def add_new_admin_into_admin_db(name, password, db: sqlite3.Connection):
    password_hash = generate_password_hash(password)
    db.execute(
        "INSERT INTO admin (username, password_hash) VALUES (?,?)",
        (name, password_hash)
    )
    db.commit()


def _add_column_in_csv(csv_input_file_path, csv_output_file_path, column_name: str, values):
    """Adds a new column to the csv entry and fills it with the specified values
        :param csv_input_file_path: The file to add the new column, path included
        :param csv_out_file_path: The file to add the new column, path included
        :param column_name: The name of the new column to be added
        :param values: A list of strings with the values for each row of the column \n
    """
    with open(csv_input_file_path, 'r') as csv_input, open(csv_output_file_path, 'w') as csv_output:
        writer = csv.writer(csv_output, lineterminator='\n')
        reader = csv.reader(csv_input)

        counter = 0
        all = []
        row = next(reader)
        row.append(column_name)
        all.append(row)

        for row in reader:
            row.append(values[counter])
            all.append(row)
            counter += 1
        writer.writerows(all)


def _get_num_students(csv_file) -> int:
    with open(csv_file, 'r') as input:
        reader = csv.reader(input)
        return sum(1 for row in reader) - 1


def add_user_to_database(first_name, last_name, username, password, class_name,  db: sqlite3.Connection) -> bool:
    """Adds a new user into the database. Be sure to check that the username is not taken already
    Check in advance, that the username is not taken already. 
    Throws an sqlite3.IntegrityError if the username isn't UNIQUE
    :param: first_name: The new users first name
    :param: last_name: The new users last name
    :param: username: The new users username. Must be a unique one, otherwise the Insert will fail
    :param: password: The password for the username. Be sure to check for safety in advance
    :param: class_name: The new users class
    :param: db: The database the user should be added to \n
    Returns True, if the user is successfully added, False otherwise.
    """
    pw_hash = generate_password_hash(password)
    try:
        db.execute(
            "INSERT INTO user (first_name, last_name, username, password_hash, class)"
            " VALUES (?,?,?,?,?)",
            (first_name, last_name,
             username, pw_hash, class_name)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError as e:
        return False


def _create_password_list(pwd_length: int, num_of_pwd: int) -> List[str]:
    pwd_list = []
    for i in range(num_of_pwd):
        pwd_list.append(_generate_password(pwd_length))
    return pwd_list


def is_username_taken(username, db: sqlite3.Connection):
    # Prepare the SQL query with the username as a parameter
    query = """
    SELECT COUNT(*) FROM user WHERE username = :username
    UNION ALL
    SELECT COUNT(*) FROM admin WHERE username = :username;
    """

    # Execute the query with the username parameter and fetch results
    results = db.execute(query, {'username': username}).fetchall()

    # Check if any of the results is greater than 0, indicating that the username is taken
    return any(count > 0 for count, in results)


def get_query_for_nth_vote(nth_vote) -> str:
    nth_query = "SELECT first_name, last_name, class, first_vote, second_vote, third_vote " \
        "FROM user "\
        "INNER JOIN vote ON user.id = vote.user_id " \
        "WHERE vote."+nth_vote+" = ? ORDER BY class, last_name"
    return nth_query

def get_all_grades() -> set[int]:
    '''Returns a set of grades from all courses that can be voted
    '''
    grades = set()
    for course in g.courses:
        for c in course.classes:
            grades.add(c)

    return grades

# TODO: test needed
def calculate_courses(db: sqlite3.Connection) -> dict:
    '''Calcutes the final courses based on the votes of all students and the maximum 
    capacity of each course. 
    Returns a dict with course name as key and a list of student dictionaries as value.
    '''
    # Easy solution:
    grades = get_all_grades()
    # create a dict so students for each class (i.e. 8a- 8d is ONE class 8) get stored where key is class
    students_per_grade = {} 
    for grade in grades:
        students_per_grade[grade] = []
    
    # fill the dict:
    # get all n-th-graders, where n is element of grades-list. Randomly order the students
    for nth_grade in students_per_grade:
        grade = str(nth_grade) + "%"
        students = db.execute("SELECT * from user WHERE class like ? AND vote_passed = 1", (grade,)).fetchall()
        # reorder students randomly
        shuffle(students)
        students_per_grade[nth_grade] = students

    # dict that stores the students-Row-objects for each course, e.g. final_course['Sport-JG8'] = [student1, student2,...]
    final_courses = {}
    # dict that stores the actual nums of students inside a specific course
    available_spots_per_course = {}
    for course in g.courses:
        final_courses[course.name] =[]
        available_spots_per_course[course.name] = int(course.max_participants)

    # create an additional list 'unfulfilled_wish' if even third wish not fulfilled for student
    final_courses['unfulfilled_wish'] = []
    # loop through every student of each list for each class:
    for grade in grades:
        if len(students_per_grade[grade]) != 0:
            for student in students_per_grade[grade]:
                vote = db.execute("SELECT * from vote WHERE user_id = ?", (student['id'],)).fetchone()
                # check if course for first_vote is available, 
                # if so add to list, update dict
                if available_spots_per_course[vote['first_vote']] > 0:
                    final_courses[vote['first_vote']].append(student)
                    available_spots_per_course[vote['first_vote']] -= 1
                # if not, check second- and third-vote. If even third vote not available add to unfulfilled wish course
                elif available_spots_per_course[vote['second_vote']] >0:
                    final_courses[vote['second_vote']].append(student)
                    available_spots_per_course[vote['second_vote']] -= 1
                elif available_spots_per_course[vote['third_vote']] > 0:
                    final_courses[vote['third_vote']].append(student)
                    available_spots_per_course[vote['third_vote']] -= 1
                else:
                    final_courses['unfulfilled_wish'].append(student)
    # create a dictionary that stores 
    serialized_data = {course: [row_to_dict(student) for student in students] for course, students, in final_courses.items()}
    get_cache().set('course_proposals', serialized_data)
    session['courses_calculated'] = True
    return final_courses


def row_to_dict(row):
    return dict(zip(row.keys(), row))