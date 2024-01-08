from voting.models import Course, init_courses
import os
import tempfile


def test_course_to_string():
    course = Course("7,8", 'Kurs1', 20, 'Lehrer1', 'Beschreibung1', 'img1')

    name = str(course)

    assert name == 'Kurs1'


def test_load_courses(app):
    # should return list of courses:
    with app.app_context():
        courses = init_courses(app=app)

        assert len(courses) == 7
        assert courses[0].name == 'Kurs1'


def test_load_courses_empty_static_folder(app):
    with app.app_context():
        app.static_folder = None
        courses = init_courses(app)

        assert len(courses) == 7


def test_load_course_with_image(app):
    with app.app_context():
        app.static_folder = os.path.dirname('../tests/static_folder/')
        courses = init_courses(app)

        assert len(courses) == 7

        assert courses[2].img_name == 'kurs3.img'
        assert courses[0].img_name == app.config['DEFAULT_IMAGE']
