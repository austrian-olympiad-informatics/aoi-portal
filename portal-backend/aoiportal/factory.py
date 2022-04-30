from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from aoiportal.models import db
from aoiportal.auth import login_manager, auth_bp
from aoiportal.oauth import oauth_bp
from aoiportal.mail import mail
from aoiportal.profile import profile_bp
from aoiportal.admin import admin_bp
from aoiportal.contests import contests_bp


def create_app(settings_obj):
    package = __name__.split('.')[0]
    app = Flask(package, instance_relative_config=True)

    app.config.from_object(settings_obj)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(contests_bp)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    return app
