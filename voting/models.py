from flask import current_app, Flask, g
import csv
import os

class Course:
    def __init__(self, name, max_participants, teacher, description, img_name) -> None:
        self.name = name
        self.max_participants = max_participants
        self.teacher = teacher
        self.description = description
        self.img_name = img_name
    

def get_courses(app: Flask):
    if 'courses' not in g:    
        courses = []
        with open(os.path.join(app.instance_path, 'courses.csv'), mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            img_name = ''
            for row in csv_reader:
                # check if there is a file in the static folder:
                if app.static_folder:
                    if os.path.exists(os.path.join(app.static_folder, row['img_name'])):
                        img_name = row['img_name']
                    else:
                        img_name = current_app.config['DEFAULT_IMAGE']
                courses.append(Course(row['name'], row['max_participants'], row['teacher'], row['description'], img_name))
        g.courses = courses
       
    return g.courses

