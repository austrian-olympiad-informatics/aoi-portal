import base64
import datetime
import json
from typing import Optional

import nacl.secret
from flask import Blueprint
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from aoiportal.auth_util import get_current_user, login_required
from aoiportal.error import AOIConflict, AOINotFound
from aoiportal.helpers import create_participation
from aoiportal.models import Contest, Participation, db  # type: ignore
from aoiportal.utils import utcnow
from aoiportal.web_utils import json_api

contests_bp = Blueprint("contests", __name__)


@contests_bp.route("/api/contests")
@login_required
@json_api()
def list_contests():
    q = (
        db.session.query(Contest, Participation)
        .join(
            Participation,
            and_(
                Contest.id == Participation.contest_id,
                Participation.user_id == get_current_user().id,
            ),
            isouter=True,
        )
        .filter(Contest.deleted == False)  # pylint: disable=singleton-comparison
        .order_by(Contest.order_priority.desc())
    )
    ret = []
    for contest, part in q:
        joined = part is not None
        can_join = False
        if not joined:
            can_join = contest.open_signup or get_current_user().is_admin
        if not joined and not can_join:
            continue

        value = {
            "uuid": contest.uuid,
            "name": contest.name,
            "teaser": contest.teaser,
            "description": contest.description,
            "joined": joined,
            "open_signup": contest.open_signup or get_current_user().is_admin,
            "quali_round": contest.quali_round,
            "order_priority": contest.order_priority,
            "archived": contest.archived,
        }
        if joined:
            value["url"] = contest.url
            sso_enabled = bool(
                contest.cms_allow_sso_authentication
                and contest.cms_sso_secret_key
                and contest.url
            )
            value["sso_enabled"] = sso_enabled
            value["cms_name"] = contest.cms_name
            value["allow_frontendv2"] = contest.cms_allow_frontendv2

        ret.append(value)

    return ret


@contests_bp.route("/api/contests/<contest_uuid>")
@login_required
@json_api()
def get_contest(contest_uuid: str):
    contest = Contest.query.filter_by(uuid=contest_uuid).first()
    if contest is None or contest.deleted:
        raise AOINotFound("Contest not found")

    current_user = get_current_user()
    assert current_user is not None
    part: Optional[Participation] = (
        db.session.query(Participation)
        .filter(Participation.contest == contest)
        .filter(Participation.user == current_user)
        .first()
    )
    joined = part is not None
    can_join = False
    if not joined:
        can_join = contest.open_signup or current_user.is_admin
    if not joined and not can_join:
        raise AOINotFound("Contest not found")

    value = {
        "name": contest.name,
        "teaser": contest.teaser,
        "description": contest.description,
        "joined": joined,
        "open_signup": contest.open_signup or current_user.is_admin,
        "quali_round": contest.quali_round,
        "order_priority": contest.order_priority,
        "archived": contest.archived,
    }
    if joined:
        value["url"] = contest.url
        sso_enabled = bool(
            contest.cms_allow_sso_authentication
            and contest.cms_sso_secret_key
            and contest.url
        )
        value["sso_enabled"] = sso_enabled
        value["cms_name"] = contest.cms_name
        value["allow_frontendv2"] = contest.cms_allow_frontendv2

    return value


@contests_bp.route("/api/contests/<contest_uuid>/join", methods=["POST"])
@login_required
@json_api()
def join_contest(contest_uuid: str):
    contest = Contest.query.filter_by(uuid=contest_uuid).first()
    can_join = (
        contest is not None
        and (contest.open_signup or get_current_user().is_admin)
        and not contest.deleted
    )
    if not can_join:
        raise AOINotFound("Contest not found")

    current_user = get_current_user()
    assert current_user is not None
    existing_part = (
        db.session.query(Participation)
        .filter(Participation.contest_id == contest.id)
        .filter(Participation.user_id == current_user.id)
        .first()
    )
    if existing_part is not None:
        raise AOIConflict("Contest already joined.")

    create_participation(current_user, contest, hidden=current_user.is_admin)

    if contest.auto_add_to_group is not None:
        try:
            current_user.groups.append(contest.auto_add_to_group)
            db.session.commit()
        except IntegrityError:
            # already in group
            pass

    return {"success": True}


@contests_bp.route("/api/contests/<contest_uuid>/gen-sso-token", methods=["POST"])
@login_required
@json_api()
def gen_sso_token(contest_uuid: str):
    # TODO: add state param like in oauth to avoid attacker giving user URL
    # that will log them in to different account
    contest: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if contest is None:
        raise AOINotFound("Contest not found")

    current_user = get_current_user()
    assert current_user is not None
    part: Optional[Participation] = (
        db.session.query(Participation)
        .filter(Participation.contest_id == contest.id)
        .filter(Participation.user_id == current_user.id)
        .first()
    )
    if part is None:
        raise AOINotFound("Not registered in contest")

    if (
        not contest.cms_allow_sso_authentication
        or not contest.cms_sso_secret_key
        or not contest.url
    ):
        raise AOIConflict("SSO is not enabled")

    keybytes = base64.b64decode(contest.cms_sso_secret_key.encode())
    box = nacl.secret.SecretBox(keybytes)
    now = utcnow()
    data = {
        "participation_id": part.cms_id,
        "created_at": now.timestamp(),
        "valid_until": (now + datetime.timedelta(minutes=5)).timestamp(),
    }
    plaintext = json.dumps(data).encode()
    ciphertext = box.encrypt(plaintext)

    return {
        "endpoint": f"{contest.url}/sso/authorized",
        "token": base64.urlsafe_b64encode(ciphertext).decode(),
    }
