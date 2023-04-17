from voting.models import Course, load_courses
import os
import tempfile
def test_course_to_string():
    course = Course('Kurs1', 20, 'Lehrer1', 'Beschreibung1', 'img1')

    name = str(course)

    assert name == 'Course name: Kurs1'

def test_load_courses(app):
    # should return list of courses:
    with app.app_context():
        courses = load_courses(app=app)

        assert len(courses) == 4
        assert courses[0].name == 'Kurs1'

def test_load_courses_empty_static_folder(app):
    with app.app_context():
        app.static_folder = None
        courses = load_courses(app)

        assert len(courses) == 4

def test_load_course_with_image(app):
    with app.app_context():
        app.static_folder = os.path.dirname('../tests/static_folder/')
        courses = load_courses(app)

        assert len(courses) == 4

        assert courses[2].img_name == 'kurs3.img'
        assert courses[0].img_name == app.config['DEFAULT_IMAGE']