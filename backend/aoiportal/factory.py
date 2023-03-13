from pathlib import Path

import voluptuous as vol  # type: ignore
from flask import Flask
from yaml import safe_load  # type: ignore

from aoiportal import error
from aoiportal.admin import admin_bp
from aoiportal.auth import auth_bp
from aoiportal.bot import bot_bp
from aoiportal.const import (
    KEY_BASE_URL,
    KEY_CLIENT_ID,
    KEY_CLIENT_SECRET,
    KEY_CMS,
    KEY_DATABASE_URI,
    KEY_DEBUG,
    KEY_DEFAULT_SENDER,
    KEY_DISCORD_OAUTH,
    KEY_EVALUATION_SERVICE,
    KEY_GITHUB_OAUTH,
    KEY_GOOGLE_OAUTH,
    KEY_HOST,
    KEY_MAIL,
    KEY_PASSWORD,
    KEY_PORT,
    KEY_SECRET_KEY,
    KEY_SESSION_TOKEN_KEY,
    KEY_USE_TLS,
    KEY_USERNAME,
)
from aoiportal.contests import contests_bp
from aoiportal.mail import mail
from aoiportal.models import db  # type: ignore
from aoiportal.newsletter import newsletter_bp
from aoiportal.oauth import oauth_bp
from aoiportal.profile import profile_bp

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(KEY_DATABASE_URI): str,
        vol.Required(KEY_SECRET_KEY): str,
        vol.Required(KEY_SESSION_TOKEN_KEY): str,
        vol.Optional(KEY_DEBUG, default=False): bool,
        vol.Optional(KEY_BASE_URL, default=None): vol.Any(None, str),
        vol.Optional(KEY_MAIL): vol.Schema(
            {
                vol.Optional(KEY_HOST, default="localhost"): str,
                vol.Optional(KEY_PORT, default=25): int,
                vol.Optional(KEY_USE_TLS, default=False): bool,
                vol.Optional(KEY_USERNAME, default=None): vol.Any(str, None),
                vol.Optional(KEY_PASSWORD, default=None): vol.Any(str, None),
                vol.Optional(KEY_DEFAULT_SENDER, default=None): vol.Any(str, None),
            }
        ),
        vol.Optional(KEY_GITHUB_OAUTH): vol.Schema(
            {
                vol.Required(KEY_CLIENT_ID): str,
                vol.Required(KEY_CLIENT_SECRET): str,
            }
        ),
        vol.Optional(KEY_GOOGLE_OAUTH): vol.Schema(
            {
                vol.Required(KEY_CLIENT_ID): str,
                vol.Required(KEY_CLIENT_SECRET): str,
            }
        ),
        vol.Optional(KEY_DISCORD_OAUTH): vol.Schema(
            {
                vol.Required(KEY_CLIENT_ID): str,
                vol.Required(KEY_CLIENT_SECRET): str,
            }
        ),
        vol.Optional(KEY_CMS): vol.Schema(
            {
                vol.Required(KEY_DATABASE_URI): str,
                vol.Optional(KEY_EVALUATION_SERVICE, default={}): vol.Schema(
                    {
                        vol.Optional(KEY_HOST, default="localhost"): str,
                        vol.Optional(KEY_PORT, default=25000): int,
                    }
                ),
            }
        ),
    }
)


def create_app(config_file: Path):
    package = __name__.split(".", 1)[0]
    app = Flask(package, instance_relative_config=True)

    if not config_file.is_file():
        raise FileNotFoundError(f"Configuration file {config_file} not found")

    with config_file.open() as f:
        conf = safe_load(f)

    conf = CONFIG_SCHEMA(conf)

    app.config["DEBUG"] = conf[KEY_DEBUG]
    app.config["SECRET_KEY"] = conf[KEY_SECRET_KEY]
    app.config["AOI_SESSION_TOKEN_KEY"] = conf[KEY_SESSION_TOKEN_KEY]
    app.config["BASE_URL"] = conf[KEY_BASE_URL]
    app.config["SQLALCHEMY_DATABASE_URI"] = conf[KEY_DATABASE_URI]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if KEY_MAIL in conf:
        app.config["MAIL_SERVER"] = conf[KEY_MAIL][KEY_HOST]
        app.config["MAIL_PORT"] = conf[KEY_MAIL][KEY_PORT]
        app.config["MAIL_USE_TLS"] = conf[KEY_MAIL][KEY_USE_TLS]
        app.config["MAIL_USERNAME"] = conf[KEY_MAIL][KEY_USERNAME]
        app.config["MAIL_PASSWORD"] = conf[KEY_MAIL][KEY_PASSWORD]
        app.config["MAIL_DEFAULT_SENDER"] = conf[KEY_MAIL][KEY_DEFAULT_SENDER]

    if KEY_GITHUB_OAUTH in conf:
        app.config["GITHUB_OAUTH_CLIENT_ID"] = conf[KEY_GITHUB_OAUTH][KEY_CLIENT_ID]
        app.config["GITHUB_OAUTH_CLIENT_SECRET"] = conf[KEY_GITHUB_OAUTH][
            KEY_CLIENT_SECRET
        ]

    if KEY_GOOGLE_OAUTH in conf:
        app.config["GOOGLE_OAUTH_CLIENT_ID"] = conf[KEY_GOOGLE_OAUTH][KEY_CLIENT_ID]
        app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = conf[KEY_GOOGLE_OAUTH][
            KEY_CLIENT_SECRET
        ]

    if KEY_DISCORD_OAUTH in conf:
        app.config["DISCORD_OAUTH_CLIENT_ID"] = conf[KEY_DISCORD_OAUTH][KEY_CLIENT_ID]
        app.config["DISCORD_OAUTH_CLIENT_SECRET"] = conf[KEY_DISCORD_OAUTH][
            KEY_CLIENT_SECRET
        ]

    if KEY_CMS in conf:
        app.config["CMS_DATABASE_URI"] = conf[KEY_CMS][KEY_DATABASE_URI]
        app.config["CMS_EVALUATION_SERVICE_HOST"] = conf[KEY_CMS][
            KEY_EVALUATION_SERVICE
        ][KEY_HOST]
        app.config["CMS_EVALUATION_SERVICE_PORT"] = conf[KEY_CMS][
            KEY_EVALUATION_SERVICE
        ][KEY_PORT]

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

    if KEY_CMS in conf:
        from aoiportal.cmsmirror.admin import cmsadmin_bp  # type: ignore
        from aoiportal.cmsmirror.db import init_app as cmsia  # type: ignore
        from aoiportal.cmsmirror.views import cmsmirror_bp  # type: ignore

        cmsia(app)
        app.register_blueprint(cmsmirror_bp)
        app.register_blueprint(cmsadmin_bp)

    return app
