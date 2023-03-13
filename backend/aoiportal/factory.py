import json
from pathlib import Path

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from aoiportal import error
from aoiportal.admin import admin_bp
from aoiportal.auth import auth_bp
from aoiportal.bot import bot_bp
from aoiportal.contests import contests_bp
from aoiportal.mail import mail
from aoiportal.models import db  # type: ignore
from aoiportal.newsletter import newsletter_bp
from aoiportal.oauth import oauth_bp
from aoiportal.profile import profile_bp


def create_app(base_config_obj, config_file):
    package = __name__.split(".", 1)[0]
    app = Flask(package, instance_relative_config=True)

    app.config.from_object(base_config_obj)
    if Path(config_file).is_file():
        app.config.from_file(config_file, load=json.load)

    db.init_app(app)
    mail.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(contests_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(newsletter_bp)
    app.register_blueprint(bot_bp)
    error.init_app(app)

    from aoiportal.cmsmirror.admin import cmsadmin_bp  # type: ignore
    from aoiportal.cmsmirror.db import init_app as cmsmirror_init_app  # type: ignore
    from aoiportal.cmsmirror.views import cmsmirror_bp  # type: ignore

    cmsmirror_init_app(app)
    app.register_blueprint(cmsmirror_bp)
    app.register_blueprint(cmsadmin_bp)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    return app
