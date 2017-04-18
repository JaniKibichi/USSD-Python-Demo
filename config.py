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
    SECRET_KEY = os.environ.get('SECRETE_KEY') or str(uuid.uuid4())
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    
    AT_APIKEY = "3b7af98d0e2fb886898dc495c4e8e235764ecaf1a843caa4fbd92bf116aa1bb7"
    AT_USERNAME = "darklotus"
    AT_NUMBER = "+254703554404"
    SMS_CODE = 2080
    PRODUCT_NAME = "Nerds Payements"
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    Configuration variables when in development mode
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    """
    Testing configuration variables
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}