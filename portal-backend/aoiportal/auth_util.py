import base64
import functools
import secrets
from datetime import timedelta
from typing import Optional, Tuple

import bcrypt
import nacl.exceptions
import nacl.secret
from flask import current_app, g, request
from sqlalchemy.orm import joinedload
from werkzeug.local import LocalProxy

from aoiportal.error import ERROR_LOGIN_REQUIRED, AOIUnauthorized
from aoiportal.models import User, UserSession, db
from aoiportal.utils import as_utc, utcnow

_G_CURRENT_SESSION_KEY = "_aoi_auth_current_session"


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(password: str, password_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash)


def _get_session_secretbox() -> nacl.secret.SecretBox:
    session_token_key = current_app.config["AOI_SESSION_TOKEN_KEY"]
    keybytes = base64.b64decode(session_token_key)
    return nacl.secret.SecretBox(keybytes)


def gen_token_public_private() -> Tuple[str, str]:
    # Send the first tuple item to the user, store the second one in the DB
    # (leverages MAC of ciphertext to authenticate)
    plaintext = secrets.token_urlsafe(24)
    box = _get_session_secretbox()
    ciphertextb = box.encrypt(plaintext.encode())
    ciphertext = base64.urlsafe_b64encode(ciphertextb).decode()
    return (ciphertext, plaintext)


def token_get_private_part(public: str) -> Optional[str]:
    # Counterpart to gen_token_public_private
    try:
        ciphertextb = base64.urlsafe_b64decode(public)
    except ValueError:
        return None
    box = _get_session_secretbox()
    try:
        return box.decrypt(ciphertextb).decode()
    except nacl.exceptions.CryptoError:
        return None


def _load_session() -> Optional[UserSession]:
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return None
    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    plaintext = token_get_private_part(parts[1])
    if plaintext is None:
        return None

    sess: Optional[UserSession] = (
        db.session.query(UserSession)
        .filter(UserSession.token == plaintext)
        .options(joinedload(UserSession.user))
        .first()
    )
    if sess is None:
        return None

    now = utcnow()
    if now < as_utc(sess.created_at):
        return None
    if now > as_utc(sess.valid_until):
        return None

    return sess


def get_current_session() -> Optional[UserSession]:
    if _G_CURRENT_SESSION_KEY not in g:
        setattr(g, _G_CURRENT_SESSION_KEY, _load_session())

    return getattr(g, _G_CURRENT_SESSION_KEY)


def get_current_user() -> Optional[User]:
    sess = get_current_session()
    if sess is None:
        return None
    return sess.user


def create_session(user: User) -> Tuple[UserSession, str]:
    public, private = gen_token_public_private()
    now = utcnow()
    sess = UserSession(
        token=private,
        user=user,
        created_at=now,
        valid_until=now + timedelta(days=30 * 6),
    )
    db.session.add(sess)
    db.session.commit()
    return (sess, public)


def invalidate_session(session: Optional[UserSession] = None):
    db.session.delete(session)
    db.session.commit()


def login_required(fn):
    @functools.wraps(fn)
    def decorated(*args, **kwargs):
        if request.method != "OPTIONS" and get_current_session() is None:
            raise AOIUnauthorized(
                "Need to log in first",
                error_code=ERROR_LOGIN_REQUIRED,
            )
        return fn(*args, **kwargs)

    return decorated
