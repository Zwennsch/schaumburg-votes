from flask import current_app
import csv
import os

_courses_list = []


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


def init_courses():
    global _courses_list
    courses = []
    # print("course_images_source_folder:", current_app.config['COURSE_IMAGES_SRC_FOLDER'])
    with open((current_app.config['COURSES']), mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        # img_name = ''
        try:
            for row in csv_reader:
                classes = tuple(map(int, row['classes'].split(',')))
                img_name = current_app.config['DEFAULT_IMAGE_NAME']
                # check if there is a file in the instance folder:
                if os.path.exists(os.path.join(current_app.config['COURSE_IMAGES_SRC_FOLDER'], row['img_name'])):
                    img_name = row['img_name']
                courses.append(Course(classes,
                                      row['name'], row['max_participants'], row['teacher'], row['description'], img_name))
        except KeyError as ex:
            print('Warning: Could not read courses.csv file properly because of KeyError. Please check format of file!')
    _courses_list = courses


def get_courses_list() -> list[Course]:
    return _courses_list
