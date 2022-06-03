# type: ignore

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

from .admin import Admin
from .base import Base
from .contest import Announcement, Contest
from .fsobject import FSObject, LargeObject
from .printjob import PrintJob
from .session import custom_psycopg2_connection, init_app, session
from .submission import (
    Evaluation,
    Executable,
    File,
    Meme,
    Submission,
    SubmissionResult,
    Token,
)
from .task import (
    Attachment,
    Dataset,
    LanguageTemplate,
    Manager,
    Statement,
    Task,
    Testcase,
    TestManager,
)
from .types import (
    CastingArray,
    Codename,
    Digest,
    Filename,
    FilenameSchema,
    FilenameSchemaArray,
)
from .user import Message, Participation, Question, Team, User
from .usereval import UserEval, UserEvalExecutable, UserEvalFile, UserEvalResult
from .usertest import (
    UserTest,
    UserTestExecutable,
    UserTestFile,
    UserTestManager,
    UserTestResult,
)

logger = logging.getLogger(__name__)


# Define what this package will provide.

__all__ = [
    # session
    "session",
    "init_app",
    "custom_psycopg2_connection",
    # types
    "CastingArray",
    "Codename",
    "Filename",
    "FilenameSchema",
    "FilenameSchemaArray",
    "Digest",
    # base
    "Base",
    # fsobject
    "FSObject",
    "LargeObject",
    # contest
    "Contest",
    "Announcement",
    # user
    "User",
    "Team",
    "Participation",
    "Message",
    "Question",
    # admin
    "Admin",
    # task
    "Task",
    "Statement",
    "Attachment",
    "Dataset",
    "Manager",
    "Testcase",
    "LanguageTemplate",
    "TestManager",
    # submission
    "Submission",
    "File",
    "Token",
    "SubmissionResult",
    "Executable",
    "Evaluation",
    "Meme",
    # usertest
    "UserTest",
    "UserTestFile",
    "UserTestManager",
    "UserTestResult",
    "UserTestExecutable",
    # printjob
    "PrintJob",
    # usereval
    "UserEval",
    "UserEvalFile",
    "UserEvalResult",
    "UserEvalExecutable",
]
