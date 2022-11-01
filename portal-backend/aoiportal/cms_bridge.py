import datetime
import secrets
from dataclasses import dataclass
from typing import Dict, List, Optional

from slugify import slugify

from aoiportal.cmsmirror.db import Contest as CMSContest  # type: ignore
from aoiportal.cmsmirror.db import Participation as CMSParticipation  # type: ignore
from aoiportal.cmsmirror.db import Submission as CMSSubmission  # type: ignore
from aoiportal.cmsmirror.db import (
    SubmissionResult as CMSSubmissionResult,  # type: ignore
)
from aoiportal.cmsmirror.db import Task as CMSTask  # type: ignore
from aoiportal.cmsmirror.db import User as CMSUser  # type: ignore
from aoiportal.cmsmirror.db import session as cms_session
from aoiportal.cmsmirror.util import ScoreInput, score_calculation  # type: ignore


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
    task_scores: Dict[str, Optional[float]]
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
        except Exception:  # pylint: disable=broad-except
            subtask_scores = None

        if subtask_scores is None or len(subtask_scores) == 0:
            # Task's score type is not group, assume a single subtask.
            subtask_scores = {1: score}

        for idx, score in subtask_scores.items():
            max_scores[idx] = max(max_scores.get(idx, 0.0), score)

    return sum(max_scores.values())


def _task_score(part: CMSParticipation, task: CMSTask):
    submissions: List[CMSSubmission] = [
        s for s in part.submissions if s.task is task and s.official
    ]
    if not submissions:
        return 0.0, False

    submissions_and_results = []
    for sub in sorted(submissions, key=lambda s: s.timestamp):
        res = next(
            (r for r in sub.results if r.dataset_id == task.active_dataset_id), None
        )
        submissions_and_results.append((sub, res))

    score_details_tokened = []
    partial = False
    for s, sr in submissions_and_results:
        if sr is None or not sr.scored():
            partial = True
            score, score_details = None, None
        else:
            score, score_details = sr.score, sr.score_details
        score_details_tokened.append((score, score_details, True))

    if task.score_mode == "max":
        score = _task_score_max(score_details_tokened)
    elif task.score_mode == "max_subtask":
        score = _task_score_max_subtask(score_details_tokened)
    else:
        raise ValueError(f"Unknown score mode '{task.score_mode}'")
    score = round(score, task.score_precision)
    return score, partial


def get_contest_ranking(contest_id: int) -> RankingResult:
    task_id_name = (
        cms_session.query(CMSTask.id, CMSTask.name)
        .filter(CMSTask.contest_id == contest_id)
        .all()
    )
    part_id_uid = (
        cms_session.query(CMSParticipation.id, CMSParticipation.user_id)
        .filter(CMSParticipation.contest_id == contest_id)
        .all()
    )

    q = (
        cms_session.query(
            CMSTask.id,
            CMSParticipation.id,
            CMSTask.score_mode,
            CMSSubmissionResult.score,
            CMSSubmissionResult.score_details,
        )
        .join(CMSSubmission.task)
        .join(CMSSubmission.results)
        .join(CMSSubmission.participation)
        .join(CMSParticipation.user)
        .filter(CMSTask.contest_id == contest_id)
        .filter(CMSParticipation.hidden == False)
        .filter(CMSParticipation.contest_id == contest_id)
        .filter(CMSSubmissionResult.dataset_id == CMSTask.active_dataset_id)
        .filter(CMSSubmission.official)
        .all()
    )

    rows = [
        ScoreInput(
            task_id=task_id,
            part_id=part_id,
            score_mode=score_mode,
            score=score,
            score_details=score_details,
        )
        for task_id, part_id, score_mode, score, score_details in q
    ]
    res = score_calculation(rows)

    task_id_to_name = dict(task_id_name)
    task_names = [row[1] for row in task_id_name]
    part_id_to_uid = dict(part_id_uid)

    uid_task_scores: Dict[int, Dict[int, float]] = {}
    for (task_id, part_id), v in res.items():
        uid = part_id_to_uid[part_id]
        x = uid_task_scores.setdefault(uid, {})
        x[task_id] = v.score

    ranking = []
    for uid, x in uid_task_scores.items():
        ranking.append(
            RankingUser(
                user_id=uid,
                task_scores={
                    name: x.get(task_id, None)
                    for task_id, name in task_id_to_name.items()
                },
                total_score=sum(x.values()),
            )
        )

    return RankingResult(
        tasks=task_names,
        ranking=ranking,
    )


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
        return (
            cms_session.query(CMSUser).filter(CMSUser.username == u).first() is not None
        )

    if not exists(username):
        return username

    i = 1
    while True:
        attempt = f"{username}{i}"
        if not exists(attempt):
            return attempt
        i += 1


def create_user(email: str, first_name: str, last_name: str) -> CreateUserResult:
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
    contest = cms_session.query(CMSContest).filter(CMSContest.id == contest_id).first()
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
