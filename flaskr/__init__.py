import os
from flask import Flask

def create_app(test_cofig=None):
    """
   Application factory function for creating and configuring the Flask app.

   This function sets up the configuration, database, and routes for the application.
   It can also be used to configure the app for testing by passing a test configuration.

   :param test_config: Optional dictionary for providing a test configuration. If provided,
                       the app will be configured using this instead of the instance configuration.
   :return: The configured Flask application instance.
   """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    if test_cofig is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/userlogin')
    def userLogIn():
        return 'Welcome!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app



