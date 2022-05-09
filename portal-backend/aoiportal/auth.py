import hmac
import secrets
from datetime import timedelta
from typing import Optional
from uuid import uuid4

import voluptuous as vol
from flask import Blueprint, render_template
from sqlalchemy.exc import IntegrityError

from aoiportal.auth_util import (
    check_password,
    create_session,
    get_current_session,
    get_current_user,
    hash_password,
    invalidate_session,
    login_required,
)
from aoiportal.const import (
    KEY_EMAIL,
    KEY_FIRST_NAME,
    KEY_LAST_NAME,
    KEY_NEW_PASSWORD,
    KEY_OLD_PASSWORD,
    KEY_PASSWORD,
    KEY_UUID,
    KEY_VERIFICATION_CODE,
)
from aoiportal.error import (
    ERROR_ALREADY_LOGGED_IN,
    ERROR_EMAIL_EXISTS,
    ERROR_INVALID_PASSWORD,
    ERROR_INVALID_VERIFICATION_CODE,
    ERROR_NO_LONGER_VALID,
    ERROR_RATE_LIMIT,
    ERROR_TOO_MANY_ATTEMPTS,
    ERROR_USER_NOT_FOUND,
    AOIBadRequest,
    AOIConflict,
    AOINotFound,
    AOIUnauthorized,
)
from aoiportal.mail import send_email
from aoiportal.models import (
    User,
    UserEmailChangeRequest,
    UserPasswordResetRequest,
    UserRegisterRequest,
    db,
)
from aoiportal.utils import as_utc, utcnow
from aoiportal.web_utils import json_api

auth_bp = Blueprint("auth", __name__)

SET_PASSWORD_SCHEMA = vol.All(str, vol.Length(min=8))


@auth_bp.route("/api/auth/login", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_EMAIL): vol.Email(),
        vol.Required(KEY_PASSWORD): str,
    }
)
def login(data):
    if get_current_user() is not None:
        raise AOIConflict("Already logged in", error_code=ERROR_ALREADY_LOGGED_IN)

    user: Optional[User] = User.query.filter_by(email=data[KEY_EMAIL]).first()
    if user is None:
        raise AOINotFound("User does not exist", error_code=ERROR_USER_NOT_FOUND)
    if user.password_hash is None or not check_password(
        data[KEY_PASSWORD], user.password_hash
    ):
        raise AOIUnauthorized("Invalid password", error_code=ERROR_INVALID_PASSWORD)
    db.session.commit()
    _, token = create_session(user)
    return {
        "success": True,
        "token": token,
    }


@auth_bp.route("/api/auth/status")
@json_api()
def auth_status():
    u = get_current_user()
    if u is None:
        return {
            "authenticated": False,
            "admin": False
        }
    return {
        "authenticated": True,
        "admin": u.is_admin,
        "first_name": u.first_name,
        "last_name": u.last_name,
    }


@auth_bp.route("/api/auth/logout", methods=["POST"])
@login_required
@json_api()
def logout():
    invalidate_session(get_current_session())
    return {"success": True}


def send_email_verification_code(user: UserRegisterRequest) -> None:
    code = user.verification_code
    kwargs = {"first_name": user.first_name, "verification_code": code}
    content_html = render_template("email_verification.html", **kwargs)
    send_email(
        user.email,
        f"{code} ist dein Informatikolympiade Verifizierungscode",
        content_html,
    )


def send_email_change_verification_code(req: UserEmailChangeRequest) -> None:
    code = req.verification_code
    kwargs = {"first_name": req.user.first_name, "verification_code": code}
    content_html = render_template("email_change.html", **kwargs)
    send_email(
        req.new_email,
        "Informatikolympiade Änderung E-Mail-Adresse",
        content_html,
    )


def send_password_reset_verification_code(req: UserPasswordResetRequest) -> None:
    code = req.verification_code
    kwargs = {"first_name": req.user.first_name, "verification_code": code}
    content_html = render_template("password_reset.html", **kwargs)
    send_email(
        req.user.email,
        "Informatikolympiade Passwort Zurücksetzen",
        content_html,
    )


@auth_bp.route("/api/auth/register", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_EMAIL): vol.Email(),
        vol.Required(KEY_FIRST_NAME): vol.All(str, vol.Length(min=1)),
        vol.Required(KEY_LAST_NAME): vol.All(str, vol.Length(min=1)),
        vol.Required(KEY_PASSWORD): SET_PASSWORD_SCHEMA,
    }
)
def register(data):
    existing_user: Optional[User] = User.query.filter_by(email=data[KEY_EMAIL]).first()
    if existing_user is not None:
        raise AOIConflict("A user with that email already exists", error_code=ERROR_EMAIL_EXISTS)

    now = utcnow()
    recent_req_count = (
        db.session.query(UserRegisterRequest)
        .filter(UserRegisterRequest.email == data[KEY_EMAIL])
        .filter(UserRegisterRequest.created_at > now - timedelta(hours=12))
        .count()
    )
    if recent_req_count >= 3:
        raise AOIBadRequest("Register rate limited.", error_code=ERROR_RATE_LIMIT)

    verification_code = "".join(secrets.choice("0123456789") for i in range(6))
    user_register_request = UserRegisterRequest(
        uuid=str(uuid4()),
        first_name=data[KEY_FIRST_NAME],
        last_name=data[KEY_LAST_NAME],
        email=data[KEY_EMAIL],
        password_hash=hash_password(data[KEY_PASSWORD]),
        verification_code=verification_code,
        created_at=now,
        valid_until=now + timedelta(hours=3),
        attempts=0,
        valid=True,
    )
    db.session.add(user_register_request)
    db.session.commit()

    send_email_verification_code(user_register_request)
    return {
        "success": True,
        "uuid": user_register_request.uuid,
    }


"""
# TODO: could be used to brute force verification code
@auth_bp.route("/api/auth/register-rerequest-email", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_UUID): str,
    }
)
def register_rerequest_email(data):
    req: Optional[UserRegisterRequest] = UserRegisterRequest.query.filter_by(uuid=data[KEY_UUID]).first()
    if req is None:
        raise AOINotFound("Register request not found")
    now = utcnow()
    if not req.valid:
        raise AOIBadRequest("Register request not valid")

    new_verification_code = ''.join(secrets.choice("0123456789") for i in range(6))
    now = utcnow()

    req.verification_code = new_verification_code
    req.valid_until = now + timedelta(hours=3)
    req.attempts = 0
    db.session.commit()

    send_email_verification_code(req)
    return {"success": True}
"""


@auth_bp.route("/api/auth/register-verify", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_UUID): str,
        vol.Required(KEY_VERIFICATION_CODE): str,
    }
)
def register_verify(data):
    req: Optional[UserRegisterRequest] = UserRegisterRequest.query.filter_by(
        uuid=data[KEY_UUID]
    ).first()
    if req is None:
        raise AOINotFound("Register request not found")
    now = utcnow()
    if not req.valid or now < as_utc(req.created_at) or now > as_utc(req.valid_until):
        raise AOIBadRequest("Register request not valid", error_code=ERROR_NO_LONGER_VALID)
    if req.attempts >= 3:
        raise AOIBadRequest("Too many attempts", error_code=ERROR_TOO_MANY_ATTEMPTS)

    same = hmac.compare_digest(req.verification_code, data[KEY_VERIFICATION_CODE])
    if not same:
        req.attempts += 1
        db.session.commit()
        raise AOIBadRequest("Invalid verification code", error_code=ERROR_INVALID_VERIFICATION_CODE)
    user = User(
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        password_hash=req.password_hash,
        created_at=now,
    )
    req.valid = False
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        raise AOIBadRequest("User already exists", error_code=ERROR_EMAIL_EXISTS)

    _, token = create_session(user)
    return {
        "success": True,
        "token": token,
    }


@auth_bp.route("/api/auth/change-password", methods=["POST"])
@login_required
@json_api(
    {
        vol.Optional(KEY_OLD_PASSWORD): str,
        vol.Required(KEY_NEW_PASSWORD): SET_PASSWORD_SCHEMA,
    }
)
def change_password(data):
    u = get_current_user()
    if u.password_hash is not None:
        if KEY_OLD_PASSWORD not in data:
            raise AOIBadRequest("Need to specify old_password.")
        if not u.check_password(data[KEY_OLD_PASSWORD]):
            raise AOIBadRequest("Old password does not match", error_code=ERROR_INVALID_PASSWORD)
    u.password_hash = hash_password(data[KEY_NEW_PASSWORD])
    # TODO: invalidate old sessions except this one
    db.session.commit()
    return {"success": True}


@auth_bp.route("/api/auth/request-password-reset", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_EMAIL): vol.Email(),
    }
)
def request_password_reset(data):
    user = User.query.filter_by(email=data[KEY_EMAIL]).first()
    if user is None:
        raise AOINotFound("No user with that email address.", error_code=ERROR_USER_NOT_FOUND)

    now = utcnow()
    recent_req_count = (
        db.session.query(UserPasswordResetRequest)
        .filter(UserPasswordResetRequest.user == user)
        .filter(UserPasswordResetRequest.created_at > now - timedelta(hours=12))
        .count()
    )
    if recent_req_count >= 3:
        raise AOIBadRequest("Password reset rate limited.", error_code=ERROR_RATE_LIMIT)

    verification_code = "".join(secrets.choice("0123456789") for i in range(6))
    now = utcnow()
    password_request = UserPasswordResetRequest(
        uuid=str(uuid4()),
        user=user,
        verification_code=verification_code,
        created_at=now,
        valid_until=now + timedelta(hours=3),
        attempts=0,
        valid=True,
    )
    db.session.add(password_request)
    db.session.commit()

    send_password_reset_verification_code(password_request)
    return {
        "success": True,
        "uuid": password_request.uuid,
    }


@auth_bp.route("/api/auth/reset-password", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_UUID): str,
        vol.Required(KEY_VERIFICATION_CODE): str,
        vol.Optional(KEY_NEW_PASSWORD): SET_PASSWORD_SCHEMA,
    }
)
def reset_password(data):
    req: Optional[UserPasswordResetRequest] = UserPasswordResetRequest.query.filter_by(
        uuid=data[KEY_UUID]
    ).first()
    if req is None:
        raise AOINotFound("Password reset request not found")
    now = utcnow()
    if not req.valid or now < as_utc(req.created_at) or now > as_utc(req.valid_until):
        raise AOIBadRequest("Password reset request not valid", error_code=ERROR_NO_LONGER_VALID)
    if req.attempts >= 3:
        raise AOIBadRequest("Too many attempts", error_code=ERROR_TOO_MANY_ATTEMPTS)

    same = hmac.compare_digest(req.verification_code, data[KEY_VERIFICATION_CODE])
    if not same:
        req.attempts += 1
        db.session.commit()
        raise AOIBadRequest("Invalid verification code", error_code=ERROR_INVALID_VERIFICATION_CODE)

    if KEY_NEW_PASSWORD not in data:
        return {
            "success": True,
        }

    req.user.password_hash = hash_password(data[KEY_NEW_PASSWORD])
    # TODO: invalidate old sessions except this one
    db.session.commit()
    _, token = create_session(req.user)
    return {
        "success": True,
        "token": token,
    }


@auth_bp.route("/api/auth/change-email", methods=["POST"])
@login_required
@json_api(
    {
        vol.Optional(KEY_PASSWORD): str,
        vol.Required(KEY_EMAIL): vol.Email(),
    }
)
def change_email(data):
    current_user = get_current_user()
    if current_user.email == data[KEY_EMAIL]:
        raise AOIBadRequest("Email hasn't changed")
    if current_user.password_hash is not None:
        if KEY_PASSWORD not in data:
            raise AOIBadRequest("Password is required")
        if not check_password(data[KEY_PASSWORD], current_user.password_hash):
            raise AOIBadRequest("Password does not match", error_code=ERROR_INVALID_PASSWORD)
    existing = User.query.filter_by(email=data[KEY_EMAIL]).first()
    if existing is not None:
        raise AOIBadRequest("Email already registered for a different user.", error_code=ERROR_EMAIL_EXISTS)

    now = utcnow()
    recent_req_count = (
        db.session.query(UserEmailChangeRequest)
        .filter(UserEmailChangeRequest.user == current_user)
        .filter(UserEmailChangeRequest.created_at > now - timedelta(hours=12))
        .count()
    )
    if recent_req_count >= 3:
        raise AOIBadRequest("Password reset rate limited.", error_code=ERROR_RATE_LIMIT)

    verification_code = "".join(secrets.choice("0123456789") for i in range(6))
    email_change_request = UserEmailChangeRequest(
        uuid=str(uuid4()),
        user=current_user,
        new_email=data[KEY_EMAIL],
        verification_code=verification_code,
        created_at=now,
        valid_until=now + timedelta(hours=3),
        attempts=0,
        valid=True,
    )
    db.session.add(email_change_request)
    db.session.commit()

    send_email_change_verification_code(email_change_request)
    return {
        "success": True,
        "uuid": email_change_request.uuid,
    }


@auth_bp.route("/api/auth/change-email-verify", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_UUID): str,
        vol.Required(KEY_VERIFICATION_CODE): str,
    }
)
def change_email_verify(data):
    req: Optional[UserEmailChangeRequest] = UserEmailChangeRequest.query.filter_by(
        uuid=data[KEY_UUID]
    ).first()
    if req is None:
        raise AOINotFound("Email change request not found")
    now = utcnow()
    if not req.valid or now < as_utc(req.created_at) or now > as_utc(req.valid_until):
        raise AOIBadRequest("Email change request not valid", error_code=ERROR_NO_LONGER_VALID)
    if req.attempts >= 3:
        raise AOIBadRequest("Too many attempts", error_code=ERROR_TOO_MANY_ATTEMPTS)

    same = hmac.compare_digest(req.verification_code, data[KEY_VERIFICATION_CODE])
    if not same:
        req.attempts += 1
        db.session.commit()
        raise AOIBadRequest("Invalid verification code", error_code=ERROR_INVALID_VERIFICATION_CODE)

    req.user.email = req.new_email
    # TODO: invalidate old sessions except this one
    db.session.commit()
    return {"success": True}
