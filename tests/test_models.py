from voting.models import Course, get_courses_list, init_courses
import os


def test_course_to_string():
    course = Course("7,8", 'Kurs1', 20, 'Lehrer1', 'Beschreibung1', 'img1')

    name = str(course)

    assert name == 'Kurs1'


def test_init_courses(app):
    # should return list of courses:
    with app.app_context():
        # init_courses(app=app)
        courses = get_courses_list()

        assert len(courses) == 7
        assert courses[0].name == 'Kurs1'


def test_init_courses_empty_static_folder(app):
    with app.app_context():
        app.static_folder = None

        courses = get_courses_list()

        assert len(courses) == 7


# def test_load_course_with_image(app):
#     with app.app_context():
#         app.static_folder = os.path.dirname('../tests/static_folder/')
#         # needs to be done to load the images
#         init_courses(app)
#         courses = get_courses_list()

#         assert len(courses) == 7
#         assert courses[2].img_name == 'kurs3.img'
#         assert courses[0].img_name == app.config['DEFAULT_IMAGE']
