#!/usr/bin/env python3

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2012 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2012-2015 Luca Wehrstedt <luca.wehrstedt@gmail.com>
# Copyright © 2015-2016 Stefano Maggiolo <s.maggiolo@gmail.com>
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

"""UserTest-related database interface for SQLAlchemy.

"""

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey, ForeignKeyConstraint, \
    UniqueConstraint
from sqlalchemy.types import Integer, Float, String, Unicode, DateTime, \
    BigInteger

from . import Filename, FilenameSchema, Digest, Base, Participation, Task, \
    Dataset


class UserEval(Base):
    __tablename__ = 'user_evals'

    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    uuid = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    # User and Contest, thus Participation (id and object) that did the
    # submission.
    participation_id = Column(
        Integer,
        ForeignKey(Participation.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True)
    participation = relationship(
        Participation,
        back_populates="user_evals")

    # Task (id and object) of the eval.
    task_id = Column(
        Integer,
        ForeignKey(Task.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True)
    task = relationship(
        Task,
        back_populates="user_evals")

    # Time of the request.
    timestamp = Column(
        DateTime,
        nullable=False)

    # Language of eval, or None if not applicable.
    language = Column(
        String,
        nullable=True)

    # Input (provided by the user) file's digest for this eval.
    input = Column(
        Digest,
        nullable=False)

    # These one-to-many relationships are the reversed directions of
    # the ones defined in the "child" classes using foreign keys.

    files = relationship(
        "UserEvalFile",
        collection_class=attribute_mapped_collection("filename"),
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="user_eval")

    results = relationship(
        "UserEvalResult",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="user_eval")

    def get_result(self, dataset=None):
        """Return the result associated to a dataset.

        dataset (Dataset|None): the dataset for which the caller wants
            the user eval result; if None, the active one is used.

        return (UserEvalResult|None): the user eval result associated
            to this user eval and the given dataset, if it exists in
            the database, otherwise None.

        """
        if dataset is not None:
            # Use IDs to avoid triggering a lazy-load query.
            assert self.task_id == dataset.task_id
            dataset_id = dataset.id
        else:
            dataset_id = self.task.active_dataset_id

        return UserEvalResult.get_from_id(
            (self.id, dataset_id), self.sa_session)

    def get_result_or_create(self, dataset=None):
        """Return and, if necessary, create the result for a dataset.

        dataset (Dataset|None): the dataset for which the caller wants
            the user eval result; if None, the active one is used.

        return (UserEvalResult): the user eval result associated to
            the this user eval and the given dataset; if it does not
            exists, a new one is created.

        """
        if dataset is None:
            dataset = self.task.active_dataset

        user_eval_result = self.get_result(dataset)

        if user_eval_result is None:
            user_eval_result = UserEvalResult(user_eval=self,
                                              dataset=dataset)

        return user_eval_result


class UserEvalFile(Base):
    __tablename__ = 'user_eval_files'
    __table_args__ = (
        UniqueConstraint('user_eval_id', 'filename'),
    )

    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    # UserEval (id and object) owning the file.
    user_eval_id = Column(
        Integer,
        ForeignKey(UserEval.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True)
    user_eval = relationship(
        UserEval,
        back_populates="files")

    # Filename and digest of the submitted file.
    filename = Column(
        FilenameSchema,
        nullable=False)
    digest = Column(
        Digest,
        nullable=False)


class UserEvalResult(Base):
    """Class to store the execution results of a user_eval.

    """
    # Possible statuses of a user eval result. COMPILING and
    # EVALUATING do not necessarily imply we are going to schedule
    # compilation and run for these user eval results: for
    # example, they might be for datasets not scheduled for
    # evaluation, or they might have passed the maximum number of
    # tries. If a user eval result does not exists for a pair
    # (user eval, dataset), its status can be implicitly assumed to
    # be COMPILING.
    COMPILING = 1
    COMPILATION_FAILED = 2
    EVALUATING = 3
    EVALUATED = 4

    __tablename__ = 'user_eval_results'
    __table_args__ = (
        UniqueConstraint('user_eval_id', 'dataset_id'),
    )

    # Primary key is (user_eval_id, dataset_id).
    user_eval_id = Column(
        Integer,
        ForeignKey(UserEval.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True)
    user_eval = relationship(
        UserEval,
        back_populates="results")

    dataset_id = Column(
        Integer,
        ForeignKey(Dataset.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True)
    dataset = relationship(
        Dataset)

    # Now below follow the actual result fields.

    # Output file's digest for this eval
    output = Column(
        Digest,
        nullable=True)

    # Compilation outcome (can be None = yet to compile, "ok" =
    # compilation successful and we can evaluate, "fail" =
    # compilation unsuccessful, throw it away).
    compilation_outcome = Column(
        String,
        nullable=True)

    # The output from the sandbox (to allow localization the first item
    # of the list is a format string, possibly containing some "%s",
    # that will be filled in using the remaining items of the list).
    compilation_text = Column(
        ARRAY(String),
        nullable=False,
        default=[])

    # Number of attempts of compilation.
    compilation_tries = Column(
        Integer,
        nullable=False,
        default=0)

    # The compiler stdout and stderr.
    compilation_stdout = Column(
        Unicode,
        nullable=True)
    compilation_stderr = Column(
        Unicode,
        nullable=True)

    # Other information about the compilation.
    compilation_time = Column(
        Float,
        nullable=True)
    compilation_wall_clock_time = Column(
        Float,
        nullable=True)
    compilation_memory = Column(
        BigInteger,
        nullable=True)

    # Worker shard and sandbox where the compilation was performed.
    compilation_shard = Column(
        Integer,
        nullable=True)
    compilation_sandbox = Column(
        String,
        nullable=True)

    # Evaluation outcome (can be None = yet to evaluate, "ok" =
    # evaluation successful).
    evaluation_outcome = Column(
        String,
        nullable=True)

    # The output from the grader, usually "Correct", "Time limit", ...
    # (to allow localization the first item of the list is a format
    # string, possibly containing some "%s", that will be filled in
    # using the remaining items of the list).
    evaluation_text = Column(
        ARRAY(String),
        nullable=False,
        default=[])

    # Number of attempts of evaluation.
    evaluation_tries = Column(
        Integer,
        nullable=False,
        default=0)

    # Other information about the execution.
    execution_time = Column(
        Float,
        nullable=True)
    execution_wall_clock_time = Column(
        Float,
        nullable=True)
    execution_memory = Column(
        BigInteger,
        nullable=True)

    # Worker shard and sandbox where the evaluation was performed.
    evaluation_shard = Column(
        Integer,
        nullable=True)
    evaluation_sandbox = Column(
        String,
        nullable=True)

    # These one-to-many relationships are the reversed directions of
    # the ones defined in the "child" classes using foreign keys.

    executables = relationship(
        "UserEvalExecutable",
        collection_class=attribute_mapped_collection("filename"),
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="user_eval_result")

    def get_status(self):
        """Return the status of this object.

        """
        if not self.compiled():
            return UserEvalResult.COMPILING
        elif self.compilation_failed():
            return UserEvalResult.COMPILATION_FAILED
        elif not self.evaluated():
            return UserEvalResult.EVALUATING
        else:
            return UserEvalResult.EVALUATED

    def compiled(self):
        """Return whether the user eval result has been compiled.

        return (bool): True if compiled, False otherwise.

        """
        return self.compilation_outcome is not None

    @staticmethod
    def filter_compiled():
        """Return a filtering expression for compiled user eval results.

        """
        return UserEvalResult.compilation_outcome.isnot(None)

    def compilation_failed(self):
        """Return whether the user eval result did not compile.

        return (bool): True if the compilation failed (in the sense
            that there is a problem in the user's source), False if
            not yet compiled or compilation was successful.

        """
        return self.compilation_outcome == "fail"

    @staticmethod
    def filter_compilation_failed():
        """Return a filtering expression for user eval results failing
        compilation.

        """
        return UserEvalResult.compilation_outcome == "fail"

    def compilation_succeeded(self):
        """Return whether the user eval compiled.

        return (bool): True if the compilation succeeded (in the sense
            that an executable was created), False if not yet compiled
            or compilation was unsuccessful.

        """
        return self.compilation_outcome == "ok"

    @staticmethod
    def filter_compilation_succeeded():
        """Return a filtering expression for user eval results failing
        compilation.

        """
        return UserEvalResult.compilation_outcome == "ok"

    def evaluated(self):
        """Return whether the user eval result has been evaluated.

        return (bool): True if evaluated, False otherwise.

        """
        return self.evaluation_outcome is not None

    @staticmethod
    def filter_evaluated():
        """Return a filtering lambda for evaluated user eval results.

        """
        return UserEvalResult.evaluation_outcome.isnot(None)

    def invalidate_compilation(self):
        """Blank all compilation and evaluation outcomes.

        """
        self.invalidate_evaluation()
        self.compilation_outcome = None
        self.compilation_text = []
        self.compilation_tries = 0
        self.compilation_time = None
        self.compilation_wall_clock_time = None
        self.compilation_memory = None
        self.compilation_shard = None
        self.compilation_sandbox = None
        self.executables = {}

    def invalidate_evaluation(self):
        """Blank the evaluation outcome.

        """
        self.evaluation_outcome = None
        self.evaluation_text = []
        self.evaluation_tries = 0
        self.execution_time = None
        self.execution_wall_clock_time = None
        self.execution_memory = None
        self.evaluation_shard = None
        self.evaluation_sandbox = None
        self.output = None

    def set_compilation_outcome(self, success):
        """Set the compilation outcome based on the success.

        success (bool): if the compilation was successful.

        """
        self.compilation_outcome = "ok" if success else "fail"

    def set_evaluation_outcome(self):
        """Set the evaluation outcome (always ok now).

        """
        self.evaluation_outcome = "ok"


class UserEvalExecutable(Base):
    """Class to store information about one file generated by the
    compilation of a user eval.

    """
    __tablename__ = 'user_eval_executables'
    __table_args__ = (
        ForeignKeyConstraint(
            ('user_eval_id', 'dataset_id'),
            (UserEvalResult.user_eval_id, UserEvalResult.dataset_id),
            onupdate="CASCADE", ondelete="CASCADE"),
        UniqueConstraint('user_eval_id', 'dataset_id', 'filename'),
    )

    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    # UserEval (id and object) owning the executable.
    user_eval_id = Column(
        Integer,
        ForeignKey(UserEval.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True)
    user_eval = relationship(
        UserEval,
        viewonly=True)

    # Dataset (id and object) owning the executable.
    dataset_id = Column(
        Integer,
        ForeignKey(Dataset.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True)
    dataset = relationship(
        Dataset,
        viewonly=True)

    # UserEvalResult owning the executable.
    user_eval_result = relationship(
        UserEvalResult,
        back_populates="executables")

    # Filename and digest of the generated executable.
    filename = Column(
        Filename,
        nullable=False)
    digest = Column(
        Digest,
        nullable=False)
