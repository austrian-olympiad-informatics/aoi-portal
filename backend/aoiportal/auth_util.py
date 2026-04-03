import base64
import functools
import logging
import secrets
from datetime import timedelta
from typing import Optional, Tuple

import bcrypt
import jwt
import nacl.exceptions
import nacl.secret
from flask import current_app, g, request
from sqlalchemy.orm import joinedload  # type: ignore

from aoiportal.error import (
    ERROR_ADMIN_REQUIRED,
    ERROR_LOGIN_REQUIRED,
    AOIForbidden,
    AOIUnauthorized,
)
from aoiportal.models import Contest, Participation, User, UserSession, db  # type: ignore
from aoiportal.utils import as_utc, utcnow

_G_CURRENT_SESSION_KEY = "_aoi_auth_current_session"
_G_PROXY_AUTH_KEY = "_aoi_proxy_auth"
_G_PROXY_AUTH_ERROR_KEY = "_aoi_proxy_auth_error"
_G_PROXY_USER_KEY = "_aoi_proxy_user"
_G_PROXY_CONTEST_KEY = "_aoi_proxy_contest"

_logger = logging.getLogger(__name__)


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


def _get_proxy_auth_header() -> Optional[str]:
    if current_app.config.get("PROXY_AUTH_JWT_PUBLIC_KEY") is None:
        return None
    return request.headers.get("X-Proxy-Auth")


def has_proxy_header() -> bool:
    return _get_proxy_auth_header() is not None


def _load_proxy_auth() -> None:
    """Attempt to authenticate via proxy JWT header.

    Sets g flags for proxy auth state regardless of success/failure.
    On failure (bad token), sets the error flag so the frontend can
    show an error page instead of the login form.
    """
    if hasattr(g, _G_PROXY_AUTH_KEY):
        return

    setattr(g, _G_PROXY_AUTH_KEY, False)
    setattr(g, _G_PROXY_AUTH_ERROR_KEY, False)
    setattr(g, _G_PROXY_USER_KEY, None)
    setattr(g, _G_PROXY_CONTEST_KEY, None)

    token_str = _get_proxy_auth_header()
    if token_str is None:
        return

    public_key_pem = current_app.config["PROXY_AUTH_JWT_PUBLIC_KEY"]

    try:
        payload = jwt.decode(
            token_str,
            public_key_pem,
            algorithms=["RS256", "ES256"],
            options={"require": ["sub", "contest", "exp"]},
            leeway=30,
        )
    except jwt.PyJWTError as e:
        _logger.warning("Proxy auth JWT validation failed: %s", e)
        setattr(g, _G_PROXY_AUTH_ERROR_KEY, True)
        return

    cms_username = payload.get("sub")
    cms_name = payload.get("contest")
    if not cms_username or not cms_name:
        _logger.warning("Proxy auth JWT missing sub or contest claim")
        setattr(g, _G_PROXY_AUTH_ERROR_KEY, True)
        return

    user: Optional[User] = User.query.filter_by(cms_username=cms_username).first()
    if user is None:
        _logger.warning("Proxy auth: user with cms_username=%r not found", cms_username)
        setattr(g, _G_PROXY_AUTH_ERROR_KEY, True)
        return

    contest: Optional[Contest] = Contest.query.filter_by(cms_name=cms_name).first()
    if contest is None or contest.deleted:
        _logger.warning("Proxy auth: contest with cms_name=%r not found", cms_name)
        setattr(g, _G_PROXY_AUTH_ERROR_KEY, True)
        return

    # Auto-join: create participation if missing
    part: Optional[Participation] = (
        db.session.query(Participation)
        .filter(Participation.contest_id == contest.id)
        .filter(Participation.user_id == user.id)
        .first()
    )
    if part is None:
        from aoiportal.helpers import create_participation
        create_participation(user, contest)

    setattr(g, _G_PROXY_AUTH_KEY, True)
    setattr(g, _G_PROXY_USER_KEY, user)
    setattr(g, _G_PROXY_CONTEST_KEY, contest)


def is_proxy_auth() -> bool:
    _load_proxy_auth()
    return getattr(g, _G_PROXY_AUTH_KEY, False)


def has_proxy_auth_error() -> bool:
    _load_proxy_auth()
    return getattr(g, _G_PROXY_AUTH_ERROR_KEY, False)


def get_proxy_contest() -> Optional[Contest]:
    _load_proxy_auth()
    return getattr(g, _G_PROXY_CONTEST_KEY, None)


def get_current_user() -> Optional[User]:
    # Proxy auth takes full precedence over session auth
    if is_proxy_auth():
        return getattr(g, _G_PROXY_USER_KEY, None)
    if has_proxy_auth_error():
        return None
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
        if request.method != "OPTIONS" and get_current_user() is None:
            raise AOIUnauthorized(
                "Need to log in first",
                error_code=ERROR_LOGIN_REQUIRED,
            )
        return fn(*args, **kwargs)

    return decorated


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
