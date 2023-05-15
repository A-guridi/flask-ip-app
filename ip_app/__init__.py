import os
from flask import Flask
from ip_app import model
from ip_app import ip_services


def create_app(test_config=None):
    """
    Constructor to create a Flask app. It only takes as an input a configuration mapping,
    or it can read it by default from the configuration file stored locally.
    Args:
        test_config (dict): The configuration parameters for the app (see config file for more details)

    Returns:
        A flask app with a database and 3 API endpoints defined in the blueprint
    """
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        from ip_app.config import ProductionConfig
        # load the instance config, if it exists, when not testing
        app.config.from_object(ProductionConfig)
        app.config['DATABASE'] = os.path.join(app.instance_path, app.config['DATABASE_NAME'] )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # index webpage just to welcome the users and for testing purposes
    @app.route('/')
    def index():
        return 'Hi, welcome to the IP services app'
    
    # initialize the db object
    model.init_app(app)

    # add the blueprint with ip APIs
    app.register_blueprint(ip_services.bp)
    

    return app