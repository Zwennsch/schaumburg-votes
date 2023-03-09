# Python webapp with Flask collecting votes in a school - Schaumburg-Votes

## A fully functional webapp written in Python using the Flask framework to collect and evaluate votes from students.

Students from Schaumburger Str. Bremen should be able to vote from a choice of courses their favorite three some courses. 

## User instructions:
- initialize the database first from command-line in root folder using:
    flask --app voting init-db

- fill table 'user' inside voting.sql db in instance folder:
    1. store a file students.csv in instance folder
    this will only be for temporarily use, you can delete this file after the data is stored in the database voting.sql in the instance folder
    the file contains 4 columns:
        Klasse, Nachname, Vorname, LogIn
    2. from command-line in root folder use:
        flask --app voting fill-user-db

- this leads to two things:
    1. It will create a new file in instance folder called 'student_pwd.csv' which contains the original students.csv info and an additional column containing a 5 letter password for each user. 
    These passwords should be passed individually to each student for login.
    You can delete this file afterwards.
    2. the user table in voting.sqlite gets filled with users and hashed passwords

- create a courses.csv in the instance folder.
    It should contain 5 columns:
        name, max_participants, teacher, description, img_name
    for each course you can place an image in the static folder. 
    If you don't provide one, a default image will be shown later


    

