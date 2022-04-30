import os
import argparse
import sys

from aoiportal.factory import create_app
from aoiportal.models import db, User
from aoiportal.config import DevelopmentConfig
from aoiportal.utils import utcnow

app = create_app(DevelopmentConfig)

parser = argparse.ArgumentParser("aoiportal")
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


def cmd_wsgi(args):
    print(app.url_map)
    app.run(host=args.host, port=args.port)


def cmd_createdb(args):
    with app.app_context():
        db.create_all()


def cmd_dropdb(args):
    with app.app_context():
        db.drop_all()


def cmd_addadmin(args):
    with app.app_context():
        u = User(
            email=args.email,
            first_name=args.first_name,
            last_name=args.last_name,
            is_admin=True,
            email_confirmed=True,
            last_email_confirmed_at=utcnow(),
        )
        u.set_password(args.password)
        db.session.add(u)
        db.session.commit()


COMMANDS = {
    "wsgi": cmd_wsgi,
    "createdb": cmd_createdb,
    "dropdb": cmd_dropdb,
    "addadmin": cmd_addadmin
}


if __name__ == '__main__':
    args = parser.parse_args()
    cmd = COMMANDS[args.action]
    sys.exit(cmd(args) or 0)
