import os

from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        # TODO: the secret key should be overridden with a random value when deploying 
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'voting.sqlite'),
        COURSES=os.path.join(app.instance_path, 'courses.csv'),
        STUDENTS=os.path.join(app.instance_path, 'students.csv'),
        STUDENTS_PWD=os.path.join(app.instance_path, 'students_pwd.csv'),
        DEFAULT_IMAGE='New-Class-Alert.jpg'
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

   
    from . import auth
    app.register_blueprint(auth.bp)

    from . import views
    app.register_blueprint(views.bp)

    return app

