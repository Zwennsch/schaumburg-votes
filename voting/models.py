from flask import Flask, current_app
import csv
import os


class Course:
    def __init__(self, classes, name, max_participants, teacher, description, img_name) -> None:
        self.classes = classes
        self.name = name
        self.max_participants = max_participants
        self.teacher = teacher
        self.description = description
        self.img_name = img_name

    def __str__(self) -> str:
        return "{}".format(self.name)
    
   


def load_courses(app: Flask):
    courses = []
    # TODO: should return an error if there is no courses.csv file
    with open((current_app.config['COURSES']), mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        img_name = ''
        for row in csv_reader:
            classes = tuple(map(int, row['classes'].split(',')))
            img_name = app.config['DEFAULT_IMAGE']
            # check if there is a file in the static folder:
            if app.static_folder:
                if os.path.exists(os.path.join(app.static_folder, row['img_name'])):
                    img_name = row['img_name']
                    
            courses.append(Course(classes,
                row['name'], row['max_participants'], row['teacher'], row['description'], img_name))
    return courses
