import os
import argparse
import sys

from cmsbridge.factory import create_app
from cmsbridge.config import DevelopmentConfig

app = create_app(DevelopmentConfig)

parser = argparse.ArgumentParser("cmsbridge")
subparsers = parser.add_subparsers(help="action", dest="action")

wsgi_parser = subparsers.add_parser("wsgi")
wsgi_parser.add_argument("-p", "--port", type=int, default=5000)
wsgi_parser.add_argument("--host", type=str, default="0.0.0.0")


def cmd_wsgi(args):
    print(app.url_map)
    app.run(host=args.host, port=args.port)


COMMANDS = {
    "wsgi": cmd_wsgi,
}


if __name__ == '__main__':
    args = parser.parse_args()
    cmd = COMMANDS[args.action]
    sys.exit(cmd(args) or 0)
