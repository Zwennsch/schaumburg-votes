from flask import current_app, Flask, g
import csv
import os

class Course:
    def __init__(self, name, max_participants, teacher, description, img_path) -> None:
        self.name = name
        self.max_participants = max_participants
        self.teacher = teacher
        self.description = description
        self.img_path = img_path
    

def get_courses(app: Flask):
    if 'courses' not in g:    
        courses = []
        with open(os.path.join(app.instance_path, 'courses.csv'), mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                courses.append(Course(row['name'], row['max_participants'], row['teacher'], row['description'], row['img_name']))
        g.courses = courses
       
    return g.courses

