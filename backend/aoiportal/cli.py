from pathlib import Path

import click
from flask import Flask, current_app
from flask.cli import FlaskGroup, pass_script_info

from aoiportal.factory import create_app as factory_create_app


def create_app(*args, **kwargs):
    ctx = click.get_current_context()
    script_info = ctx.obj

    if not hasattr(script_info, "config"):
        # for example --help command
        return None

    app: Flask = factory_create_app(Path(script_info.config))

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
@click.option(
    "-c", "--config", default="config/config.yaml", help="Path to config file"
)
@pass_script_info
def cli(script_info, config):
    script_info.config = config


@cli.command()
def initdb():
    """Initialize the database."""
    with current_app.app_context():
        from aoiportal.models import db

        db.create_all()


@cli.command()
def dropdb():
    """Drop the database."""
    with current_app.app_context():
        from aoiportal.models import db

        db.drop_all()


@cli.command()
@click.option("--email", type=str, required=True)
@click.option("--first-name", type=str, required=True)
@click.option("--last-name", type=str, required=True)
@click.option("--password", type=str, required=True)
def addadmin(email, first_name, last_name, password):
    """Add an admin user."""
    with current_app.app_context():
        from aoiportal.auth_util import hash_password
        from aoiportal.models import User, db

        u = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=True,
            password_hash=hash_password(password),
        )
        db.session.add(u)
        db.session.commit()
