from flask import Flask
from flask_bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.babel import Babel
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_nav import Nav
from flask_mail import Mail
from celery import Celery as CeleryClass
from functools import partial
import os


class Celery(CeleryClass):
    """
    Subclasses the original Celery class to obtain a new class
    suitable to work under the app factory paradigm of Flask.
    """

    def __init__(self, app=None):
        """
        If app argument provided then initialize celery using application
        config values.  If no app argument provided you should do
        initialization later with `init_app` method.

        Args:
           app: Flask application instance.

        """
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Actual method to read celery settings from `app` configuration and
        initialize the celery instance.

        Args:
           app: Flask application instance.

        """
        # Instantiate celery and read config
        super(Celery, self).__init__(app.name,
                                     broker=app.config['CELERY_BROKER_URL'])
        # Update the config
        self.conf.update(app.config)

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
nav = Nav()
celery = Celery()
mail = Mail()
babel = Babel()
login_manager = LoginManager()

_buildout_path = __file__

for i in range(2 + __name__.count('.')):
    _buildout_path = os.path.dirname(_buildout_path)

abspath = partial(os.path.join, _buildout_path)


@login_manager.user_loader
def load_user(user_id):
    from revot.models import User
    return User.query.get(user_id)


def create_app(config):
    """
    Flask app factory. Creates an app for Flask application after setting
    up configurations, Flask extensions and project blueprints,
    """
    app = Flask('revot')

    # app.config.from_object(config)
    app.config.from_pyfile(abspath(config))
    # config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    nav.init_app(app)
    mail.init_app(app)
    celery.init_app(app)
    babel.init_app(app)
    login_manager.init_app(app)

    import pdb; pdb.set_trace()
    
    # Register blueprints
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from populate import populate as populate_blueprint
    app.register_blueprint(populate_blueprint)

    from navigation import navigation as navigation_blueprint
    app.register_blueprint(navigation_blueprint)

    return app
