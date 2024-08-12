import os

from flask import Flask, send_from_directory


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'voting.sqlite'),
        COURSE_IMAGES_FOLDER_NAME='course_images',
        COURSE_IMAGES_SRC_FOLDER=os.path.join(
            app.instance_path, 'course_images'),
        COURSES=os.path.join(app.instance_path, 'courses.csv'),
        STUDENTS=os.path.join(app.instance_path, 'students.csv'),
        STUDENTS_PWD=os.path.join(app.instance_path, 'students_pwd.csv'),
        DEFAULT_IMAGE_NAME='DEFAULT.jpg',
        # COURSES_CALCULATED= False,
        CACHE_TYPE='SimpleCache',
        CACHE_DEFAULT_TIMEOUT=600  # 10 minutes of cache timeout
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import cache
    cache.init_cache(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import views
    app.register_blueprint(views.bp)

    from . import models
    # make sure this gets only loaded after courses.csv is in instance folder
    if os.path.exists(os.path.join(app.instance_path, 'courses.csv')):
        with app.app_context():
            models.init_courses()

    @app.route('/instance/course_images/<filename>')
    def course_image(filename):
        return send_from_directory(
            app.config['COURSE_IMAGES_SRC_FOLDER'],
            filename
        )

    return app
