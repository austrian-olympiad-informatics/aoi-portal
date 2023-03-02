import collections
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

import voluptuous as vol
from flask import Blueprint, g, jsonify, request, send_file
from sqlalchemy import func
from sqlalchemy.orm import Load, Query, joinedload, selectinload
from werkzeug.local import LocalProxy

from aoiportal.auth_util import admin_required, get_current_user
from aoiportal.cmsmirror import scores
from aoiportal.cmsmirror.const import KEY_HIDDEN
from aoiportal.cmsmirror.db import (
    Contest,
    Dataset,
    Participation,
    SubtaskScore,
    Task,
    User,
    UserEval,
    UserEvalResult,
    session,
)
from aoiportal.cmsmirror.db.contest import Announcement
from aoiportal.cmsmirror.db.submission import Meme, Submission, SubmissionResult
from aoiportal.cmsmirror.db.user import Message, Question
from aoiportal.cmsmirror.util import open_digest, paginate
from aoiportal.const import KEY_CONTEST_ID, KEY_PARTICIPATION_ID, KEY_TASK_ID
from aoiportal.error import AOIBadRequest, AOINotFound
from aoiportal.utils import as_utc
from aoiportal.web_utils import json_api

cmsadmin_bp = Blueprint("cmsadmin", __name__)


def _get_contest() -> Contest:
    key = "cms_contest"
    if hasattr(g, key):
        return getattr(g, key)
    assert request.view_args is not None
    contest_id = request.view_args["contest_id"]
    contest = session.query(Contest).filter(Contest.id == contest_id).first()
    if contest is None:
        raise AOINotFound("Contest not found")
    setattr(g, key, contest)
    return contest


current_contest: Contest = LocalProxy(lambda: _get_contest())


def _dump_task_short(task: Task):
    return {
        "id": task.id,
        "name": task.name,
        "title": task.title,
    }


def _dump_meme(meme: Meme):
    return {
        "id": meme.id,
        "filename": meme.filename,
        "digest": meme.digest,
        "min_score": meme.min_score,
        "max_score": meme.max_score,
        "factor": meme.factor,
        "task": _dump_task_short(meme.task) if meme.task is not None else None,
    }


def _dump_contest(contest: Contest):
    return {
        "id": contest.id,
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
        "tasks": [_dump_task_short(task) for task in contest.tasks],
        "score_precision": contest.score_precision,
        "languages": contest.languages,
        "allow_frontendv2": contest.allow_frontendv2,
    }


@cmsadmin_bp.route("/api/cms/admin/contests")
@admin_required
@json_api()
def get_contests():
    contests = session.query(Contest).order_by(Contest.id.desc()).all()
    return [_dump_contest(c) for c in contests]


@cmsadmin_bp.route("/api/cms/admin/contest/<int:contest_id>")
@admin_required
@json_api()
def get_contest(contest_id: int):
    return _dump_contest(current_contest)


def _dump_announcement(ann: Announcement):
    return {
        "id": ann.id,
        "timestamp": as_utc(ann.timestamp).isoformat(),
        "subject": ann.subject,
        "text": ann.text,
        "task": _dump_task_short(ann.task) if ann.task is not None else None,
    }


@cmsadmin_bp.route("/api/cms/admin/contest/<int:contest_id>/announcements")
@admin_required
@json_api()
def get_contest_announcements(contest_id: int):
    return [_dump_announcement(ann) for ann in current_contest.announcements]


def _dump_participation_short(p: Participation):
    return {
        "id": p.id,
        "user": {
            "id": p.user.id,
            "first_name": p.user.first_name,
            "last_name": p.user.last_name,
            "username": p.user.username,
        },
        "hidden": p.hidden,
    }


def _dump_contest_short(c: Contest):
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
    }


def _dump_question(q: Question):
    return {
        "id": q.id,
        "timestamp": as_utc(q.question_timestamp).isoformat(),
        "subject": q.subject,
        "text": q.text,
        "task": _dump_task_short(q.task) if q.task is not None else None,
        "ignored": q.ignored,
        "reply": {
            "timestamp": as_utc(q.reply_timestamp).isoformat(),
            "subject": q.reply_subject,
            "text": q.reply_text,
        }
        if q.reply_timestamp is not None
        else None,
        "participation": _dump_participation_short(q.participation),
    }


def _dump_message(msg: Message):
    return {
        "id": msg.id,
        "timestamp": as_utc(msg.timestamp).isoformat(),
        "subject": msg.subject,
        "text": msg.text,
        "task": _dump_task_short(msg.task) if msg.task is not None else None,
        "participation": _dump_participation_short(msg.participation),
    }


@cmsadmin_bp.route("/api/cms/admin/contest/<int:contest_id>/questions")
@admin_required
@json_api()
def get_contest_questions(contest_id: int):
    questions: List[Question] = (
        session.query(Question)
        .join(Question.participation)
        .filter(Participation.contest_id == current_contest.id)
        .order_by(Question.question_timestamp.desc())
        .options(joinedload(Participation.user))
        .all()
    )
    return [_dump_question(q) for q in questions]


@cmsadmin_bp.route("/api/cms/admin/contest/<int:contest_id>/messages")
@admin_required
@json_api()
def get_contest_messages(contest_id: int):
    messages: List[Message] = (
        session.query(Message)
        .join(Message.participation)
        .filter(Participation.contest_id == current_contest.id)
        .order_by(Message.timestamp.desc())
        .options(joinedload(Participation.user))
        .all()
    )
    return [_dump_message(msg) for msg in messages]


def dump_submission(
    sub: Submission,
    res: Optional[SubmissionResult],
    *,
    detailed: bool = False,
):
    base = {
        "id": sub.id,
        "uuid": sub.uuid,
        "timestamp": as_utc(sub.timestamp).isoformat(),
        "language": sub.language,
        "official": sub.official,
        "comment": sub.comment,
    }

    base["participation"] = _dump_participation_short(sub.participation)
    base["contest"] = _dump_contest_short(sub.task.contest)
    base["task"] = _dump_task_short(sub.task)

    if res is None:
        status = SubmissionResult.COMPILING
        meme_digest = None
    else:
        status = res.get_status()
        meme_digest = res.meme.digest if res.meme is not None else None

        ds = res.dataset
        if ds.score_type == "Sum":
            max_score = ds.score_type_parameters * len(ds.testcases)
        else:
            max_score = sum(p for p, _ in ds.score_type_parameters)
        base["max_score"] = max_score
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
        res_dct["score_precision"] = sub.task.score_precision
        if res.score_details and "max_score" in res.score_details[0]:
            res_dct["subtasks"] = [
                {
                    "max_score": st["max_score"],
                    "fraction": st["score_fraction"],
                }
                for st in res.score_details
            ]

    if detailed:
        base["files"] = [
            {
                "filename": f.filename,
                "digest": f.digest,
            }
            for f in sub.files.values()
        ]

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
                    "compilation_memory": res.compilation_memory,
                    "compilation_wall_clock_time": res.compilation_wall_clock_time,
                    "compilation_tries": res.compilation_tries,
                    "compilation_shard": res.compilation_shard,
                    "compilation_sandbox": res.compilation_sandbox,
                    "executables": [
                        {
                            "id": exe.id,
                            "filename": exe.filename,
                            "digest": exe.digest,
                        }
                        for exe in res.executables.values()
                    ],
                }
            )

        if status in [SubmissionResult.SCORING, SubmissionResult.SCORED]:
            res_dct.update(
                {
                    "evaluation_tries": res.evaluation_tries,
                    "evaluations": [
                        {
                            "id": ev.id,
                            "testcase": {
                                "id": ev.testcase.id,
                                "codename": ev.testcase.codename,
                                "public": ev.testcase.public,
                                "input_digest": ev.testcase.input,
                                "output_digest": ev.testcase.output,
                            },
                            "outcome": ev.outcome,
                            "text": ev.text,
                            "execution_time": ev.execution_time,
                            "execution_wall_clock_time": ev.execution_wall_clock_time,
                            "execution_memory": ev.execution_memory,
                            "evaluation_shard": ev.evaluation_shard,
                            "evaluation_sandbox": ev.evaluation_sandbox,
                        }
                        for ev in sorted(
                            res.evaluations, key=lambda ev: ev.testcase.codename
                        )
                    ],
                }
            )

        if status == SubmissionResult.SCORED:
            res_dct.update(
                {
                    "score": res.score,
                    "evaluation_tries": res.evaluation_tries,
                    "score_details": res.score_details,
                }
            )
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
                        "fraction": st["score_fraction"],
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


def dump_user_eval(
    eva: UserEval,
    res: Optional[UserEvalResult],
    *,
    detailed: bool = False,
):
    base = {
        "id": eva.id,
        "uuid": eva.uuid,
        "timestamp": as_utc(eva.timestamp).isoformat(),
        "language": eva.language,
    }

    base["participation"] = _dump_participation_short(eva.participation)
    base["contest"] = _dump_contest_short(eva.task.contest)
    base["task"] = _dump_task_short(eva.task)

    if res is None:
        status = UserEvalResult.COMPILING
    else:
        status = res.get_status()
    res_dct = base["result"] = {
        "status": {
            UserEvalResult.COMPILING: "compiling",
            UserEvalResult.COMPILATION_FAILED: "compilation_failed",
            UserEvalResult.EVALUATING: "evaluating",
            UserEvalResult.EVALUATED: "evaluated",
        }[status],
    }

    if detailed:
        base["input_digest"] = eva.input
        base["files"] = [
            {
                "filename": f.filename,
                "digest": f.digest,
            }
            for f in eva.files.values()
        ]

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
                    "compilation_memory": res.compilation_memory,
                    "compilation_wall_clock_time": res.compilation_wall_clock_time,
                    "compilation_tries": res.compilation_tries,
                    "compilation_shard": res.compilation_shard,
                    "compilation_sandbox": res.compilation_sandbox,
                    "executables": [
                        {
                            "id": exe.id,
                            "filename": exe.filename,
                            "digest": exe.digest,
                        }
                        for exe in res.executables.values()
                    ],
                }
            )

        if status in [UserEvalResult.EVALUATED]:
            res_dct.update(
                {
                    "evaluation_tries": res.evaluation_tries,
                    "execution_time": res.execution_time,
                    "execution_wall_clock_time": res.execution_wall_clock_time,
                    "execution_memory": res.execution_memory,
                    "evaluation_shard": res.evaluation_shard,
                    "evaluation_sandbox": res.evaluation_sandbox,
                    "output_digest": res.output,
                }
            )

    return base


def _get_submissions(
    contest_id: Optional[int] = None,
    task_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    q = (
        session.query(Submission, SubmissionResult, Participation)
        .join(Submission.task)
        .join(Submission.participation)
        .outerjoin(
            Submission.results.and_(
                SubmissionResult.dataset_id == Task.active_dataset_id
            )
        )
        .options(
            Load(Submission).load_only(
                Submission.id,
                Submission.uuid,
                Submission.timestamp,
                Submission.language,
                Submission.official,
            ),
            Load(SubmissionResult).load_only(
                SubmissionResult.submission_id,
                SubmissionResult.dataset_id,
                SubmissionResult.compilation_outcome,
                SubmissionResult.score,
                SubmissionResult.score_details,
                SubmissionResult.compilation_outcome,
                SubmissionResult.evaluation_outcome,
            ),
            joinedload(SubmissionResult.meme),
            Load(Meme).load_only(
                Meme.id,
                Meme.filename,
                Meme.digest,
            ),
            selectinload(Submission.task),
            Load(Task).load_only(
                Task.id,
                Task.name,
                Task.title,
                Task.score_precision,
                Task.score_mode,
            ),
            selectinload(SubmissionResult.dataset),
            Load(Dataset).load_only(Dataset.score_type_parameters),
            Load(Participation).load_only(
                Participation.id,
                Participation.user_id,
            ),
            selectinload(Participation.contest),
            Load(Contest).load_only(
                Contest.id,
                Contest.name,
            ),
            joinedload(Participation.user),
            Load(User).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.username,
            ),
        )
        .order_by(Submission.timestamp.desc())
    )

    if contest_id is not None:
        q = q.filter(Task.contest_id == contest_id)

    if task_id is not None:
        q = q.filter(Task.id == task_id)

    if user_id is not None:
        q = q.filter(Participation.user_id == user_id)

    page = paginate(q)
    submissions: List[
        Tuple[Submission, Optional[SubmissionResult], Participation]
    ] = page.items

    return {
        "page": page.page,
        "per_page": page.per_page,
        "total": page.total,
        "items": [
            dump_submission(
                sub,
                res,
                detailed=False,
            )
            for sub, res, _ in submissions
        ],
    }


def _dump_task(task: Task, detailed: bool = False):
    ret = {
        "id": task.id,
        "name": task.name,
        "title": task.title,
        "contest": _dump_contest_short(task.contest)
        if task.contest is not None
        else None,
    }
    if detailed:
        ret.update(
            {
                "statements": [
                    {
                        "id": stat.id,
                        "language": stat.language,
                        "digest": stat.digest,
                    }
                    for stat in task.statements.values()
                ],
                "attachments": [
                    {
                        "id": att.id,
                        "filename": att.filename,
                        "digest": att.digest,
                    }
                    for att in task.attachments.values()
                ],
                "submission_format": task.submission_format,
                "score_precision": task.score_precision,
                "score_mode": task.score_mode,
                "active_dataset": {
                    "id": task.active_dataset.id,
                    "time_limit": task.active_dataset.time_limit,
                    "memory_limit": task.active_dataset.memory_limit,
                    "task_type": task.active_dataset.task_type,
                    "task_type_parameters": task.active_dataset.task_type_parameters,
                    "score_type": task.active_dataset.score_type,
                    "score_type_parameters": task.active_dataset.score_type_parameters,
                    "managers": [
                        {
                            "id": man.id,
                            "filename": man.filename,
                            "digest": man.digest,
                        }
                        for man in task.active_dataset.managers.values()
                    ],
                    "testcases": [
                        {
                            "id": tc.id,
                            "codename": tc.codename,
                            "public": tc.public,
                            "input_digest": tc.input,
                            "output_digest": tc.output,
                        }
                        for tc in sorted(
                            task.active_dataset.testcases.values(),
                            key=lambda x: x.codename,
                        )
                    ],
                    "language_templates": [
                        {
                            "id": lt.id,
                            "filename": lt.filename,
                            "digest": lt.digest,
                        }
                        for lt in task.active_dataset.language_templates.values()
                    ],
                    "test_managers": [
                        {
                            "id": tm.id,
                            "filename": tm.filename,
                            "digest": tm.digest,
                        }
                        for tm in task.active_dataset.test_managers.values()
                    ],
                },
            }
        )
    return ret


@cmsadmin_bp.route("/api/cms/admin/contest/<int:contest_id>/tasks")
@admin_required
@json_api()
def get_contest_tasks(contest_id: int):
    return [_dump_task(task) for task in current_contest.tasks]


@cmsadmin_bp.route("/api/cms/admin/task/<int:task_id>")
@admin_required
@json_api()
def get_task(task_id: int):
    task = session.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise AOINotFound("Task not found")
    return _dump_task(task, detailed=True)


@cmsadmin_bp.route("/api/cms/admin/contest/<int:contest_id>/participations")
@admin_required
@json_api()
def get_contest_participations(contest_id: int):
    parts: List[Participation] = (
        session.query(Participation)
        .filter(Participation.contest_id == current_contest.id)
        .order_by(Participation.id.asc())
        .options(joinedload(Participation.user))
        .all()
    )
    return [_dump_participation_short(part) for part in parts]


@cmsadmin_bp.route("/api/cms/admin/contest/<int:contest_id>/ranking")
@admin_required
@json_api()
def get_contest_ranking(contest_id: int):
    contest_data = scores.get_contest_scores(current_contest.id)
    return {
        "tasks": [
            {
                "id": tid,
                "name": task.name,
                "title": task.title,
                "max_score": task.max_score,
                "subtask_max_scores": task.subtask_max_scores,
                "score_precision": task.score_precision,
            }
            for tid, task in contest_data.tasks.items()
        ],
        "score_precision": contest_data.score_precision,
        "results": [
            {
                "id": pid,
                "hidden": part.hidden,
                "score": part.score,
                "task_scores": [
                    {
                        "id": tid,
                        "score": task.score,
                        "subtask_scores": task.subtask_scores,
                        "num_submissions": task.num_submissions,
                    }
                    for tid, task in part.task_scores.items()
                ],
                "rank": part.rank,
            }
            for pid, part in contest_data.results.items()
        ],
    }


@cmsadmin_bp.route("/api/cms/admin/participation/<int:participation_id>")
@admin_required
@json_api()
def get_participation(participation_id: int):
    part: Optional[Participation] = (
        session.query(Participation)
        .filter(Participation.id == participation_id)
        .options(joinedload(Participation.user))
        .first()
    )
    if part is None:
        raise AOINotFound("Participation not found")
    return _dump_participation_short(part)


@cmsadmin_bp.route(
    "/api/cms/admin/participation/<int:participation_id>/update", methods=["PUT"]
)
@admin_required
@json_api(
    {
        vol.Optional(KEY_HIDDEN): bool,
    }
)
def update_participation(data, participation_id: int):
    part: Optional[Participation] = (
        session.query(Participation)
        .filter(Participation.id == participation_id)
        .first()
    )
    if part is None:
        raise AOINotFound("Participation not found")
    if KEY_HIDDEN in data:
        part.hidden = data[KEY_HIDDEN]
    session.commit()
    return {"success": True}


@cmsadmin_bp.route("/api/cms/admin/participation/<int:participation_id>/score")
@admin_required
@json_api()
def get_participation_score(participation_id: int):
    part: Optional[Participation] = (
        session.query(Participation)
        .filter(Participation.id == participation_id)
        .first()
    )
    if part is None:
        raise AOINotFound("Participation not found")
    contest_data = scores.get_contest_scores(part.contest_id)
    part_res = contest_data.results[participation_id]
    return {
        "score": part_res.score,
        "task_scores": [
            {
                "id": task_id,
                "score": task_res.score,
                "subtask_scores": task_res.subtask_scores,
                "num_submissions": task_res.num_submissions,
            }
            for task_id, task_res in part_res.task_scores.items()
        ],
        "rank": part_res.rank,
        "tasks": [
            {
                "id": tid,
                "name": task.name,
                "title": task.title,
                "max_score": task.max_score,
                "subtask_max_scores": task.subtask_max_scores,
                "score_precision": task.score_precision,
            }
            for tid, task in contest_data.tasks.items()
        ],
        "score_precision": contest_data.score_precision,
        "hidden": part_res.hidden,
    }


@cmsadmin_bp.route("/api/cms/admin/participation/<int:participation_id>/questions")
@admin_required
@json_api()
def get_participation_questions(participation_id: int):
    questions: List[Question] = (
        session.query(Question)
        .join(Question.participation)
        .filter(Participation.id == participation_id)
        .order_by(Question.question_timestamp.desc())
        .options(joinedload(Participation.user))
        .all()
    )
    return [_dump_question(q) for q in questions]


@cmsadmin_bp.route("/api/cms/admin/participation/<int:participation_id>/messages")
@admin_required
@json_api()
def get_participation_messages(participation_id: int):
    questions: List[Message] = (
        session.query(Message)
        .join(Message.participation)
        .filter(Message.id == participation_id)
        .order_by(Message.timestamp.desc())
        .options(joinedload(Participation.user))
        .all()
    )
    return [_dump_message(q) for q in questions]


@cmsadmin_bp.route("/api/cms/admin/submissions")
@admin_required
@json_api()
def get_all_submissions():
    contest_id = None
    if "contest_id" in request.args:
        try:
            contest_id = int(request.args["contest_id"])
        except (ValueError, TypeError):
            raise AOIBadRequest("Contest id invalid format")
        contest = session.query(Contest).filter(Contest.id == contest_id).first()
        if contest is None:
            raise AOINotFound("Task not found")

    task_id = None
    if "task_id" in request.args:
        try:
            task_id = int(request.args["task_id"])
        except (ValueError, TypeError):
            raise AOIBadRequest("Task id invalid format")
        task = session.query(Task).filter(Task.id == task_id).first()
        if task is None:
            raise AOINotFound("Task not found")

    user_id = None
    if "user_id" in request.args:
        try:
            user_id = int(request.args["user_id"])
        except (ValueError, TypeError):
            raise AOIBadRequest("User id invalid format")
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise AOINotFound("User not found")

    data = _get_submissions(
        contest_id=contest_id,
        task_id=task_id,
        user_id=user_id,
    )
    resp = jsonify(data)
    resp.add_etag()
    return resp.make_conditional(request)


@cmsadmin_bp.route("/api/cms/admin/user-evals")
@admin_required
@json_api()
def get_all_user_evals():
    contest_id = None
    if "contest_id" in request.args:
        try:
            contest_id = int(request.args["contest_id"])
        except (ValueError, TypeError):
            raise AOIBadRequest("Contest id invalid format")
        contest = session.query(Contest).filter(Contest.id == contest_id).first()
        if contest is None:
            raise AOINotFound("Task not found")

    task_id = None
    if "task_id" in request.args:
        try:
            task_id = int(request.args["task_id"])
        except (ValueError, TypeError):
            raise AOIBadRequest("Task id invalid format")
        task = session.query(Task).filter(Task.id == task_id).first()
        if task is None:
            raise AOINotFound("Task not found")

    user_id = None
    if "user_id" in request.args:
        try:
            user_id = int(request.args["user_id"])
        except (ValueError, TypeError):
            raise AOIBadRequest("User id invalid format")
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise AOINotFound("User not found")

    q = (
        session.query(UserEval, UserEvalResult, Participation)
        .join(UserEval.task)
        .join(UserEval.participation)
        .outerjoin(
            UserEval.results.and_(UserEvalResult.dataset_id == Task.active_dataset_id)
        )
        .options(
            Load(UserEval).load_only(
                UserEval.id,
                UserEval.uuid,
                UserEval.timestamp,
                UserEval.language,
            ),
            Load(UserEvalResult).load_only(
                UserEvalResult.user_eval_id,
                UserEvalResult.dataset_id,
                UserEvalResult.compilation_outcome,
                UserEvalResult.compilation_outcome,
                UserEvalResult.evaluation_outcome,
            ),
            selectinload(UserEval.task),
            Load(Task).load_only(
                Task.id,
                Task.name,
                Task.title,
                Task.score_precision,
                Task.score_mode,
            ),
            Load(Participation).load_only(
                Participation.id,
                Participation.user_id,
            ),
            selectinload(Participation.contest),
            Load(Contest).load_only(
                Contest.id,
                Contest.name,
            ),
            joinedload(Participation.user),
            Load(User).load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.username,
            ),
        )
        .order_by(UserEval.timestamp.desc())
    )

    if contest_id is not None:
        q = q.filter(Task.contest_id == contest_id)

    if task_id is not None:
        q = q.filter(Task.id == task_id)

    if user_id is not None:
        q = q.filter(Participation.user_id == user_id)

    page = paginate(q)
    user_evals: List[
        Tuple[UserEval, Optional[UserEvalResult], Participation]
    ] = page.items

    data = {
        "page": page.page,
        "per_page": page.per_page,
        "total": page.total,
        "items": [
            dump_user_eval(
                eva,
                res,
                detailed=False,
            )
            for eva, res, _ in user_evals
        ],
    }

    resp = jsonify(data)
    resp.add_etag()
    return resp.make_conditional(request)


@cmsadmin_bp.route("/api/cms/admin/submission/<submission_uuid>")
@admin_required
@json_api()
def get_submission(submission_uuid):
    q: Optional[Tuple[Submission, Optional[SubmissionResult]]] = (
        session.query(Submission, SubmissionResult)
        .filter(Submission.uuid == submission_uuid)
        .join(Submission.task)
        .outerjoin(
            Submission.results.and_(
                SubmissionResult.dataset_id == Task.active_dataset_id
            )
        )
        .options(
            joinedload(Submission.task),
            joinedload(Submission.participation),
            joinedload(Submission.files),
            joinedload(SubmissionResult.meme),
            joinedload(SubmissionResult.meme),
            joinedload(SubmissionResult.executables),
            selectinload(SubmissionResult.evaluations),
        )
        .first()
    )
    if q is None:
        raise AOINotFound("Submission not found")
    sub, res = q
    return dump_submission(
        sub,
        res,
        detailed=True,
    )


@cmsadmin_bp.route("/api/cms/admin/user-eval/<user_eval_uuid>")
@admin_required
@json_api()
def get_user_eval(user_eval_uuid):
    q: Optional[Tuple[UserEval, Optional[UserEvalResult]]] = (
        session.query(UserEval, UserEvalResult)
        .filter(UserEval.uuid == user_eval_uuid)
        .join(UserEval.task)
        .outerjoin(
            UserEval.results.and_(UserEvalResult.dataset_id == Task.active_dataset_id)
        )
        .options(
            joinedload(UserEval.task),
            joinedload(UserEval.participation),
            joinedload(UserEval.files),
            joinedload(UserEvalResult.executables),
        )
        .first()
    )
    if q is None:
        raise AOINotFound("User Eval not found")
    eva, res = q
    return dump_user_eval(
        eva,
        res,
        detailed=True,
    )


@cmsadmin_bp.route("/api/cms/admin/digest/<digest>")
@admin_required
@json_api()
def get_digest(digest):
    fh = open_digest(digest)
    resp = send_file(fh, download_name=f"data.bin")
    resp.headers["Cache-Control"] = "private, max-age=604800"
    return resp


@cmsadmin_bp.route("/api/cms/admin/memes")
@admin_required
@json_api()
def get_memes():
    memes: List[Meme] = session.query(Meme).options(joinedload(Meme.task)).all()
    return [_dump_meme(meme) for meme in memes]


@cmsadmin_bp.route("/api/cms/admin/meme/<int:meme_id>")
@admin_required
@json_api()
def get_meme(meme_id: int):
    meme: Optional[Meme] = (
        session.query(Meme)
        .filter(Meme.id == meme_id)
        .options(joinedload(Meme.task))
        .first()
    )
    if meme is None:
        raise AOINotFound("Meme not found")
    return _dump_meme(meme)


@cmsadmin_bp.route("/api/cms/admin/users")
@admin_required
@json_api()
def get_users():
    users: List[User] = (
        session.query(User)
        .order_by(User.id.asc())
        .options(joinedload(User.participations))
        .options(selectinload("participations.contest"))
        .all()
    )
    return [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "participations": [
                {
                    "id": part.id,
                    "contest": _dump_contest_short(part.contest),
                }
                for part in user.participations
            ],
        }
        for user in users
    ]


@cmsadmin_bp.route("/api/cms/admin/user/<int:user_id>")
@admin_required
@json_api()
def get_user(user_id: int):
    user: Optional[User] = (
        session.query(User)
        .filter(User.id == user_id)
        .options(joinedload(User.participations))
        .options(selectinload("participations.contest"))
        .first()
    )
    if user is None:
        raise AOINotFound("User not found")
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "participations": [
            {
                "id": part.id,
                "contest": _dump_contest_short(part.contest),
            }
            for part in user.participations
        ],
    }


@cmsadmin_bp.route("/api/cms/admin/tasks")
@admin_required
@json_api()
def get_tasks():
    tasks: List[Task] = session.query(Task).options(joinedload(Task.contest)).all()
    return [
        {
            "id": task.id,
            "name": task.name,
            "title": task.title,
            "contest": _dump_contest_short(task.contest)
            if task.contest is not None
            else None,
        }
        for task in tasks
    ]
