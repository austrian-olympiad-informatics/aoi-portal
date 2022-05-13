import base64
import datetime
import functools
import uuid
from typing import Optional

import nacl.secret
import nacl.utils
import voluptuous as vol  # type: ignore
from flask import Blueprint, current_app
from sqlalchemy.orm import joinedload

from aoiportal.auth_util import get_current_user, hash_password, login_required
from aoiportal.cms_bridge import ContestUpdateParams, cms
from aoiportal.const import (
    KEY_ADDRESS_STREET,
    KEY_ADDRESS_TOWN,
    KEY_ADDRESS_ZIP,
    KEY_ARCHIVED,
    KEY_AUTO_ADD_TO_GROUP_ID,
    KEY_BIRTHDAY,
    KEY_CMS_ID,
    KEY_CMS_USERNAME,
    KEY_CONTENT,
    KEY_DESCRIPTION,
    KEY_EMAIL,
    KEY_FIRST_NAME,
    KEY_GROUP_ID,
    KEY_GROUPS,
    KEY_IS_ADMIN,
    KEY_LAST_NAME,
    KEY_MANUAL_PASSWORD,
    KEY_NAME,
    KEY_OPEN_SIGNUP,
    KEY_ORDER_PRIORITY,
    KEY_PASSWORD,
    KEY_PHONE_NR,
    KEY_QUALI_ROUND,
    KEY_RANDOM_MANUAL_PASSWORDS,
    KEY_RECIPIENTS,
    KEY_REPLY_TO,
    KEY_SCHOOL_ADDRESS,
    KEY_SCHOOL_NAME,
    KEY_SUBJECT,
    KEY_TEASER,
    KEY_URL,
    KEY_USER_ID,
    KEY_USERS,
)
from aoiportal.error import ERROR_ADMIN_REQUIRED, AOIForbidden, AOINotFound
from aoiportal.mail import Address, encode_email, send_mass
from aoiportal.models import (  # type: ignore
    Contest,
    Group,
    NewsletterSubscription,
    Participation,
    User,
    db,
)
from aoiportal.newsletter import gen_unsubscribe_link
from aoiportal.web_utils import json_api

admin_bp = Blueprint("admin", __name__)


def admin_required(fn):
    @login_required
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        if not get_current_user().is_admin:
            raise AOIForbidden(
                "This API needs admin access.", error_code=ERROR_ADMIN_REQUIRED
            )
        return fn(*args, **kwargs)

    return wrapped


def _conv_user(user: User) -> dict:
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "is_admin": user.is_admin,
        "birthday": user.birthday.isoformat() if user.birthday is not None else None,
        "phone_nr": user.phone_nr,
        "address_street": user.address_street,
        "address_zip": user.address_zip,
        "address_town": user.address_town,
        "school_name": user.school_name,
        "school_address": user.school_address,
        "cms_id": user.cms_id,
        "cms_username": user.cms_username,
        "groups": [
            {
                "id": g.id,
                "name": g.name,
            }
            for g in user.groups
        ],
    }


@admin_bp.route("/api/admin/users")
@admin_required
@json_api()
def get_users():
    q = db.session.query(User).options(joinedload(User.groups))
    return [_conv_user(u) for u in q]


@admin_bp.route("/api/admin/users/<int:user_id>")
@admin_required
@json_api()
def get_user(user_id: int):
    u = User.query.filter_by(id=user_id).first()
    if u is None:
        raise AOINotFound("User not found")
    return {
        **_conv_user(u),
        "groups": [
            {
                "id": g.id,
                "name": g.name,
                "description": g.description,
            }
            for g in u.groups
        ],
        "participations": [
            {
                "id": p.id,
                "contest": {
                    "uuid": p.contest.uuid,
                    "cms_name": p.contest.cms_name,
                    "cms_description": p.contest.cms_description,
                },
            }
            for p in u.participations
        ],
    }


@admin_bp.route("/api/admin/users/<int:user_id>/delete", methods=["DELETE"])
@admin_required
@json_api()
def delete_user(user_id: int):
    u = User.query.filter_by(id=user_id).first()
    if u is None:
        raise AOINotFound("User not found")
    db.session.delete(u)
    db.session.commit()
    return {"success": True}


def _conv_datestr(datestr: Optional[str]) -> Optional[datetime.date]:
    if datestr is None:
        return None
    dt = datetime.datetime.strptime(datestr, "%Y-%m-%d")
    return dt.date()


@admin_bp.route("/api/admin/users/<int:user_id>/update", methods=["PUT"])
@admin_required
@json_api(
    {
        vol.Optional(KEY_FIRST_NAME): str,
        vol.Optional(KEY_LAST_NAME): str,
        vol.Optional(KEY_EMAIL): str,
        vol.Optional(KEY_PASSWORD): vol.All(str, vol.Length(min=8)),
        vol.Optional(KEY_IS_ADMIN): bool,
        vol.Optional(KEY_BIRTHDAY): vol.Any(None, vol.Date()),
        vol.Optional(KEY_PHONE_NR): vol.Any(None, str),
        vol.Optional(KEY_ADDRESS_STREET): vol.Any(None, str),
        vol.Optional(KEY_ADDRESS_ZIP): vol.Any(None, str),
        vol.Optional(KEY_ADDRESS_TOWN): vol.Any(None, str),
        vol.Optional(KEY_SCHOOL_NAME): vol.Any(None, str),
        vol.Optional(KEY_SCHOOL_ADDRESS): vol.Any(None, str),
        vol.Optional(KEY_CMS_ID): vol.Any(None, int),
        vol.Optional(KEY_CMS_USERNAME): vol.Any(None, str),
        vol.Optional(KEY_GROUPS): [int],
    }
)
def update_user(data, user_id: int):
    u: Optional[User] = User.query.filter_by(id=user_id).first()
    if u is None:
        raise AOINotFound("User not found")
    if KEY_FIRST_NAME in data:
        u.first_name = data[KEY_FIRST_NAME]
    if KEY_LAST_NAME in data:
        u.last_name = data[KEY_LAST_NAME]
    if KEY_EMAIL in data:
        u.email = data[KEY_EMAIL]
    if KEY_PASSWORD in data:
        u.password_hash = hash_password(data[KEY_PASSWORD])
    if KEY_IS_ADMIN in data:
        u.is_admin = data[KEY_IS_ADMIN]
    if KEY_BIRTHDAY in data:
        u.birthday = _conv_datestr(data[KEY_BIRTHDAY])
    if KEY_PHONE_NR in data:
        u.phone_nr = data[KEY_PHONE_NR]
    if KEY_ADDRESS_STREET in data:
        u.address_street = data[KEY_ADDRESS_STREET]
    if KEY_ADDRESS_ZIP in data:
        u.address_zip = data[KEY_ADDRESS_ZIP]
    if KEY_ADDRESS_TOWN in data:
        u.address_town = data[KEY_ADDRESS_TOWN]
    if KEY_SCHOOL_NAME in data:
        u.school_name = data[KEY_SCHOOL_NAME]
    if KEY_SCHOOL_ADDRESS in data:
        u.school_address = data[KEY_SCHOOL_ADDRESS]
    if KEY_GROUPS in data:
        u.groups = []
        for gid in data[KEY_GROUPS]:
            g: Optional[Group] = Group.query.filter_by(id=gid).first()
            if g is None:
                raise AOINotFound("Group not found")
            u.groups.append(g)
    if KEY_CMS_ID in data:
        u.cms_id = data[KEY_CMS_ID]
    if KEY_CMS_USERNAME in data:
        u.cms_username = data[KEY_CMS_USERNAME]

    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/users/create", methods=["POST"])
@admin_required
@json_api(
    {
        vol.Required(KEY_FIRST_NAME): str,
        vol.Required(KEY_LAST_NAME): str,
        vol.Required(KEY_EMAIL): str,
        vol.Required(KEY_PASSWORD): vol.All(str, vol.Length(min=8)),
        vol.Optional(KEY_IS_ADMIN, default=False): bool,
        vol.Optional(KEY_BIRTHDAY, default=None): vol.Any(None, vol.Date()),
        vol.Optional(KEY_PHONE_NR, default=None): vol.Any(None, str),
        vol.Optional(KEY_ADDRESS_STREET, default=None): vol.Any(None, str),
        vol.Optional(KEY_ADDRESS_ZIP, default=None): vol.Any(None, str),
        vol.Optional(KEY_ADDRESS_TOWN, default=None): vol.Any(None, str),
        vol.Optional(KEY_SCHOOL_NAME, default=None): vol.Any(None, str),
        vol.Optional(KEY_SCHOOL_ADDRESS, default=None): vol.Any(None, str),
        vol.Optional(KEY_GROUPS, default=[]): [int],
        vol.Optional(KEY_CMS_ID, default=None): vol.Any(None, int),
        vol.Optional(KEY_CMS_USERNAME, default=None): vol.Any(None, str),
    }
)
def create_user(data):
    u = User(
        first_name=data[KEY_FIRST_NAME],
        last_name=data[KEY_LAST_NAME],
        email=data[KEY_EMAIL],
        is_admin=data[KEY_IS_ADMIN],
        birthday=_conv_datestr(data[KEY_BIRTHDAY]),
        phone_nr=data[KEY_PHONE_NR],
        address_street=data[KEY_ADDRESS_STREET],
        address_zip=data[KEY_ADDRESS_ZIP],
        address_town=data[KEY_ADDRESS_TOWN],
        school_name=data[KEY_SCHOOL_NAME],
        school_address=data[KEY_SCHOOL_ADDRESS],
        cms_id=data[KEY_CMS_ID],
        cms_username=data[KEY_CMS_USERNAME],
        password_hash=hash_password(data[KEY_PASSWORD]),
    )
    for gid in data[KEY_GROUPS]:
        g: Optional[Group] = Group.query.filter_by(id=gid).first()
        if g is None:
            raise AOINotFound("Group not found")
        u.groups.append(g)

    db.session.add(u)
    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/refresh-cms-contests", methods=["POST"])
@admin_required
@json_api()
def refresh_cms_contests():
    ourcontests = Contest.query.all()
    ourids = {c.cms_id: c for c in ourcontests}
    cmscontests = cms.list_contests()
    cmsids = {c.id: c for c in cmscontests}

    for c in cmscontests:
        if c.id not in ourids:
            # does not exist yet, create it
            cmsc = Contest(
                uuid=str(uuid.uuid4()),
                cms_id=c.id,
                name=c.name,
                teaser=c.description,
                description=c.description,
            )
        else:
            cmsc = ourids[c.id]

        cmsc.cms_name = c.name
        cmsc.cms_description = c.name
        cmsc.cms_allow_sso_authentication = c.allow_sso_authentication
        cmsc.cms_sso_secret_key = c.sso_secret_key
        cmsc.cms_sso_redirect_url = c.sso_redirect_url
        cmsc.deleted = False

        if c.id not in ourids:
            db.session.add(cmsc)

    for c in ourcontests:
        if c.cms_id not in cmsids:
            # no longer exists in cms, delete
            c.deleted = True

    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/contests")
@admin_required
@json_api()
def list_contests():
    return [
        {
            "uuid": c.uuid,
            "cms_id": c.cms_id,
            "cms_name": c.cms_name,
            "cms_description": c.cms_description,
            "cms_allow_sso_authentication": c.cms_allow_sso_authentication,
            "cms_sso_redirect_url": c.cms_sso_redirect_url,
            "url": c.url,
            "open_signup": c.open_signup,
            "quali_round": c.quali_round,
            "name": c.name,
            "teaser": c.teaser,
            "description": c.description,
            "archived": c.archived,
            "deleted": c.deleted,
            "order_priority": c.order_priority,
            "auto_add_to_group": {
                "id": c.auto_add_to_group.id,
                "name": c.auto_add_to_group.name,
                "description": c.auto_add_to_group.description,
            }
            if c.auto_add_to_group is not None
            else None,
            "participant_count": len(c.participations),
        }
        for c in db.session.query(Contest)
    ]


@admin_bp.route("/api/admin/contests/<contest_uuid>")
@admin_required
@json_api()
def get_contest(contest_uuid: str):
    c = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")
    return {
        "uuid": c.uuid,
        "cms_id": c.cms_id,
        "cms_name": c.cms_name,
        "cms_description": c.cms_description,
        "cms_allow_sso_authentication": c.cms_allow_sso_authentication,
        "cms_sso_secret_key": c.cms_sso_secret_key,
        "cms_sso_redirect_url": c.cms_sso_redirect_url,
        "url": c.url,
        "open_signup": c.open_signup,
        "quali_round": c.quali_round,
        "name": c.name,
        "teaser": c.teaser,
        "description": c.description,
        "archived": c.archived,
        "deleted": c.deleted,
        "order_priority": c.order_priority,
        "auto_add_to_group": {
            "id": c.auto_add_to_group.id,
            "name": c.auto_add_to_group.name,
            "description": c.auto_add_to_group.description,
        }
        if c.auto_add_to_group is not None
        else None,
        "participations": [
            {
                "id": p.id,
                "cms_id": p.cms_id,
                "user": {
                    "id": p.user.id,
                    "first_name": p.user.first_name,
                    "last_name": p.user.last_name,
                    "username": p.user.cms_username,
                },
                "manual_password": p.manual_password,
            }
            for p in c.participations
        ],
    }


@admin_bp.route("/api/admin/contests/<contest_uuid>/ranking")
@admin_required
@json_api()
def get_contest_ranking(contest_uuid: str):
    c: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")
    res = cms.get_contest_ranking(contest_id=c.cms_id)

    cmsid_to_uid = {
        part.user.cms_id: part.user_id
        for part in db.session.query(Participation).filter(
            Participation.contest_id == c.id
        )
    }

    return {
        "success": True,
        "tasks": res.tasks,
        "ranking": [
            {
                "user_id": cmsid_to_uid[r.user_id],
                "task_scores": r.task_scores,
                "total_score": r.total_score,
            }
            for r in res.ranking
            if r.user_id in cmsid_to_uid
        ],
    }


@admin_bp.route("/api/admin/contests/<contest_uuid>/delete", methods=["DELETE"])
@admin_required
@json_api()
def delete_contest(contest_uuid: str):
    c = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")
    db.session.delete(c)
    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/contests/<contest_uuid>/update", methods=["PUT"])
@admin_required
@json_api(
    {
        vol.Optional(KEY_OPEN_SIGNUP): bool,
        vol.Optional(KEY_AUTO_ADD_TO_GROUP_ID): vol.Any(None, int),
        vol.Optional(KEY_URL): str,
        vol.Optional(KEY_NAME): str,
        vol.Optional(KEY_TEASER): str,
        vol.Optional(KEY_DESCRIPTION): str,
        vol.Optional(KEY_QUALI_ROUND): bool,
        vol.Optional(KEY_ARCHIVED): bool,
        vol.Optional(KEY_ORDER_PRIORITY): vol.Coerce(float),
    }
)
def update_contest(data, contest_uuid: str):
    c: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")
    if KEY_OPEN_SIGNUP in data:
        c.open_signup = data[KEY_OPEN_SIGNUP]
    if KEY_AUTO_ADD_TO_GROUP_ID in data:
        if data[KEY_AUTO_ADD_TO_GROUP_ID] is None:
            c.auto_add_to_group = None
        else:
            group: Optional[Group] = Group.query.filter_by(
                id=data[KEY_AUTO_ADD_TO_GROUP_ID]
            ).first()
            if group is not None:
                raise AOINotFound("Group not found")
            c.auto_add_to_group = group
    if KEY_URL in data:
        c.url = data[KEY_URL]
    if KEY_NAME in data:
        c.name = data[KEY_NAME]
    if KEY_TEASER in data:
        c.teaser = data[KEY_TEASER]
    if KEY_DESCRIPTION in data:
        c.description = data[KEY_DESCRIPTION]
    if KEY_QUALI_ROUND in data:
        c.quali_round = data[KEY_QUALI_ROUND]
    if KEY_ARCHIVED in data:
        c.archived = data[KEY_ARCHIVED]
    if KEY_ORDER_PRIORITY in data:
        c.order_priority = data[KEY_ORDER_PRIORITY]
    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/contests/<contest_uuid>/provision-sso", methods=["POST"])
@admin_required
@json_api()
def contest_provision_sso(contest_uuid: str):
    c: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")

    secret_key_b = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    secret_key = base64.b64encode(secret_key_b).decode()
    base_url = current_app.config["BASE_URL"]
    redirect_url = f"{base_url}/contests/{c.uuid}/sso"

    cms.update_contest(
        contest_id=c.cms_id,
        params=ContestUpdateParams(
            name=c.cms_name,
            description=c.cms_description,
            allow_sso_authentication=True,
            sso_secret_key=secret_key,
            sso_redirect_url=redirect_url,
        ),
    )
    c.cms_allow_sso_authentication = True
    c.cms_sso_secret_key = secret_key
    c.cms_sso_redirect_url = redirect_url
    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/contests/<contest_uuid>/remove-sso", methods=["POST"])
@admin_required
@json_api()
def contest_remove_sso(contest_uuid: str):
    c: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")

    cms.update_contest(
        contest_id=c.cms_id,
        params=ContestUpdateParams(
            name=c.cms_name,
            description=c.cms_description,
            allow_sso_authentication=False,
            sso_secret_key="",
            sso_redirect_url="",
        ),
    )
    c.cms_allow_sso_authentication = False
    c.cms_sso_secret_key = ""
    c.cms_sso_redirect_url = ""
    db.session.commit()
    return {"success": True}


@admin_bp.route(
    "/api/admin/contests/<contest_uuid>/participations/create", methods=["POST"]
)
@admin_required
@json_api(
    {
        vol.Required(KEY_USER_ID): int,
        vol.Optional(KEY_CMS_ID, default=None): vol.Any(None, int),
        vol.Optional(KEY_MANUAL_PASSWORD, default=None): vol.Any(None, str),
    }
)
def create_participation(data, contest_uuid: str):
    c: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")
    user: Optional[User] = User.query.filter_by(id=data[KEY_USER_ID]).first()
    if user is None:
        raise AOINotFound("User not found")

    if data[KEY_CMS_ID] is None:
        from aoiportal.helpers import create_participation

        part = create_participation(user, c, manual_password=data[KEY_MANUAL_PASSWORD])
    else:
        part = Participation(
            cms_id=data[KEY_CMS_ID],
            contest=c,
            user=user,
        )
        db.session.add(part)
        db.session.commit()

        if data[KEY_MANUAL_PASSWORD] is not None:
            cms.set_participation_password(
                contest_id=c.cms_id,
                participation_id=part.cms_id,
                manual_password=data[KEY_MANUAL_PASSWORD],
            )
            part.manual_password = data[KEY_MANUAL_PASSWORD]
            db.session.commit()

    return {
        "success": True,
        "id": part.id,
    }


@admin_bp.route("/api/admin/contests/<contest_uuid>/participations/<int:part_id>")
@admin_required
@json_api()
def get_participation(contest_uuid: str, part_id: int):
    c: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")
    part = Participation.query.filter_by(id=part_id, contest_id=c.id).first()
    if part is None:
        raise AOINotFound("Participation not found")

    return {
        "cms_id": part.cms_id,
        "user": {
            "id": part.user.id,
            "first_name": part.user.first_name,
            "last_name": part.user.last_name,
            "email": part.user.email,
            "cms_username": part.user.cms_username,
        },
        "manual_password": part.manual_password,
    }


@admin_bp.route(
    "/api/admin/contests/<contest_uuid>/participations/<int:part_id>/update",
    methods=["PUT"],
)
@admin_required
@json_api(
    {
        vol.Optional(KEY_CMS_ID): int,
        vol.Optional(KEY_MANUAL_PASSWORD): vol.Any(None, str),
    }
)
def update_participation(data, contest_uuid: str, part_id: int):
    c: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")
    part = Participation.query.filter_by(part_id=part_id, contest_id=c.id).first()
    if part is None:
        raise AOINotFound("Participation not found")
    if KEY_CMS_ID in data:
        part.cms_id = data[KEY_CMS_ID]
        db.session.commit()
    if KEY_MANUAL_PASSWORD in data:
        cms.set_participation_password(
            contest_id=part.contest.cms_id,
            participation_id=part.cms_id,
            manual_password=data[KEY_MANUAL_PASSWORD],
        )
        part.manual_password = data[KEY_MANUAL_PASSWORD]
        db.session.commit()
    return {
        "success": True,
    }


@admin_bp.route(
    "/api/admin/contests/<contest_uuid>/participations/<int:part_id>/delete",
    methods=["DELETE"],
)
@admin_required
@json_api()
def delete_participation(contest_uuid: str, part_id: int):
    c: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")
    part = Participation.query.filter_by(id=part_id, contest_id=c.id).first()
    if part is None:
        raise AOINotFound("Participation not found")

    db.session.delete(part)
    db.session.commit()

    # TODO: remove the participation in CMS as well

    return {"success": True}


@admin_bp.route("/api/admin/contests/<contest_uuid>/import-group", methods=["POST"])
@admin_required
@json_api(
    {
        vol.Required(KEY_GROUP_ID): int,
        vol.Optional(KEY_RANDOM_MANUAL_PASSWORDS, default=False): bool,
    }
)
def contest_import_group(data, contest_uuid: str):
    c: Optional[Contest] = Contest.query.filter_by(uuid=contest_uuid).first()
    if c is None:
        raise AOINotFound("Contest not found")
    g: Optional[Group] = Group.query.filter_by(id=data[KEY_GROUP_ID]).first()
    if g is None:
        raise AOINotFound("Group not found")
    for u in g.users:
        existing: Optional[Participation] = Participation.query.filter_by(
            user_id=u.id, contest_id=c.id
        ).first()
        if existing is not None:
            continue
        from aoiportal.helpers import create_participation, random_password

        create_participation(u, c, manual_password=random_password())

    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/groups")
@admin_required
@json_api()
def list_groups():
    return [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "user_count": len(g.users),
        }
        for g in db.session.query(Group)
    ]


@admin_bp.route("/api/admin/groups/<int:group_id>")
@admin_required
@json_api()
def get_group(group_id: int):
    g: Optional[Group] = Group.query.filter_by(id=group_id).first()
    if g is None:
        raise AOINotFound("Group not found")
    return {
        "id": g.id,
        "name": g.name,
        "description": g.description,
        "users": [
            {
                "id": u.id,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "email": u.email,
            }
            for u in g.users
        ],
    }


@admin_bp.route("/api/admin/groups/<int:group_id>/update", methods=["PUT"])
@admin_required
@json_api(
    {
        vol.Optional(KEY_NAME): str,
        vol.Optional(KEY_DESCRIPTION): str,
        vol.Optional(KEY_USERS): [int],
    }
)
def update_group(data, group_id: int):
    g: Optional[Group] = Group.query.filter_by(id=group_id).first()
    if g is None:
        raise AOINotFound("Group not found")
    if KEY_NAME in data:
        g.name = data[KEY_NAME]
    if KEY_DESCRIPTION in data:
        g.description = data[KEY_DESCRIPTION]
    if KEY_USERS in data:
        g.users = []
        for uid in data[KEY_USERS]:
            user = User.query.filter_by(id=uid).first()
            if user is None:
                raise AOINotFound("User not found")
            g.users.append(user)
    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/groups/create", methods=["POST"])
@admin_required
@json_api(
    {
        vol.Required(KEY_NAME): str,
        vol.Required(KEY_DESCRIPTION): str,
        vol.Optional(KEY_USERS, default=[]): [int],
    }
)
def create_group(data):
    g = Group(
        name=data[KEY_NAME],
        description=data[KEY_DESCRIPTION],
    )
    g.users = []
    for uid in data[KEY_USERS]:
        user = User.query.filter_by(id=uid).first()
        if user is None:
            raise AOINotFound("User not found")
        g.users.append(user)
    db.session.add(g)
    db.session.commit()
    return {
        "success": True,
        "id": g.id,
    }


@admin_bp.route("/api/admin/groups/<int:group_id>/delete", methods=["DELETE"])
@admin_required
@json_api()
def delete_group(group_id: int):
    g: Optional[Group] = Group.query.filter_by(id=group_id).first()
    if g is None:
        raise AOINotFound("Group not found")
    db.session.delete(g)
    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/user-email", methods=["POST"])
@admin_required
@json_api(
    {
        vol.Required(KEY_RECIPIENTS): [int],
        vol.Required(KEY_SUBJECT): str,
        vol.Required(KEY_CONTENT): str,
        vol.Optional(KEY_REPLY_TO): [
            {
                vol.Required(KEY_EMAIL): vol.Email(),
                vol.Optional(KEY_NAME): str,
            }
        ],
    }
)
def send_user_email(data):
    reply_to = None
    if KEY_REPLY_TO in data:
        reply_to = [
            Address(v[KEY_EMAIL], v.get(KEY_NAME) or None) for v in data[KEY_REPLY_TO]
        ]
    mails = []
    for uid in set(data[KEY_RECIPIENTS]):
        u: Optional[User] = User.query.filter_by(id=uid).first()
        if u is None:
            raise AOINotFound(f"User {uid} not found")
        content = (
            data[KEY_CONTENT]
            .replace("%VORNAME%", u.first_name)
            .replace("%NACHNAME%", u.last_name)
        )
        mails.append(
            encode_email(
                to=Address(u.email, f"{u.first_name} {u.last_name}"),
                subject=data[KEY_SUBJECT],
                content_html=content,
                reply_to=reply_to or None,
            )
        )

    failed = send_mass(mails)
    return {"success": True, "failed_addresses": [f.recipients for f in failed]}


@admin_bp.route("/api/admin/newsletter/subscribers")
@admin_required
@json_api()
def get_newsletter_subscribers():
    return [
        {
            "email": sub.email,
            "created_at": sub.created_at,
        }
        for sub in db.session.query(NewsletterSubscription)
    ]


@admin_bp.route("/api/admin/newsletter/<email>/delete", methods=["DELETE"])
@admin_required
@json_api()
def delete_newsletter_subscriber(email: str):
    sub: Optional[NewsletterSubscription] = NewsletterSubscription.query.filter_by(
        email=email
    ).first()
    if sub is None:
        raise AOINotFound("Subscription not found")
    db.session.delete(sub)
    db.session.commit()
    return {"success": True}


@admin_bp.route("/api/admin/newsletter-email", methods=["POST"])
@admin_required
@json_api(
    {
        vol.Required(KEY_SUBJECT): str,
        vol.Required(KEY_CONTENT): str,
        vol.Optional(KEY_REPLY_TO): [
            {
                vol.Required(KEY_EMAIL): vol.Email(),
                vol.Optional(KEY_NAME): str,
            }
        ],
    }
)
def send_newsletter_email(data):
    reply_to = None
    if KEY_REPLY_TO in data:
        reply_to = [
            Address(v[KEY_EMAIL], v.get(KEY_NAME) or None) for v in data[KEY_REPLY_TO]
        ]
    mails = []
    for sub in db.session.query(NewsletterSubscription):
        unsubscribe_link = gen_unsubscribe_link(sub)
        mails.append(
            encode_email(
                to=Address(sub.email),
                subject=data[KEY_SUBJECT],
                content_html=data[KEY_CONTENT],
                reply_to=reply_to or None,
                unsubscribe_link=unsubscribe_link,
            )
        )

    failed = send_mass(mails)
    return {"success": True, "failed_addresses": [f.recipients for f in failed]}
