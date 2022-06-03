import base64
import datetime
import functools
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

import dateutil.parser
import voluptuous as vol  # type: ignore
from flask import Blueprint, g, request, send_file
from sqlalchemy.orm import joinedload
from werkzeug.local import LocalProxy

from aoiportal.auth_util import get_current_user, login_required
from aoiportal.cmsmirror.db import (  # type: ignore
    Announcement,
    Attachment,
    Contest,
    Dataset,
    File,
    LanguageTemplate,
    Meme,
    Message,
    Participation,
    Question,
    Statement,
    Submission,
    SubmissionResult,
    Task,
    User,
    UserEval,
    UserEvalFile,
    UserEvalResult,
    session,
)
from aoiportal.cmsmirror.util import (  # type: ignore
    STATIC_FILES_CACHE,
    USER_CACHE,
    create_file,
    open_digest,
    send_sub_to_evaluation_service,
    send_user_eval_to_evaluation_service,
)
from aoiportal.const import (
    KEY_CONTENT,
    KEY_FILENAME,
    KEY_FILES,
    KEY_INPUT,
    KEY_LANGUAGE,
    KEY_LAST_NOTIFICAITON,
    KEY_SUBJECT,
    KEY_TEXT,
)
from aoiportal.error import AOIBadRequest, AOIForbidden, AOINotFound
from aoiportal.utils import as_utc
from aoiportal.web_utils import json_api

_LOGGER = logging.getLogger(__name__)
cmsmirror_bp = Blueprint("cmsmirror", __name__)


def _get_participation() -> Participation:
    key = "cms_participation"
    if hasattr(g, key):
        return getattr(g, key)
    assert request.view_args is not None
    contest_name = request.view_args["contest_name"]
    cu = get_current_user()
    assert cu is not None
    part = (
        session.query(Participation)
        .join(Participation.contest)
        .filter(Contest.name == contest_name)
        .join(Participation.user)
        .filter(User.id == cu.cms_id)
        .options(joinedload(Participation.contest))
        .options(joinedload(Participation.user))
        .first()
    )
    if part is None:
        raise AOINotFound("Contest not found")
    if not part.contest.allow_frontendv2:
        raise AOINotFound("Contest not found")
    setattr(g, key, part)
    return part


def _get_task() -> Task:
    key = "cms_task"
    if hasattr(g, key):
        return getattr(g, key)
    assert request.view_args is not None
    task_name = request.view_args["task_name"]
    task: Optional[Task] = (
        session.query(Task)
        .filter(Task.contest_id == current_contest.id)
        .filter(Task.name == task_name)
        .options(joinedload(Task.statements))
        .options(joinedload(Task.attachments))
        .options(joinedload(Task.active_dataset))
        .first()
    )
    if task is None:
        raise AOINotFound("Task not found")
    setattr(g, key, task)
    return task


current_participation: Participation = LocalProxy(lambda: _get_participation())
current_contest: Contest = LocalProxy(lambda: current_participation.contest)
current_task: Task = LocalProxy(lambda: _get_task())


def active_contest_required(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        now = datetime.datetime.utcnow()
        if current_contest.phase(now) not in (0, 2):
            raise AOIForbidden("Contest is not active")
        return fn(*args, **kwargs)

    return wrapped


def _conv_announcement(ann: Announcement):
    return {
        "timestamp": as_utc(ann.timestamp).isoformat(),
        "subject": ann.subject,
        "text": ann.text,
        "task": ann.task.name if ann.task is not None else None,
    }


def _conv_message(msg: Message):
    return {
        "timestamp": as_utc(msg.timestamp).isoformat(),
        "subject": msg.subject,
        "text": msg.text,
        "task": msg.task.name if msg.task is not None else None,
    }


def _conv_question(q: Question):
    return {
        "timestamp": as_utc(q.question_timestamp).isoformat(),
        "subject": q.subject,
        "text": q.text,
        "reply": {
            "timestamp": as_utc(q.reply_timestamp).isoformat(),
            "subject": q.reply_subject,
            "text": q.reply_text,
        }
        if q.reply_timestamp is not None
        else None,
        "task": q.task.name if q.task is not None else None,
    }


@cmsmirror_bp.route("/api/cms/<contest_name>")
@login_required
@json_api()
def get_contest(contest_name: str):
    part = current_participation
    contest = current_contest
    ret = {
        "name": contest.name,
        "description": contest.description,
        "start": as_utc(contest.start).isoformat(),
        "stop": as_utc(contest.stop).isoformat(),
        "analysis": {
            "start": as_utc(contest.analysis_start).isoformat(),
            "stop": as_utc(contest.analysis_stop).isoformat(),
        }
        if contest.analysis_enabled
        else None,
        "is_active": False,
        "announcements": [_conv_announcement(ann) for ann in contest.announcements],
        "messages": [_conv_message(msg) for msg in part.messages],
        "questions": [_conv_question(q) for q in part.questions],
    }
    now = datetime.datetime.utcnow()
    if 0 <= contest.phase(now) <= 2:
        ret.update(
            {
                "tasks": [
                    {
                        "name": task.name,
                        "title": task.title,
                    }
                    for task in contest.tasks
                ],
                "languages": contest.languages,
                "is_active": True,
            }
        )
    return ret


def dump_submission(
    sub: Submission, res: Optional[SubmissionResult], *, detailed: bool
):
    base = {
        "uuid": sub.uuid,
        "timestamp": as_utc(sub.timestamp).isoformat(),
        "language": sub.language,
        "files": [
            {
                "filename": f.filename,
                "digest": f.digest,
            }
            for f in sub.files.values()
        ],
        "official": sub.official,
    }
    if res is None:
        status = SubmissionResult.COMPILING
        meme_digest = None
    else:
        status = res.get_status()
        meme_digest = res.meme.digest if res.meme is not None else None
    res_dct = base["result"] = {
        "status": {
            SubmissionResult.COMPILING: "compiling",
            SubmissionResult.COMPILATION_FAILED: "compilation_failed",
            SubmissionResult.EVALUATING: "evaluating",
            SubmissionResult.SCORING: "scoring",
            SubmissionResult.SCORED: "scored",
        }[status],
        "meme_digest": meme_digest,
    }

    if status == SubmissionResult.SCORED:
        assert res is not None
        res_dct["score"] = res.score
        if res.score_details and "max_score" in res.score_details[0]:
            res_dct["subtasks"] = [
                {
                    "max_score": st["max_score"],
                    "score_fraction": st["score_fraction"],
                }
                for st in res.score_details
            ]

    if detailed:
        if status in [
            SubmissionResult.COMPILATION_FAILED,
            SubmissionResult.EVALUATING,
            SubmissionResult.SCORING,
            SubmissionResult.SCORED,
        ]:
            res_dct.update(
                {
                    "compilation_text": res.compilation_text[0],  # COMPILATION_MESSAGES
                    "compilation_stdout": res.compilation_stdout,
                    "compilation_stderr": res.compilation_stderr,
                    "compilation_time": res.compilation_time,
                    "compilation_wall_clock_time": res.compilation_wall_clock_time,
                    "compilation_memory": res.compilation_memory,
                }
            )

        if status == SubmissionResult.SCORED:
            res_dct["score"] = res.score
            if not res.score_details or "max_score" not in res.score_details[0]:
                res_dct["testcases"] = [
                    {
                        "text": tc["text"],
                        "time": tc["time"],
                        "memory": tc["memory"],
                        "outcome": tc["outcome"],
                    }
                    for tc in res.score_details
                ]
            else:
                res_dct["subtasks"] = [
                    {
                        "max_score": st["max_score"],
                        "score_fraction": st["score_fraction"],
                        "testcases": [
                            {
                                "text": tc["text"],
                                "time": tc["time"],
                                "memory": tc["memory"],
                                "outcome": tc["outcome"],
                            }
                            for tc in st["testcases"]
                        ],
                    }
                    for st in res.score_details
                ]

    return base


EXT_TO_LANGUAGES: Dict[str, List[str]] = {
    ".c": ["C11 / gcc"],
    ".cpp": ["C++20 / g++", "C++17 / g++", "C++14 / g++", "C++11 / g++"],
    ".cc": ["C++20 / g++", "C++17 / g++", "C++14 / g++", "C++11 / g++"],
    ".cxx": ["C++20 / g++", "C++17 / g++", "C++14 / g++", "C++11 / g++"],
    ".c++": ["C++20 / g++", "C++17 / g++", "C++14 / g++", "C++11 / g++"],
    ".C": ["C++20 / g++", "C++17 / g++", "C++14 / g++", "C++11 / g++"],
    ".cs": ["C# / Mono"],
    ".hs": ["Haskell / ghc"],
    ".java": ["Java / JDK"],
    ".py": ["Python 3 / CPython", "Python 3 / PyPy", "Python 2 / CPython"],
    ".rs": ["Rust"],
    ".kt": ["Kotlin"],
    ".js": ["Javascript"],
    ".ts": ["Typescript"],
    ".go": ["Go"],
}


@cmsmirror_bp.route("/api/cms/<contest_name>/task/<task_name>")
@login_required
@active_contest_required
@json_api()
def get_task(contest_name: str, task_name: str):
    part = current_participation
    task = current_task
    ds: Dataset = task.active_dataset
    submissions: List[Tuple[Submission, Optional[SubmissionResult]]] = (
        session.query(Submission, SubmissionResult)
        .filter(Submission.participation_id == part.id)
        .filter(Submission.task_id == task.id)
        .outerjoin(
            Submission.results.and_(
                SubmissionResult.dataset_id == current_task.active_dataset_id
            )
        )
        .options(joinedload(Submission.files))
        .options(joinedload(SubmissionResult.meme))
        .all()
    )

    if ds.score_type == "Sum":
        scoring = {
            "type": "sum",
            "score_per_testcase": ds.score_type_parameters,
            "num_testcases": len(ds.testcases),
        }
        max_score = ds.score_type_parameters * len(ds.testcases)
    else:
        scoring = {
            "type": {
                "GroupMin": "group_min",
                "GroupMul": "group_mul",
                "GroupThreshold": "group_threshold",
            }[ds.score_type],
            "subtasks": [p for p, _ in ds.score_type_parameters],
        }
        max_score = sum(p for p, _ in ds.score_type_parameters)

    score = 0.0
    score_subtasks = None

    if task.score_mode == "max":
        score = max(
            [res.score for _, res in submissions if res is not None and res.scored()],
            default=0.0,
        )
    elif task.score_mode == "max_subtask":
        sub_scores: Dict[int, float] = {}
        for sub, res in submissions:
            if not sub.official or res is None or not res.scored():
                continue
            if not res.score_details or "max_score" not in res.score_details[0]:
                temp = {1: res.score}
            else:
                temp = {
                    st["idx"]: st["score_fraction"] * st["max_score"]
                    for st in res.score_details
                }
            for k, v in temp.items():
                sub_scores[k] = max(sub_scores.get(k, 0.0), v)

        score = sum(sub_scores.values())
        score_subtasks = [sub_scores[idx] for idx in sorted(sub_scores)]

    language_templates = {}
    for lt in ds.language_templates.values():
        langs = EXT_TO_LANGUAGES.get(Path(lt.filename).suffix, [])
        for lang in langs:
            if lang in task.contest.languages:
                language_templates[lang] = {
                    "filename": lt.filename,
                    "digest": lt.digest,
                }

    return {
        "name": task.name,
        "title": task.title,
        "languages": task.contest.languages,
        "feedback_level": task.feedback_level,
        "statements": [
            {
                "language": stmt.language,
                "digest": stmt.digest,
            }
            for stmt in task.statements.values()
        ],
        "attachments": [
            {
                "filename": att.filename,
                "digest": att.digest,
            }
            for att in task.attachments.values()
        ],
        "time_limit": ds.time_limit,
        "memory_limit": ds.memory_limit,
        "task_type": {
            "Batch": "batch",
            "Communication": "communication",
            "Ojuz": "ojuz",
            "OutputOnly": "output_only",
            "TwoSteps": "two_steps",
        }[ds.task_type],
        "scoring": scoring,
        "submissions": [
            dump_submission(sub, res, detailed=False) for sub, res in submissions
        ],
        "score": score,
        "max_score": max_score,
        "score_precision": task.score_precision,
        "score_mode": task.score_mode,
        "score_subtasks": score_subtasks,
        "submission_format": task.submission_format,
        "language_templates": language_templates,
        "announcements": [_conv_announcement(ann) for ann in task.announcements],
        "messages": [
            _conv_message(msg) for msg in part.messages if msg.task_id == task.id
        ],
        "questions": [
            _conv_question(q) for q in part.questions if q.task_id == task.id
        ],
    }


@cmsmirror_bp.route(
    "/api/cms/<contest_name>/task/<task_name>/submission/<submission_uuid>"
)
@login_required
@active_contest_required
@json_api()
def get_submission(contest_name: str, task_name: str, submission_uuid: str):
    q: Optional[Tuple[Submission, Optional[SubmissionResult]]] = (
        session.query(Submission, SubmissionResult)
        .filter(Submission.task_id == current_task.id)
        .filter(Submission.uuid == submission_uuid)
        .filter(Submission.participation_id == current_participation.id)
        .outerjoin(
            Submission.results.and_(
                SubmissionResult.dataset_id == current_task.active_dataset_id
            )
        )
        .options(joinedload(Submission.files))
        .options(joinedload(SubmissionResult.meme))
        .first()
    )
    if q is None:
        raise AOINotFound("Submission not found.")

    return dump_submission(q[0], q[1], detailed=True)


@cmsmirror_bp.route(
    "/api/cms/<contest_name>/task/<task_name>/submission/<submission_uuid>/short"
)
@login_required
@active_contest_required
@json_api()
def get_submission_short(contest_name: str, task_name: str, submission_uuid: str):
    q: Optional[Tuple[Submission, Optional[SubmissionResult]]] = (
        session.query(Submission, SubmissionResult)
        .filter(Submission.task_id == current_task.id)
        .filter(Submission.uuid == submission_uuid)
        .filter(Submission.participation_id == current_participation.id)
        .outerjoin(
            Submission.results.and_(
                SubmissionResult.dataset_id == current_task.active_dataset_id
            )
        )
        .options(joinedload(Submission.files))
        .first()
    )
    if q is None:
        raise AOINotFound("Submission not found.")

    return dump_submission(q[0], q[1], detailed=False)


@cmsmirror_bp.route(
    "/api/cms/<contest_name>/task/<task_name>/submission/<submission_uuid>/meme"
)
@login_required
@active_contest_required
def get_submission_meme(contest_name: str, task_name: str, submission_uuid: str):
    q: Optional[Meme] = (
        session.query(Meme)
        .join(Meme.submission_results)
        .join(SubmissionResult.submission)
        .filter(Submission.task_id == current_task.id)
        .filter(Submission.uuid == submission_uuid)
        .filter(Submission.participation_id == current_participation.id)
        .filter(SubmissionResult.dataset_id == current_task.active_dataset_id)
        .first()
    )
    if q is None:
        raise AOINotFound("Meme not found.")

    fh = open_digest(q.digest, cache=STATIC_FILES_CACHE)
    resp = send_file(fh, download_name=f"meme{Path(q.filename).suffix}")
    resp.headers["Cache-Control"] = "private, max-age=604800"
    return resp


@cmsmirror_bp.route("/api/cms/<contest_name>/task/<task_name>/statements/<language>")
@login_required
@active_contest_required
def get_statement(contest_name: str, task_name: str, language: str):
    stmt: Optional[Statement] = (
        session.query(Statement)
        .filter(Statement.task_id == current_task.id)
        .filter(Statement.language == language)
        .first()
    )
    if stmt is None:
        raise AOINotFound("Statement not found")
    fh = open_digest(stmt.digest, cache=STATIC_FILES_CACHE)
    resp = send_file(fh, download_name=f"{stmt.task.name} ({language}).pdf")
    resp.headers["Cache-Control"] = "private, max-age=604800"
    return resp


@cmsmirror_bp.route("/api/cms/<contest_name>/task/<task_name>/attachments/<filename>")
@login_required
@active_contest_required
def get_attachment(contest_name: str, task_name: str, filename: str):
    att: Optional[Attachment] = (
        session.query(Attachment)
        .filter(Attachment.task_id == current_task.id)
        .filter(Attachment.filename == filename)
        .first()
    )
    if att is None:
        raise AOINotFound("Attachment not found")
    fh = open_digest(att.digest, cache=STATIC_FILES_CACHE)
    resp = send_file(fh, download_name=att.filename)
    resp.headers["Cache-Control"] = "private, max-age=604800"
    return resp


@cmsmirror_bp.route(
    "/api/cms/<contest_name>/task/<task_name>/language-template/<filename>"
)
@login_required
@active_contest_required
def get_language_template(contest_name: str, task_name: str, filename: str):
    lt: Optional[LanguageTemplate] = (
        session.query(LanguageTemplate)
        .filter(LanguageTemplate.dataset_id == current_task.active_dataset_id)
        .filter(LanguageTemplate.filename == filename)
        .first()
    )
    if lt is None:
        raise AOINotFound("Language template not found")
    fh = open_digest(lt.digest, cache=STATIC_FILES_CACHE)
    resp = send_file(fh, download_name=lt.filename)
    resp.headers["Cache-Control"] = "private, max-age=604800"
    return resp


@cmsmirror_bp.route(
    "/api/cms/<contest_name>/task/<task_name>/submission/<submission_uuid>/files/<filename>"
)
@login_required
@active_contest_required
def get_submission_file(
    contest_name: str, task_name: str, submission_uuid: str, filename: str
):
    sub: Optional[Submission] = (
        session.query(Submission)
        .filter(Submission.task_id == current_task.id)
        .filter(Submission.uuid == submission_uuid)
        .filter(Submission.participation_id == current_participation.id)
        .first()
    )
    if sub is None:
        raise AOINotFound("Submission not found")
    file: Optional[File] = (
        session.query(File)
        .filter(File.submission_id == sub.id)
        .filter(File.filename == filename)
        .first()
    )
    if file is None:
        raise AOINotFound("File not found")
    fh = open_digest(file.digest, cache=USER_CACHE)
    resp = send_file(fh, download_name=file.filename)
    resp.headers["Cache-Control"] = "private, max-age=604800"
    return resp


@cmsmirror_bp.route("/api/cms/<contest_name>/question", methods=["POST"])
@login_required
@active_contest_required
@json_api(
    {
        vol.Required(KEY_SUBJECT): str,
        vol.Required(KEY_TEXT): str,
    }
)
def post_question(data, contest_name: str):
    part: Participation = current_participation
    q = Question(
        question_timestamp=datetime.datetime.utcnow(),
        subject=data[KEY_SUBJECT],
        text=data[KEY_TEXT],
        participation_id=part.id,
    )
    session.add(q)
    session.commit()
    return {"success": True}


@cmsmirror_bp.route(
    "/api/cms/<contest_name>/task/<task_name>/question", methods=["POST"]
)
@login_required
@active_contest_required
@json_api(
    {
        vol.Required(KEY_SUBJECT): str,
        vol.Required(KEY_TEXT): str,
    }
)
def post_question_task(data, contest_name: str, task_name: str):
    part: Participation = current_participation
    q = Question(
        question_timestamp=datetime.datetime.utcnow(),
        subject=data[KEY_SUBJECT],
        text=data[KEY_TEXT],
        participation_id=part.id,
        task_id=current_task.id,
    )
    session.add(q)
    session.commit()
    return {"success": True}


def _base64_content(value: str):
    try:
        base64.b64decode(value, validate=True)
        return value
    except ValueError:
        raise vol.Invalid("Not valid base64")


@cmsmirror_bp.route("/api/cms/<contest_name>/task/<task_name>/submit", methods=["POST"])
@login_required
@active_contest_required
@json_api(
    {
        vol.Required(KEY_LANGUAGE): str,
        vol.Required(KEY_FILES): [
            {
                vol.Required(KEY_FILENAME): str,
                vol.Required(KEY_CONTENT): vol.All(str, _base64_content),
            }
        ],
    }
)
def submit(data, contest_name: str, task_name: str):
    allow_partial = current_task.active_dataset.task_type == "OutputOnly"
    expected_format = set(current_task.submission_format)
    set_format = set(x[KEY_FILENAME] for x in data[KEY_FILES])
    if not allow_partial and (expected_format - set_format):
        raise AOIBadRequest("At least one file missing.")
    if set_format - expected_format:
        raise AOIBadRequest("At least one file doesn't match submission format.")
    if data[KEY_LANGUAGE] not in current_contest.languages:
        raise AOIBadRequest("Language not allowed.")
    now = datetime.datetime.utcnow()
    sub = Submission(
        uuid=str(uuid4()),
        participation_id=current_participation.id,
        task_id=current_task.id,
        timestamp=now,
        language=data[KEY_LANGUAGE],
        official=current_contest.phase(now) == 0,
    )
    session.add(sub)
    for file in data[KEY_FILES]:
        fname = file[KEY_FILENAME]
        content = base64.b64decode(file[KEY_CONTENT])
        descr = f"Submission file {fname} from {current_participation.user.username} and task {current_task.name}"
        f = File(
            submission=sub,
            filename=fname,
            digest=create_file(content, descr),
        )
        session.add(f)
    session.commit()

    try:
        send_sub_to_evaluation_service(sub.id)
    except Exception:
        _LOGGER.warning("Failed to send submission to evaluation service")

    return {
        "success": True,
        "uuid": sub.uuid,
        "submission": dump_submission(sub, None, detailed=False),
    }


@cmsmirror_bp.route("/api/cms/<contest_name>/task/<task_name>/eval", methods=["POST"])
@login_required
@active_contest_required
@json_api(
    {
        vol.Required(KEY_LANGUAGE): str,
        vol.Required(KEY_FILES): [
            {
                vol.Required(KEY_FILENAME): str,
                vol.Required(KEY_CONTENT): vol.All(str, _base64_content),
            }
        ],
        vol.Required(KEY_INPUT): vol.All(str, _base64_content),
    }
)
def user_eval(data, contest_name: str, task_name: str):
    now = datetime.datetime.utcnow()
    ueval = UserEval(
        uuid=str(uuid4()),
        participation_id=current_participation.id,
        task_id=current_task.id,
        timestamp=now,
        language=data[KEY_LANGUAGE],
        input=create_file(
            base64.b64decode(data[KEY_INPUT]),
            f"Input for user eval from {current_participation.user.username}",
        ),
    )
    session.add(ueval)
    for file in data[KEY_FILES]:
        fname = file[KEY_FILENAME]
        content = base64.b64decode(file[KEY_CONTENT])
        descr = f"User eval file {fname} from {current_participation.user.username} and task {current_task.name}"
        f = UserEvalFile(
            user_eval=ueval,
            filename=fname,
            digest=create_file(content, descr),
        )
        session.add(f)
    session.commit()

    try:
        send_user_eval_to_evaluation_service(ueval.id)
    except Exception:
        _LOGGER.warning("Failed to send submission to evaluation service")

    return {
        "success": True,
        "uuid": ueval.uuid,
    }


@cmsmirror_bp.route(
    "/api/cms/<contest_name>/task/<task_name>/user-eval/<user_eval_uuid>"
)
@login_required
@active_contest_required
@json_api()
def get_usereval(contest_name: str, task_name: str, user_eval_uuid: str):
    q: Optional[Tuple[UserEval, Optional[UserEvalResult]]] = (
        session.query(UserEval, UserEvalResult)
        .filter(UserEval.task_id == current_task.id)
        .filter(UserEval.uuid == user_eval_uuid)
        .filter(UserEval.participation_id == current_participation.id)
        .outerjoin(
            UserEval.results.and_(
                UserEvalResult.dataset_id == current_task.active_dataset_id
            )
        )
        .first()
    )
    if q is None:
        raise AOINotFound("User eval not found.")
    ue: UserEval = q[0]
    res: UserEvalResult = q[1]

    base = {
        "uuid": ue.uuid,
        "timestamp": as_utc(ue.timestamp).isoformat(),
        "language": ue.language,
        "files": [f.filename for f in ue.files.values()],
    }
    status = UserEvalResult.COMPILING if res is None else res.get_status()
    res_dct = base["result"] = {
        "status": {
            UserEvalResult.COMPILING: "compiling",
            UserEvalResult.COMPILATION_FAILED: "compilation_failed",
            UserEvalResult.EVALUATING: "evaluating",
            UserEvalResult.EVALUATED: "evaluated",
        }[status],
    }

    if status in [
        UserEvalResult.COMPILATION_FAILED,
        UserEvalResult.EVALUATING,
        UserEvalResult.EVALUATED,
    ]:
        res_dct.update(
            {
                "compilation_text": res.compilation_text[0],  # COMPILATION_MESSAGES
                "compilation_stdout": res.compilation_stdout,
                "compilation_stderr": res.compilation_stderr,
                "compilation_time": res.compilation_time,
                "compilation_wall_clock_time": res.compilation_wall_clock_time,
                "compilation_memory": res.compilation_memory,
            }
        )

    if status == UserEvalResult.EVALUATED:
        res_dct["execution_time"] = res.execution_time
        res_dct["execution_wall_clock_time"] = res.execution_wall_clock_time
        res_dct["execution_memory"] = res.execution_memory
        res_dct["evaluation_outcome"] = res.evaluation_outcome
        res_dct["evaluation_text"] = res.evaluation_text
        if res.output is not None:
            with open_digest(res.output) as fh:
                output = fh.read()
            res_dct["output"] = base64.b64encode(output).decode()

    return base


def _check_dt_isoformat(value):
    if not isinstance(value, str):
        raise vol.Invalid("Datetime must be string")
    try:
        dateutil.parser.isoparse(value)
    except ValueError:
        raise vol.Invalid("Not a valid ISO 8601 datetime")
    return value


@cmsmirror_bp.route("/api/cms/<contest_name>/check-notifications", methods=["POST"])
@login_required
@json_api({vol.Optional(KEY_LAST_NOTIFICAITON): _check_dt_isoformat})
def check_notifications(data, contest_name: str):
    if KEY_LAST_NOTIFICAITON in data:
        last_notification = as_utc(
            dateutil.parser.isoparse(data[KEY_LAST_NOTIFICAITON])
        )
    else:
        last_notification = as_utc(datetime.datetime.utcfromtimestamp(0))
    new_announcements = (
        session.query(Announcement)
        .filter(Announcement.contest_id == current_contest.id)
        .filter(Announcement.timestamp > last_notification.isoformat())
        .all()
    )
    new_messages = (
        session.query(Message)
        .join(Message.participation)
        .filter(Message.participation_id == current_participation.id)
        .filter(Participation.contest_id == current_contest.id)
        .filter(Message.timestamp > last_notification.isoformat())
        .all()
    )
    new_replies = (
        session.query(Question)
        .join(Question.participation)
        .filter(Question.participation_id == current_participation.id)
        .filter(Participation.contest_id == current_contest.id)
        .filter(Question.reply_timestamp > last_notification.isoformat())
        .all()
    )
    return {
        "new_announcements": [_conv_announcement(ann) for ann in new_announcements],
        "new_messages": [_conv_message(msg) for msg in new_messages],
        "new_replies": [_conv_question(q) for q in new_replies],
    }
