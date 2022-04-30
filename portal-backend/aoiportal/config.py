import os
from pathlib import Path

basedir = Path(__file__).parent.parent.resolve()

class Config:
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv('SECRET_KEY', default='A very terrible secret key.')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "in-v3.mailjet.com"
    MAIL_PORT = "587"
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "ee91a33e942f4d9c24c337568e464897"
    MAIL_PASSWORD = "13424eab478dbd4c3e7fd39331043e8f"
    MAIL_DEFAULT_SENDER = "no-reply@informatikolympiade.at"
    BASE_URL = "https://informatikolympiade.at"

    GITHUB_OAUTH_CLIENT_ID = "cfe045dca29cdc1d6946"
    GITHUB_OAUTH_CLIENT_SECRET = "a97c964b63a19c0ba005a428ce722f05d2581c89"
    GOOGLE_OAUTH_CLIENT_ID = "847147435197-t51o4unviedru0m0d05jpt0qa5gvvi5p.apps.googleusercontent.com"
    GOOGLE_OAUTH_CLIENT_SECRET = "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"

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(basedir / "dev.db")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(basedir / "test.db")

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv('PROD_DATABASE_URI')
