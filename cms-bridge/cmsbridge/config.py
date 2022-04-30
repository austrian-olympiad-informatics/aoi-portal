import os
from pathlib import Path

basedir = Path(__file__).parent.parent.resolve()

class Config:
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv('SECRET_KEY', default='A very terrible secret key.')
    

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    FLASK_ENV = 'production'
