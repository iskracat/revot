# -*- coding: utf-8   -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or '6LeYIbsSAAAAAJezaIq3Ft_hSTo'
    USERNAME = 'admin'
    PASSWORD = 'default'
    BOOTSTRAP_QUERYSTRING_REVVING = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # Voting workflow timing constants
    MIN_VOTING_DURATION_IN_MINUTES = 60
    READY_TO_SEND_BALLOTS_IN_MINUTES = 20
    MIN_TIME_TO_SEND_BALLOTS_IN_MINUTES = 60
    # Celery settings
    CELERY_BROKER_URL='redis://localhost'
    CELERY_RESULT_BACKEND='redis://localhost'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    # Email settings
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=587
    MAIL_USE_SSL=False
    MAIL_USE_TLS=True
    MAIL_DEFAULT_SENDER='sebas.vima@gmail.com'
    MAIL_USERNAME = 'sebas.vima@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '6LeYIbsSAAAAAJezaIq3Ft_hSTo'
    # Babel i18n defaults
    BABEL_DEFAULT_LOCALE='ca'
    BABEL_DEFAULT_TIMEZONE='UTC'
    LANGUAGES={'en': u'English', 'ca': u'Català'}

    
    @staticmethod
    def init_app(app):
        pass

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/revot.db'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/revot.db'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/revot.db'
    SQLALCHEMY_ECHO = False
    MIN_VOTING_DURATION_IN_MINUTES = 10
    READY_TO_SEND_BALLOTS_IN_MINUTES = 0
    MIN_TIME_TO_SEND_BALLOTS_IN_MINUTES = 4
    MAIL_DEBUG=True
    SERVER_NAME='localhost:5000'
    HOST='0.0.0.0'

    
config = {
    'development' : DevelopmentConfig,
    'testing'     : TestingConfig,
    'production'  : ProductionConfig,
    'default'     : DevelopmentConfig
    }
