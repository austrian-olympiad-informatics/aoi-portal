import functools
from typing import Optional
import datetime

from werkzeug.exceptions import Unauthorized, NotFound
from flask import Blueprint
from flask_login import login_required, current_user
import voluptuous as vol

from aoiportal.const import KEY_ADDRESS_STREET, KEY_ADDRESS_TOWN, KEY_ADDRESS_ZIP, KEY_AUTO_ADD_TO_GROUP_ID, KEY_BIRTHDAY, KEY_CMS_ID, KEY_CONTEST_ID, KEY_DESCRIPTION, KEY_EMAIL, KEY_EMAIL_CONFIRMED, KEY_FIRST_NAME, KEY_GROUP_ID, KEY_GROUPS, KEY_IS_ADMIN, KEY_LAST_NAME, KEY_MANUAL_PASSWORD, KEY_NAME, KEY_PASSWORD, KEY_PHONE_NR, KEY_PUBLIC, KEY_RANDOM_MANUAL_PASSWORDS, KEY_SCHOOL_ADDRESS, KEY_SCHOOL_NAME, KEY_USER_ID, KEY_USERS
from aoiportal.web_utils import json_request, json_response
from aoiportal.models import (
    Contest,
    db,
    User,
    Group,
    Participation,
)
from aoiportal.cms_bridge import cms

admin_bp = Blueprint("admin", __name__)


def admin_required(fn):
    @login_required
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            raise Unauthorized("This API needs admin access.")
        return fn(*args, **kwargs)

    return wrapped


def _conv_user(user: User) -> dict:
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login is not None else None,
        "is_admin": user.is_admin,
        "email_confirmed": user.email_confirmed,
        "last_email_confirmed_at": user.last_email_confirmed_at.isoformat() if user.last_email_confirmed_at is not None else None,
        "last_password_change_at": user.last_password_change_at.isoformat() if user.last_password_change_at is not None else None,
        "birthday": user.birthday.isoformat() if user.birthday is not None else None,
        "phone_nr": user.phone_nr,
        "address_street": user.address_street,
        "address_zip": user.address_zip,
        "address_town": user.address_town,
        "school_name": user.school_name,
        "school_address": user.school_address,
    }


@admin_bp.route("/api/admin/users")
@admin_required
@json_response()
def get_users():
    return [
        _conv_user(u)
        for u in db.session.query(User)
    ]


@admin_bp.route("/api/admin/users/<int:user_id>")
@admin_required
@json_response()
def get_user(user_id: int):
    u = User.query.filter_by(id=user_id).first()
    if u is None:
        raise NotFound("User not found")
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
                    "id": p.contest.id,
                    "cms_name": p.contest.cms_name,
                    "cms_description": p.contest.cms_description,
                },
            }
            for p in u.participations
        ],
    }


@admin_bp.route("/api/admin/users/<int:user_id>/delete", methods=["DELETE"])
@admin_required
@json_response()
def delete_user(user_id: int):
    u = User.query.filter_by(id=user_id).first()
    if u is None:
        raise NotFound("User not found")
    db.session.delete(u)
    db.session.commit()
    return {
        "success": True
    }



@admin_bp.route("/api/admin/users/<int:user_id>/update", methods=["PUT"])
@admin_required
@json_request({
    vol.Optional(KEY_FIRST_NAME): str,
    vol.Optional(KEY_LAST_NAME): str,
    vol.Optional(KEY_EMAIL): str,
    vol.Optional(KEY_PASSWORD): str,
    vol.Optional(KEY_IS_ADMIN): bool,
    vol.Optional(KEY_EMAIL_CONFIRMED): bool,
    vol.Optional(KEY_BIRTHDAY): vol.Date(),
    vol.Optional(KEY_PHONE_NR): str,
    vol.Optional(KEY_ADDRESS_STREET): str,
    vol.Optional(KEY_ADDRESS_ZIP): str,
    vol.Optional(KEY_ADDRESS_TOWN): str,
    vol.Optional(KEY_SCHOOL_NAME): str,
    vol.Optional(KEY_SCHOOL_ADDRESS): str,
    vol.Optional(KEY_GROUPS): [int],
})
@json_response()
def update_user(data, user_id: int):
    u: Optional[User] = User.query.filter_by(id=user_id).first()
    if u is None:
        raise NotFound("User not found")
    if KEY_FIRST_NAME in data:
        u.first_name = data[KEY_FIRST_NAME]
    if KEY_LAST_NAME in data:
        u.last_name = data[KEY_LAST_NAME]
    if KEY_EMAIL in data:
        u.email = data[KEY_EMAIL]
    if KEY_PASSWORD in data:
        u.set_password(data[KEY_PASSWORD])
    if KEY_IS_ADMIN in data:
        u.is_admin = data[KEY_IS_ADMIN]
    if KEY_EMAIL_CONFIRMED in data:
        u.email_confirmed = data[KEY_EMAIL_CONFIRMED]
    if KEY_BIRTHDAY in data:
        dt = datetime.datetime.strptime("%Y-%m-%d", data[KEY_BIRTHDAY])
        u.birthday = dt.date()
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
                raise NotFound("Group not found")
            u.groups.append(g)

    db.session.commit()
    return {
        "success": True
    }


@admin_bp.route("/api/admin/refresh-cms-contests", methods=["POST"])
@admin_required
@json_response()
def refresh_cms_contests():
    ourcontests = Contest.query.all()
    ourids = {c.cms_id: c for c in ourcontests}
    cmscontests = cms.list_contests()
    cmsids = {c.id: c for c in cmscontests}

    for c in cmscontests:
        if c.id not in ourids:
            # does not exist yet, create it
            cmsc = Contest(cms_id=c.id, cms_name=c.name, cms_description=c.description)
            db.session.add(cmsc)
            continue
        cmsc = ourids[c.id]
        cmsc.cms_name = c.name
        cmsc.cms_description = c.name

    for c in ourcontests:
        if c.cms_id not in cmsids:
            # no longer exists in cms, delete
            db.session.delete(c)

    db.session.commit()
    return {
        "success": True
    }


@admin_bp.route("/api/admin/contests")
@admin_required
@json_response()
def list_contests():
    return [
        {
            "id": c.id,
            "cms_id": c.cms_id,
            "cms_name": c.cms_name,
            "cms_description": c.cms_description,
            "public": c.public,
            "auto_add_to_group": {
                "id": c.auto_add_to_group.id,
                "name": c.auto_add_to_group.name,
                "description": c.auto_add_to_group.description,
            } if c.auto_add_to_group is not None else None,
        }
        for c in db.session.query(Contest)
    ]


@admin_bp.route("/api/admin/contests/<int:contest_id>")
@admin_required
@json_response()
def get_contest(contest_id: int):
    c = Contest.query.filter_by(id=contest_id).first()
    if c is None:
        raise NotFound("Contest not found")
    return {
        "id": c.id,
        "cms_id": c.cms_id,
        "cms_name": c.cms_name,
        "cms_description": c.cms_description,
        "public": c.public,
        "auto_add_to_group": {
            "id": c.auto_add_to_group.id,
            "name": c.auto_add_to_group.name,
            "description": c.auto_add_to_group.description,
        } if c.auto_add_to_group is not None else None,
        "participations": [
            {
                "id": p.id,
                "cms_id": p.cms_id,
                "user": {
                    "id": p.user.id,
                    "first_name": p.user.last_name,
                    "last_name": p.user.last_name,
                    "username": p.user.cms_username,
                },
                "manual_password": p.manual_password,
            }
            for p in c.participations
        ]
    }


@admin_bp.route("/api/admin/contests/<int:contest_id>/update", methods=["PUT"])
@admin_required
@json_request({
    vol.Optional(KEY_PUBLIC): bool,
    vol.Optional(KEY_AUTO_ADD_TO_GROUP_ID): vol.Any(None, int),
})
@json_response()
def update_contest(data, contest_id: int):
    c: Optional[Contest] = Contest.query.filter_by(id=contest_id).first()
    if c is None:
        raise NotFound("Contest not found")
    if KEY_PUBLIC in data:
        c.public = data[KEY_PUBLIC]
    if KEY_AUTO_ADD_TO_GROUP_ID in data:
        if data[KEY_AUTO_ADD_TO_GROUP_ID] is None:
            c.auto_add_to_group = None
        else:
            group: Optional[Group] = Group.query.filter_by(id=data[KEY_AUTO_ADD_TO_GROUP_ID]).first()
            if group is not None:
                raise NotFound("Group not found")
            c.auto_add_to_group = group
    db.session.commit()
    return {
        "success": True
    }


@admin_bp.route("/api/admin/contests/<int:contest_id>/participations/create", methods=["POST"])
@admin_required
@json_request({
    vol.Required(KEY_USER_ID): int,
    vol.Optional(KEY_CMS_ID): int,
    vol.Optional(KEY_MANUAL_PASSWORD, default=None): vol.Any(None, str),
})
@json_response()
def create_participation(data, contest_id: int):
    c: Optional[Contest] = Contest.query.filter_by(id=contest_id).first()
    if c is None:
        raise NotFound("Contest not found")
    user: Optional[User] = User.query.filter_by(id=data[KEY_USER_ID]).first()
    if user is None:
        raise NotFound("User not found")
    
    from aoiportal.helpers import create_participation
    part = create_participation(user, c, manual_password=data[KEY_MANUAL_PASSWORD])
    return {
        "success": True,
        "id": part.id,
    }


@admin_bp.route("/api/admin/contests/<int:contest_id>/participations/<int:part_id>")
@admin_required
@json_response()
def get_participation(contest_id: int, part_id: int):
    part = Participation.query.filter_by(part_id=part_id, contest_id=contest_id).first()
    if part is None:
        raise NotFound("Participation not found")
        
    return {
        "cms_id": part.cms_id,
        "user": {
            "id": part.user.id,
            "first_name": part.user.first_name,
            "last_name": part.user.last_name,
            "email": part.user.email,
            "cms_username": part.user.cms_username,
        },
        "manual_password": part.user.manual_password,
    }


@admin_bp.route("/api/admin/contests/<int:contest_id>/participations/<int:part_id>/update", methods=["PUT"])
@admin_required
@json_request({
    vol.Optional(KEY_CMS_ID): int,
    vol.Optional(KEY_MANUAL_PASSWORD): vol.Any(None, str),
})
@json_response()
def update_participation(data, contest_id: int, part_id: int):
    part = Participation.query.filter_by(part_id=part_id, contest_id=contest_id).first()
    if part is None:
        raise NotFound("Participation not found")
    if KEY_CMS_ID in data:
        part.cms_id = data[KEY_CMS_ID]
        db.session.commit()
    if KEY_MANUAL_PASSWORD in data:
        from aoiportal.cms_bridge import cms
        cms.set_participation_password(
            contest_id=part.contest.cms_id,
            participation_id=part.cms_id,
            manual_password=data[KEY_MANUAL_PASSWORD]
        )
        part.manual_password = data[KEY_MANUAL_PASSWORD]
        db.session.commit()
    return {
        "success": True,
    }


@admin_bp.route("/api/admin/contests/<int:contest_id>/participations/<int:part_id>/delete", methods=["DELETE"])
@admin_required
@json_response()
def delete_participation(data, contest_id: int, part_id: int):
    part = Participation.query.filter_by(part_id=part_id, contest_id=contest_id).first()
    if part is None:
        raise NotFound("Participation not found")

    db.session.delete(part)
    db.session.commit()
    # TODO: should we remove the participation in CMS as well?

    return {
        "success": True
    }


@admin_bp.route("/api/admin/contests/<int:contest_id>/import-group", methods=["POST"])
@admin_required
@json_request({
    vol.Required(KEY_GROUP_ID): int,
    vol.Optional(KEY_RANDOM_MANUAL_PASSWORDS, default=False): bool,
})
@json_response()
def contest_import_group(data, contest_id: int):
    c: Optional[Contest] = Contest.query.filter_by(id=contest_id).first()
    if c is None:
        raise NotFound("Contest not found")
    g: Optional[Group] = Group.query.filter_by(id=data[KEY_GROUP_ID]).first()
    if g is None:
        raise NotFound("Group not found")
    for u in g.users:
        existing: Optional[Participation] = Participation.query.filter_by(user_id=u.id, contest_id=c.id).first()
        if existing is not None:
            continue
        from aoiportal.helpers import create_participation, random_password
        create_participation(u, c, manual_password=random_password())

    db.session.commit()
    return {
        "success": True
    }


@admin_bp.route("/api/admin/groups")
@admin_required
@json_response()
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
@json_response()
def get_group(group_id: int):
    g: Optional[Group] = Group.query.filter_by(id=group_id).first()
    if g is None:
        raise NotFound("Group not found")
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
        ]
    }


@admin_bp.route("/api/admin/groups/<int:group_id>/update", methods=["PUT"])
@admin_required
@json_request({
    vol.Optional(KEY_NAME): str,
    vol.Optional(KEY_DESCRIPTION): str,
    vol.Optional(KEY_USERS): [int],
})
@json_response()
def update_group(data, group_id: int):
    g: Optional[Group] = Group.query.filter_by(id=group_id).first()
    if g is None:
        raise NotFound("Group not found")
    if KEY_NAME in data:
        g.name = data[KEY_NAME]
    if KEY_DESCRIPTION in data:
        g.description = data[KEY_DESCRIPTION]
    if KEY_USERS in data:
        g.users = []
        for uid in data[KEY_USERS]:
            user = User.query.filter_by(id=uid).first()
            if user is None:
                raise NotFound("User not found")
            g.users.append(user)
    db.session.commit()
    return {
        "success": True
    }


@admin_bp.route("/api/admin/groups/create", methods=["POST"])
@admin_required
@json_request({
    vol.Required(KEY_NAME): str,
    vol.Required(KEY_DESCRIPTION): str,
    vol.Optional(KEY_USERS, default=[]): [int],
})
@json_response()
def create_group(data):
    g = Group(
        name=data[KEY_NAME],
        description=data[KEY_DESCRIPTION],
    )
    g.users = []
    for uid in data[KEY_USERS]:
        user = User.query.filter_by(id=uid).first()
        if user is None:
            raise NotFound("User not found")
        g.users.append(user)
    db.session.add(g)
    db.session.commit()
    return {
        "success": True,
        "id": g.id,
    }


@admin_bp.route("/api/admin/groups/<int:group_id>/delete", methods=["DELETE"])
@admin_required
@json_response()
def delete_group(group_id: int):
    g: Optional[Group] = Group.query.filter_by(id=group_id).first()
    if g is None:
        raise NotFound("Group not found")
    db.session.delete(g)
    db.session.commit()
    return {
        "success": True
    }
