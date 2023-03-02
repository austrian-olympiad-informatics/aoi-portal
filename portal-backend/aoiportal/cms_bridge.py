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
class CreateUserResult:
    cms_id: int
    cms_username: str


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
    user_id: int,
    contest_id: int,
    manual_password: Optional[str] = None,
    hidden: bool = False,
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
        hidden=hidden,
        unrestricted=False,
    )
    cms_session.add(part)
    cms_session.commit()
    return part.id
