from pathlib import Path

basedir = Path(__file__).parent.parent.resolve()


class DefaultConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentDefaultConfig(DefaultConfig):
    FLASK_ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(basedir / "dev.db")
    CMS_DATABASE_URI = "sqlite:///" + str(basedir / "cms.db")
    SECRET_KEY = "A very terrible secret key."
    AOI_SESSION_TOKEN_KEY = "UZb1zOeZtEw1fsWhRftFE0AqSVTLAouZzFwt5cwiqSo="
    CMSBRIDGE_BASE_URL = "http://localhost:5001"
    BASE_URL = "http://localhost:8080"
    DISCORD_OAUTH_CLIENT_ID = "1069392790443790508"
    DISCORD_OAUTH_CLIENT_SECRET = "RZ7Sckf4auRwAs0N0IRn_1HdUbKXAIOZ"


class ProductionDefaultConfig(DefaultConfig):
    FLASK_ENV = "production"
