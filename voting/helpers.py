import secrets
import string
import csv
import sqlite3
from werkzeug.security import generate_password_hash
from typing import List


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
        :param values: A list of strings with the values for each row of the column
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
