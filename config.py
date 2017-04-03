#usr/bin/python
"""
Configuration for the USSD application
"""
import os
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))  # base directory

class Config:
    """
    General configuration variables
    """
    AT_APIKEY = "3b7af98d0e2fb886898dc495c4e8e235764ecaf1a843caa4fbd92bf116aa1bb7"
    AT_USERNAME = "darklotus"
    SECRET_KEY = os.environ.get('SECRETE_KEY') or str(uuid.uuid4())
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    USSD_MAIL_SUBJECT_PREFIX = '[USSD]'
    USSD_MAIL_SENDER = 'USSD admin'
    USSD_ADMIN = os.environ.get('USSD_ADMIN') or 'npiusdan@gmail.com'
    SSL_DISABLE = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    Configuration variables when in development mode
    """
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'npiusdan@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '!((^tsunami13237'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    """
    Testing configuration variables
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    """
    Production mode configuration
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrator
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                                   fromaddr=cls.USSD_MAIL_SENDER,
                                   toaddrs=[cls.USSD_ADMIN],
                                   subject=cls.USSD_MAIL_SUBJECT_PREFIX + 'Application Error',
                                   credentials=credentials,
                                   secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}