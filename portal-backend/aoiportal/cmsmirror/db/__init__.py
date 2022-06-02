#!/usr/bin/env python3

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2012 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2018 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2012 Matteo Boscariol <boscarim@hotmail.com>
# Copyright © 2013 Bernard Blackham <bernard@largestprime.net>
# Copyright © 2013-2018 Luca Wehrstedt <luca.wehrstedt@gmail.com>
# Copyright © 2016 Myungwoo Chun <mc.tamaki@gmail.com>
# Copyright © 2016 Masaki Hara <ackie.h.gmai@gmail.com>
# Copyright © 2016 Amir Keivan Mohtashami <akmohtashami97@gmail.com>
# Copyright © 2018 William Di Luigi <williamdiluigi@gmail.com>
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

"""Utilities functions that interacts with the database.

"""

import logging


logger = logging.getLogger(__name__)


# Define what this package will provide.

__all__ = [
    # session
    "session", "init_app", "custom_psycopg2_connection",
    # types
    "CastingArray", "Codename", "Filename", "FilenameSchema",
    "FilenameSchemaArray", "Digest",
    # base
    "Base",
    # fsobject
    "FSObject", "LargeObject",
    # contest
    "Contest", "Announcement",
    # user
    "User", "Team", "Participation", "Message", "Question",
    # admin
    "Admin",
    # task
    "Task", "Statement", "Attachment", "Dataset", "Manager", "Testcase",
    # submission
    "Submission", "File", "Token", "SubmissionResult", "Executable",
    "Evaluation",
    # usertest
    "UserTest", "UserTestFile", "UserTestManager", "UserTestResult",
    "UserTestExecutable",
    # printjob
    "PrintJob",
]

from .session import custom_psycopg2_connection, init_app, session

from .types import CastingArray, Codename, Filename, FilenameSchema, \
    FilenameSchemaArray, Digest
from .base import Base
from .fsobject import FSObject, LargeObject
from .admin import Admin
from .contest import Contest, Announcement
from .user import User, Team, Participation, Message, Question
from .task import Task, Statement, Attachment, Dataset, Manager, Testcase
from .submission import Submission, File, Token, SubmissionResult, \
    Executable, Evaluation
from .usertest import UserTest, UserTestFile, UserTestManager, \
    UserTestResult, UserTestExecutable
from .printjob import PrintJob
