import datetime
import secrets

import voluptuous as vol  # type: ignore
from cms.db import Contest, Participation, Session, SessionGen, User  # type: ignore
from cms.grading.scoring import task_score  # type: ignore
from cmscommon.crypto import hash_password  # type: ignore
from flask import Blueprint
from slugify import slugify
from sqlalchemy.orm import joinedload  # type: ignore

from cmsbridge.const import (
    KEY_ALLOW_FRONTENDV2,
    KEY_ALLOW_SSO_AUTHENTICATION,
    KEY_CONTEST_ID,
    KEY_DESCRIPTION,
    KEY_EMAIL,
    KEY_FIRST_NAME,
    KEY_ID,
    KEY_LAST_NAME,
    KEY_MANUAL_PASSWORD,
    KEY_NAME,
    KEY_PARTICIPATION_ID,
    KEY_SSO_REDIRECT_URL,
    KEY_SSO_SECRET_KEY,
    KEY_USER_ID,
    KEY_USERNAME,
)
from cmsbridge.web_utils import json_request, json_response

views_bp = Blueprint("views", __name__)


@views_bp.route("/list-contests")
@json_response()
def list_contests():
    with SessionGen() as session:
        return [
            {
                KEY_ID: c.id,
                KEY_NAME: c.name,
                KEY_DESCRIPTION: c.description,
                KEY_ALLOW_SSO_AUTHENTICATION: c.allow_sso_authentication,
                KEY_SSO_SECRET_KEY: c.sso_secret_key,
                KEY_SSO_REDIRECT_URL: c.sso_redirect_url,
                KEY_ALLOW_FRONTENDV2: c.allow_frontendv2,
            }
            for c in session.query(Contest)
        ]


@views_bp.route("/contests/<int:contest_id>")
@json_response()
def get_contest(contest_id: int):
    with SessionGen() as session:
        c = session.query(Contest).filter(Contest.id == contest_id).first()
        return {
            KEY_ID: c.id,
            KEY_NAME: c.name,
            KEY_DESCRIPTION: c.description,
            KEY_ALLOW_SSO_AUTHENTICATION: c.allow_sso_authentication,
            KEY_SSO_SECRET_KEY: c.sso_secret_key,
            KEY_SSO_REDIRECT_URL: c.sso_redirect_url,
            KEY_ALLOW_FRONTENDV2: c.allow_frontendv2,
        }


def _gen_username(session: Session, first_name: str, last_name: str) -> str:
    username = slugify(
        f"{first_name} {last_name}",
        replacements=[("ä", "ae"), ("ü", "ue"), ("ö", "oe")],
    )

    def exists(u):
        return session.query(User).filter(User.username == u).first() is not None

    if not exists(username):
        return username

    i = 1
    while True:
        attempt = f"{username}{i}"
        if not exists(attempt):
            return attempt
        i += 1


@views_bp.route("/create-user", methods=["POST"])
@json_request(
    {
        vol.Required(KEY_EMAIL): str,
        vol.Required(KEY_FIRST_NAME): str,
        vol.Required(KEY_LAST_NAME): str,
    }
)
@json_response()
def create_user(data):
    with SessionGen() as session:
        username = _gen_username(session, data[KEY_FIRST_NAME], data[KEY_LAST_NAME])
        # We use SSO login, so just make password something unguessable
        password = secrets.token_urlsafe(32)
        stored_password = hash_password(password, "plaintext")
        user = User(
            first_name=data[KEY_FIRST_NAME],
            last_name=data[KEY_LAST_NAME],
            username=username,
            password=stored_password,
            email=data[KEY_EMAIL],
            timezone=None,
            preferred_languages=[],
        )
        session.add(user)
        session.commit()
        user_id = user.id

    return {
        "success": True,
        KEY_USER_ID: user_id,
        KEY_USERNAME: username,
    }


@views_bp.route("/create-participation", methods=["POST"])
@json_request(
    {
        vol.Required(KEY_USER_ID): int,
        vol.Required(KEY_CONTEST_ID): int,
        vol.Required(KEY_MANUAL_PASSWORD): vol.Any(None, str),
    }
)
@json_response()
def create_participation(data):
    with SessionGen() as session:
        stored_password = None
        if data[KEY_MANUAL_PASSWORD] is not None:
            stored_password = hash_password(data[KEY_MANUAL_PASSWORD], "plaintext")
        user = session.query(User).filter(User.id == data[KEY_USER_ID]).first()
        contest = (
            session.query(Contest).filter(Contest.id == data[KEY_CONTEST_ID]).first()
        )
        part = Participation(
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
        session.add(part)
        session.commit()
        part_id = part.id
    return {
        "success": True,
        KEY_PARTICIPATION_ID: part_id,
    }


@views_bp.route("/set-participation-password", methods=["POST"])
@json_request(
    {
        vol.Required(KEY_CONTEST_ID): int,
        vol.Required(KEY_PARTICIPATION_ID): int,
        vol.Required(KEY_MANUAL_PASSWORD): vol.Any(None, str),
    }
)
@json_response()
def set_participation_password(data):
    with SessionGen() as session:
        part = (
            session.query(Participation)
            .filter(Participation.id == data[KEY_PARTICIPATION_ID])
            .filter(Participation.contest_id == data[KEY_CONTEST_ID])
            .first()
        )
        stored_password = None
        if data[KEY_MANUAL_PASSWORD] is not None:
            stored_password = hash_password(data[KEY_MANUAL_PASSWORD], "plaintext")
        part.password = stored_password
        session.commit()
    return {
        "success": True,
    }


@views_bp.route("/get-contest-ranking/<int:contest_id>")
@json_response()
def get_contest_ranking(contest_id: int):
    with SessionGen() as session:
        contest = (
            session.query(Contest)
            .filter(Contest.id == contest_id)
            .options(joinedload("participations"))
            .options(joinedload("participations.submissions"))
            .options(joinedload("participations.submissions.token"))
            .options(joinedload("participations.submissions.results"))
            .first()
        )

        tasks = [task.name for task in contest.tasks]
        ranking = []

        for p in contest.participations:
            total_score = 0.0
            task_scores = {}
            for task in contest.tasks:
                t_score, _ = task_score(p, task, rounded=True)
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


@views_bp.route("/update-contest", methods=["POST"])
@json_request(
    {
        vol.Required(KEY_CONTEST_ID): int,
        vol.Required(KEY_NAME): str,
        vol.Required(KEY_DESCRIPTION): str,
        vol.Required(KEY_ALLOW_SSO_AUTHENTICATION): bool,
        vol.Required(KEY_SSO_SECRET_KEY): str,
        vol.Required(KEY_SSO_REDIRECT_URL): str,
    }
)
@json_response()
def update_contest(data):
    with SessionGen() as session:
        c: Contest = (
            session.query(Contest).filter(Contest.id == data[KEY_CONTEST_ID]).first()
        )
        c.name = data[KEY_NAME]
        c.description = data[KEY_DESCRIPTION]
        c.allow_sso_authentication = data[KEY_ALLOW_SSO_AUTHENTICATION]
        c.sso_secret_key = data[KEY_SSO_SECRET_KEY]
        c.sso_redirect_url = data[KEY_SSO_REDIRECT_URL]
        session.commit()
    return {
        "success": True,
    }
