from datetime import timedelta
import secrets
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, render_template, current_app
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
import voluptuous as vol
from werkzeug.exceptions import Conflict, BadRequest, NotFound, Unauthorized
from typing import Optional

from aoiportal.models import db, User, UserEmailVerificationCode, UserPasswordResetCode
from aoiportal.utils import utcnow, as_utc
from aoiportal.web_utils import json_request, json_response
from aoiportal.const import KEY_EMAIL, KEY_FIRST_NAME, KEY_LAST_NAME, KEY_PASSWORD, KEY_TOKEN, KEY_OLD_PASSWORD, KEY_NEW_PASSWORD
from aoiportal.mail import send_email

login_manager = LoginManager()
auth_bp = Blueprint("auth", __name__)

SET_PASSWORD_SCHEMA = vol.All(str, vol.Length(min=8))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    raise Unauthorized("Need to log in first")


@auth_bp.route("/api/auth/login", methods=["POST"])
@json_request({
    vol.Required(KEY_EMAIL): vol.Email(),
    vol.Required(KEY_PASSWORD): str,
})
@json_response()
def login(data):
    if current_user.is_authenticated:
        raise BadRequest("Already logged in")
    
    user: Optional[User] = User.query.filter_by(email=data[KEY_EMAIL]).first()
    if user is None:
        raise NotFound("User does not exist")
    if not user.has_password or not user.check_password(data[KEY_PASSWORD]):
        raise Unauthorized("Invalid password")
    if not user.email_confirmed:
        raise Unauthorized("Email address not confirmed yet")
    user.last_login = utcnow()
    db.session.commit()
    login_user(user)
    return {
        "success": True
    }


@auth_bp.route("/api/auth/status")
@json_response()
def auth_status():
    return {
        "authenticated": current_user.is_authenticated,
        "admin": current_user.is_admin if current_user.is_authenticated else False,
    }


@auth_bp.route("/api/auth/logout", methods=["POST"])
@login_required
@json_response()
def logout():
    logout_user()
    return {
        "success": True
    }


def send_email_verification_code(user: User) -> None:
    token = secrets.token_urlsafe(32)
    email_verification_code = UserEmailVerificationCode(
        user=user,
        token=token,
        valid_until=utcnow() + timedelta(hours=3),
        email=user.email,
    )
    db.session.add(email_verification_code)
    db.session.commit()

    base_url = current_app.config["BASE_URL"]
    # TODO
    confirm_url = f"{base_url}/verify-email/{token}"
    kwargs = {
        "first_name": user.first_name,
        "confirm_url": confirm_url
    }
    content_html = render_template("email_verification.html", **kwargs)
    body_txt = render_template("email_verification.txt", **kwargs)
    send_email(
        user.email, "Aktiviere deinen informatikolympiade Account",
        body_txt, content_html
    )


def send_change_email_verification_code(user: User, new_email: str) -> None:
    token = secrets.token_urlsafe(32)
    email_verification_code = UserEmailVerificationCode(
        user=user,
        token=token,
        valid_until=utcnow() + timedelta(hours=3),
        email=new_email,
    )
    db.session.add(email_verification_code)
    db.session.commit()

    base_url = current_app.config["BASE_URL"]
    # TODO
    confirm_url = f"{base_url}/verify-email/{token}"
    kwargs = {
        "first_name": user.first_name,
        "new_email": new_email,
        "confirm_url": confirm_url
    }
    content_html = render_template("email_change.html", **kwargs)
    body_txt = render_template("email_change.txt", **kwargs)
    send_email(
        user.email, "Änderung deiner Emailadresse",
        body_txt, content_html
    )


def send_password_reset_email(user: User) -> None:
    token = secrets.token_urlsafe(32)
    email_verification_code = UserPasswordResetCode(
        user=user,
        token=token,
        valid_until=utcnow() + timedelta(hours=3),
    )
    db.session.add(email_verification_code)
    db.session.commit()

    base_url = current_app.config["BASE_URL"]
    # TODO
    confirm_url = f"{base_url}/reset-password/{token}"
    kwargs = {
        "first_name": user.first_name,
        "confirm_url": confirm_url
    }
    content_html = render_template("password_reset.html", **kwargs)
    body_txt = render_template("password_reset.txt", **kwargs)
    send_email(
        user.email, "Passwort zurücksetzen",
        body_txt, content_html
    )


@auth_bp.route("/api/auth/register", methods=["POST"])
@json_request({
    vol.Required(KEY_EMAIL): vol.Email(),
    vol.Required(KEY_FIRST_NAME): vol.All(str, vol.Length(min=1)),
    vol.Required(KEY_LAST_NAME): vol.All(str, vol.Length(min=1)),
    vol.Required(KEY_PASSWORD): SET_PASSWORD_SCHEMA,
})
@json_response()
def register(data):
    existing_user: Optional[User] = User.query.filter_by(email=data[KEY_EMAIL]).first()
    if existing_user is not None:
        if existing_user.email_confirmed:
            raise Conflict("A user with that email already exists, resend confirmation mail?")
        raise Conflict("A user with that email already exists")

    try:
        user = User(
            email=data[KEY_EMAIL],
            first_name=data[KEY_FIRST_NAME],
            last_name=data[KEY_LAST_NAME],
        )
        user.set_password(data[KEY_PASSWORD])
        user.last_password_change_at = utcnow()
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict("A user with that email already exists")

    send_email_verification_code(user)
    return {
        "success": True
    }


@auth_bp.route("/api/auth/request-verification-code", methods=["POST"])
@json_request({
    vol.Required(KEY_EMAIL): vol.Email(),
})
@json_response()
def request_verification_code(data):
    user: Optional[User] = User.query.filter_by(email=data[KEY_EMAIL]).first()
    if user is None:
        raise NotFound("User not found")
    if user.email_confirmed:
        raise BadRequest("Email already verified")
    
    send_email_verification_code(user)
    return {
        "success": True
    }


@auth_bp.route("/api/auth/verify-email", methods=["POST"])
@json_request({
    vol.Required(KEY_TOKEN): str,
})
@json_response()
def verify_email(data):
    # Handles both first email verification and email changes
    token = data[KEY_TOKEN]
    obj: Optional[UserEmailVerificationCode] = UserEmailVerificationCode.query.filter_by(token=token).first()
    if obj is None:
        raise BadRequest("Invalid token")
    
    now = utcnow()
    if now > as_utc(obj.valid_until):
        raise BadRequest("Token is no longer valid")
    if (
        obj.email != obj.user.email
        and obj.user.last_email_confirmed_at is not None
        and as_utc(obj.user.last_email_confirmed_at) > as_utc(obj.created_at)
    ):
        # Email confirmed after this token was created
        raise BadRequest("Token is no longer valid")

    obj.user.email = obj.email
    obj.user.email_confirmed = True
    obj.user.last_email_confirmed_at = now
    try:
        db.session.commit()
    except IntegrityError:
        # Email already registered for different user in meantime
        # can happen while one user requests a email change
        raise BadRequest("User with that email already registered")

    return {
        "success": True
    }


@auth_bp.route("/api/auth/change-password", methods=["POST"])
@login_required
@json_request({
    vol.Optional(KEY_OLD_PASSWORD): str,
    vol.Required(KEY_NEW_PASSWORD): SET_PASSWORD_SCHEMA,
})
@json_response()
def change_password(data):
    if current_user.has_password:
        if KEY_OLD_PASSWORD not in data:
            raise BadRequest("Need to specify old_password.")
        if not current_user.check_password(data[KEY_OLD_PASSWORD]):
            raise BadRequest("Old password does not match")
    current_user.set_password(data[KEY_NEW_PASSWORD])
    current_user.last_password_change_at = utcnow()
    db.session.commit()
    return {
        "success": True
    }


@auth_bp.route("/api/auth/request-password-reset", methods=["POST"])
@json_request({
    vol.Required(KEY_EMAIL): vol.Email(),
})
@json_response()
def request_password_reset(data):
    user = User.query.filter_by(email=data[KEY_EMAIL]).first()
    if user is None:
        raise NotFound("No user with that email address.")
    send_password_reset_email(user)
    return {
        "success": True
    }


@auth_bp.route("/api/auth/reset-password", methods=["POST"])
@json_request({
    vol.Required(KEY_TOKEN): str,
    vol.Required(KEY_PASSWORD): SET_PASSWORD_SCHEMA,
})
@json_response()
def reset_password(data):
    token = data[KEY_TOKEN]
    obj: Optional[UserPasswordResetCode] = UserPasswordResetCode.query.filter_by(token=token).first()
    if obj is None:
        raise BadRequest("Invalid token")
    
    now = utcnow()
    if now > as_utc(obj.valid_until):
        raise BadRequest("Token is no longer valid")
    if (
        obj.email != obj.user.email
        and obj.user.last_password_change_at is not None
        and as_utc(obj.user.last_password_change_at) > as_utc(obj.created_at)
    ):
        # Email confirmed after this token was created
        raise BadRequest("Token is no longer valid")

    obj.user.set_password(data[KEY_PASSWORD])
    obj.user.last_password_change_at = now
    db.session.commit()
    return {
        "success": True
    }


@auth_bp.route("/api/auth/change-email", methods=["POST"])
@login_required
@json_request({
    vol.Optional(KEY_PASSWORD): str,
    vol.Required(KEY_EMAIL): vol.Email(),
})
def change_email(data):
    if current_user.email == data[KEY_EMAIL]:
        raise BadRequest("Email hasn't changed")
    if current_user.has_password:
        if KEY_PASSWORD not in data:
            raise BadRequest("Password is required")
        if not current_user.check_password(data[KEY_PASSWORD]):
            raise BadRequest("Password does not match")
    existing = User.query.filter_byte(email=data[KEY_EMAIL]).first()
    if existing is not None:
        raise BadRequest("Email already registered for a different user.")
    send_change_email_verification_code(current_user, data[KEY_EMAIL])
    return {
        "success": True
    }
