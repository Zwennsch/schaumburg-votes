import secrets
import string
import csv
import sqlite3
from werkzeug.security import generate_password_hash
# from flask import current_app


def _generate_password(length: int) -> str:
    """Generates and returns a password of a given length.
    The password contains ascii_letters and digits

    :param length: The length of the password
    """
    alphabet = string.ascii_letters + string.digits
    

    return ''.join(secrets.choice(alphabet) for i in range(length))


def fill_user_db(csv_file, db: sqlite3.Connection):
    num_students = _get_num_students(csv_file)
    password_list = _create_password_list(5, num_students)
    _add_column_in_csv(csv_file, 'password', password_list)
    with open('instance/student_pwd.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                #  TODO: the generated hash takes a long time to either create or input and looks not right
                 password_hash = generate_password_hash(row['password'])
                 print(password_hash)
                 db.execute(
                      "INSERT INTO user (first_name, last_name, username, password_hash, class)"
                    " VALUES (?,?,?,?,?)", 
                    (row['Vorname'],row['Nachname'], row['LogIn'], password_hash, row['Klasse'])
                )
            db.commit()
                 
    

def _add_column_in_csv(csv_file_path, column_name: str, values):
    """Adds a new column to the csv entry and fills it with the specified values
        :param csv_file_path: The file to add the new column, path included
        :param column_name: The name of the new column to be added
        :param values: A list of strings with the values for each row of the column
    """ 
    with open(csv_file_path, 'r') as csvinput, open('instance/student_pwd.csv', 'w') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)

        counter = 0
        all = []
        row = next(reader)
        row.append(column_name)
        all.append(row)

        for row in reader:
             row.append(values[counter])
             all.append(row)
             counter +=1
        writer.writerows(all)


def _get_num_students(csv_file) -> int:
    # TODO: should return exception if no such file exists
    with open(csv_file, 'r') as input:
        reader = csv.reader(input)
        return sum(1 for row in reader) -1        



def _create_password_list(pwd_length: int, num_of_pwd: int) -> list[str]:
    pwd_list = []
    for i in range(num_of_pwd):
        pwd_list.append(_generate_password(pwd_length))
    return pwd_list
