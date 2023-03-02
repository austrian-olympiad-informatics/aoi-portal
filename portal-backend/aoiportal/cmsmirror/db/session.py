# type: ignore

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2013 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2018 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2012 Matteo Boscariol <boscarim@hotmail.com>
# Copyright © 2013 Luca Wehrstedt <luca.wehrstedt@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Utilities related to SQLAlchemy sessions.

Contains context managers and custom methods to create sessions to
interact with SQLAlchemy objects.

"""

import logging
from dataclasses import dataclass

import psycopg2
from flask import Flask, current_app, g
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.engine import Engine, make_url  # type: ignore
from sqlalchemy.orm import Session, scoped_session, sessionmaker  # type: ignore
from werkzeug.local import LocalProxy

logger = logging.getLogger(__name__)
KEY_CMS_SESSION = "_cmsmirror_db_session"


@dataclass
class CMSExtData:
    engine: Engine
    session_factory: sessionmaker
    scoped_session_factory: scoped_session


def init_app(app: Flask) -> None:
    database_uri = app.config["CMS_DATABASE_URI"]
    engine = create_engine(database_uri)  # , echo=True)
    session_factory = sessionmaker(bind=engine)
    scoped_session_factory = scoped_session(session_factory)
    app.extensions["cms"] = CMSExtData(
        engine=engine,
        session_factory=session_factory,
        scoped_session_factory=scoped_session_factory,
    )

    @app.teardown_appcontext
    def teardown_db(exc):
        sess = g.pop(KEY_CMS_SESSION, None)
        if sess is not None:
            sess.close()


def _get_session() -> Session:
    if not hasattr(g, KEY_CMS_SESSION):
        setattr(
            g, KEY_CMS_SESSION, current_app.extensions["cms"].scoped_session_factory()
        )
    return getattr(g, KEY_CMS_SESSION)


session: Session = LocalProxy(lambda: _get_session())


def custom_psycopg2_connection(**kwargs):
    """Establish a new psycopg2.connection to the database.

    The returned connection won't be in the SQLAlchemy pool and has to
    be closed manually by the caller when it's done with it.

    All psycopg2-specific code in CMS is supposed to obtain a function
    this way.

    kwargs (dict): additional values to use as query parameters in the
        connection URL.

    return (connection): a new, shiny connection object.

    raise (AssertionError): if CMS (actually SQLAlchemy) isn't
        configured to use psycopg2 as the DB-API driver.

    """
    database_uri = current_app.config["CMS_DATABASE_URI"]
    database_url = make_url(database_uri)
    assert database_url.get_dialect().driver == "psycopg2"
    # For Unix-domain socket we don't have a port nor a host and that's fine.
    if database_url.port is None and database_url.host is not None:
        database_url.port = 5432

    # Unix-domain socket have the host in a query argument, so we build the
    # arguments dict first to avoid duplicate arguments when calling connect().
    args = {
        "host": database_url.host,
        "port": database_url.port,
        "user": database_url.username,
        "password": database_url.password,
        "database": database_url.database,
    }
    args.update(database_url.query)
    args.update(kwargs)

    return psycopg2.connect(**args)
