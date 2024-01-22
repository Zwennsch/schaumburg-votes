import os

from flask import Flask
from flask_session import Session


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'voting.sqlite'),
        COURSES=os.path.join(app.instance_path, 'courses.csv'),
        STUDENTS=os.path.join(app.instance_path, 'students.csv'),
        STUDENTS_PWD=os.path.join(app.instance_path, 'students_pwd.csv'),
        DEFAULT_IMAGE='New-Class-Alert.jpg',
        SESSION_TYPE='filesystem',
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

    # using server-side session for storing temporary courses
    session = Session()
    session.init_app(app)

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


    return app
