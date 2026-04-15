import os
import argparse
from pathlib import Path
import sys
from aoiportal.auth_util import hash_password

from aoiportal.factory import create_app
from aoiportal.models import db, User
from aoiportal.config import DevelopmentDefaultConfig

parser = argparse.ArgumentParser("aoiportal")
parser.add_argument("-c", "--config", type=str, 
                   default=str(Path(__file__).parent / "config" / "dev.yaml"),
                   help="Path to config file")
subparsers = parser.add_subparsers(help="action", dest="action")

wsgi_parser = subparsers.add_parser("wsgi")
wsgi_parser.add_argument("-p", "--port", type=int, default=5000)
wsgi_parser.add_argument("--host", type=str, default="0.0.0.0")

createdb_parser = subparsers.add_parser("createdb")

dropdb_parser = subparsers.add_parser("dropdb")

addadmin_parser = subparsers.add_parser("addadmin")
addadmin_parser.add_argument("--email", type=str, required=True)
addadmin_parser.add_argument("--first-name", dest="first_name", type=str, required=True)
addadmin_parser.add_argument("--last-name", dest="last_name", type=str, required=True)
addadmin_parser.add_argument("--password", type=str, required=True)

refreshcmscontests_parser = subparsers.add_parser("refreshcmscontests")


def cmd_wsgi(app, args):
    print(app.url_map)
    app.run(host=args.host, port=args.port)


def cmd_createdb(app, args):
    with app.app_context():
        db.create_all()


def cmd_dropdb(app, args):
    with app.app_context():
        db.drop_all()


def cmd_addadmin(app, args):
    with app.app_context():
        u = User(
            email=args.email,
            first_name=args.first_name,
            last_name=args.last_name,
            is_admin=True,
            password_hash=hash_password(args.password),
        )
        db.session.add(u)
        db.session.commit()


def cmd_refreshcmscontests(app, args):
    from aoiportal.admin import sync_cms_contests
    with app.app_context():
        sync_cms_contests()


COMMANDS = {
    "wsgi": cmd_wsgi,
    "createdb": cmd_createdb,
    "dropdb": cmd_dropdb,
    "addadmin": cmd_addadmin,
    "refreshcmscontests": cmd_refreshcmscontests,
}


if __name__ == '__main__':
    args = parser.parse_args()
    app = create_app(args.config)
    cmd = COMMANDS[args.action]
    sys.exit(cmd(app, args) or 0)
