from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
import secrets
from typing import Dict, List, Optional

import requests
from flask import current_app
from sqlalchemy.orm import joinedload
from slugify import slugify

from aoiportal.cmsmirror.db import (
    session as cms_session,
    Contest as CMSContest,
    Participation as CMSParticipation,
    Task as CMSTask,
    User as CMSUser,
)


@dataclass
class Contest:
    id: int
    name: str
    description: str
    allow_sso_authentication: bool
    sso_secret_key: str
    sso_redirect_url: str
    allow_frontendv2: bool
    # start_time: datetime.datetime
    # end_time: datetime.datetime
    # analysis_enabled: bool
    # analysis_start_time: datetime.datetime
    # analysis_end_time: datetime.datetime


@dataclass
class ContestUpdateParams:
    name: str
    description: str
    allow_sso_authentication: bool
    sso_secret_key: str
    sso_redirect_url: str


@dataclass
class RankingUser:
    user_id: int
    task_scores: Dict[str, float]
    total_score: float


@dataclass
class RankingResult:
    tasks: List[str]
    ranking: List[RankingUser]


@dataclass
class CreateUserResult:
    cms_id: int
    cms_username: str


def _task_score_max(score_details_tokened):
    return max(
        [score for score, _, _ in score_details_tokened if score is not None],
        default=0.0,
    )


def _task_score_max_subtask(score_details_tokened):
    # Maximum score for each subtask (not yet computed scores count as 0.0).
    max_scores = {}

    for score, details, _ in score_details_tokened:
        if score is None:
            continue

        if details == [] and score == 0.0:
            # Submission did not compile, ignore it.
            continue

        try:
            subtask_scores = dict(
                (subtask["idx"], subtask["score_fraction"] * subtask["max_score"])
                for subtask in details
            )
        except Exception:
            subtask_scores = None

        if subtask_scores is None or len(subtask_scores) == 0:
            # Task's score type is not group, assume a single subtask.
            subtask_scores = {1: score}

        for idx, score in subtask_scores.items():
            max_scores[idx] = max(max_scores.get(idx, 0.0), score)

    return sum(max_scores.values())


def _task_score(part: CMSParticipation, task: CMSTask):
    submissions = [s for s in part.submissions if s.task is task and s.official]
    if not submissions:
        return 0.0, False

    submissions_and_results = [
        (s, s.get_result(task.active_dataset))
        for s in sorted(submissions, key=lambda s: s.timestamp)
    ]

    score_details_tokened = []
    partial = False
    for s, sr in submissions_and_results:
        if sr is None or not sr.scored():
            partial = True
            score, score_details = None, None
        else:
            score, score_details = sr.score, sr.score_details
        score_details_tokened.append((score, score_details, s.tokened()))

    if task.score_mode == "max":
        score = _task_score_max(score_details_tokened)
    elif task.score_mode == "max_subtask":
        score = _task_score_max_subtask(score_details_tokened)
    else:
        raise ValueError("Unknown score mode '%s'" % task.score_mode)
    score = round(score, task.score_precision)
    return score, partial


def get_contest_ranking(contest_id: int) -> RankingResult:
    contest = (
        cms_session.query(CMSContest)
        .filter(CMSContest.id == contest_id)
        .options(joinedload("participations"))
        .options(joinedload("participations.submissions"))
        .options(joinedload("participations.submissions.results"))
        .first()
    )

    tasks = [task.name for task in contest.tasks]
    ranking = []

    for p in contest.participations:
        total_score = 0.0
        task_scores = {}
        for task in contest.tasks:
            t_score, _ = _task_score(p, task, rounded=True)
            task_scores[task.name] = t_score
            total_score += t_score
        total_score = round(total_score, contest.score_precision)
        ranking.append(
            {
                "user_id": p.user.id,
                "task_scores": task_scores,
                "total_score": total_score,
            }
        )

    return {"tasks": tasks, "ranking": ranking}


def update_contest(
    contest_id: int,
    *,
    name: str,
    description: str,
    allow_sso_authentication: bool,
    sso_secret_key: str,
    sso_redirect_url: str,
) -> None:
    contest = cms_session.query(CMSContest).filter(CMSContest.id == contest_id).first()
    contest.name = name
    contest.description = description
    contest.allow_sso_authentication = allow_sso_authentication
    contest.sso_secret_key = sso_secret_key
    contest.sso_redirect_url = sso_redirect_url
    cms_session.commit()


def set_participation_password(
    contest_id: int, participation_id: int, manual_password: Optional[str]
) -> None:
    part = (
        cms_session.query(CMSParticipation)
        .filter(CMSParticipation.id == participation_id)
        .filter(CMSParticipation.contest_id == contest_id)
        .first()
    )
    part.password = f"plaintext:{manual_password}"
    cms_session.commit()


def _gen_username(first_name: str, last_name: str) -> str:
    username = slugify(
        f"{first_name} {last_name}",
        replacements=[("ä", "ae"), ("ü", "ue"), ("ö", "oe")],
    )

    def exists(u):
        return cms_session.query(CMSUser).filter(CMSUser.username == u).first() is not None

    if not exists(username):
        return username

    i = 1
    while True:
        attempt = f"{username}{i}"
        if not exists(attempt):
            return attempt
        i += 1


def create_user(
    email: str, first_name: str, last_name: str
) -> CreateUserResult:
    username = _gen_username(first_name, last_name)
    # We use SSO login, so just make password something unguessable
    password = secrets.token_urlsafe(32)
    stored_password = f"plaintext:{password}"
    user = CMSUser(
        first_name=first_name,
        last_name=last_name,
        username=username,
        password=stored_password,
        email=email,
        timezone=None,
        preferred_languages=[],
    )
    cms_session.add(user)
    cms_session.commit()
    return CreateUserResult(
        cms_id=user.id,
        cms_username=user.username,
    )

def create_participation(
    user_id: int, contest_id: int, manual_password: Optional[str] = None
) -> int:
    stored_password = None
    if manual_password is not None:
        stored_password = f"plaintext:{manual_password}"
    user = cms_session.query(CMSUser).filter(CMSUser.id == user_id).first()
    contest = (
        cms_session.query(Contest).filter(Contest.id == contest_id).first()
    )
    part = CMSParticipation(
        user=user,
        contest=contest,
        ip=None,
        delay_time=datetime.timedelta(seconds=0),
        extra_time=datetime.timedelta(seconds=0),
        password=stored_password,
        team=None,
        hidden=False,
        unrestricted=False,
    )
    cms_session.add(part)
    cms_session.commit()
    return part.id
