
class DefaultConfig:
    TESTING = False
    

class DevelopmentDefaultConfig(DefaultConfig):
    FLASK_ENV = 'development'
    DEBUG = True
    SECRET_KEY = 'A very terrible secret key.'


class ProductionDefaultConfig(DefaultConfig):
    FLASK_ENV = 'production'
    DEBUG = False
