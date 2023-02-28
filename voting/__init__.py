import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # TODO: I might have to change this....
    
    # sets default configuration that the app will use
    app.config.from_mapping(
        # the secret key should be overridden with a random value when deploying 
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'voting.sqlite'),
        DEFAULT_IMAGE='New-Class-Alert.jpg'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing. Override default configuration with values taken from config.py in instance folder
        # this can for example be used to set the real SECRET_KEY
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config, if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists:
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    # TODO: it still feels right, to load courses upfront and have them available through the g object
    # from . import models
    # models.load_courses(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import views
    app.register_blueprint(views.bp)

    return app

