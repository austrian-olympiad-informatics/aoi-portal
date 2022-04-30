from flask import abort, Blueprint
from flask_login import current_user, login_user
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.exc import NoResultFound, IntegrityError
from aoiportal.models import db, User, OAuth
from aoiportal.utils import utcnow

oauth_bp = Blueprint("oauth", __name__)

github_bp = make_github_blueprint(
    scope="user:email",
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
)
oauth_bp.register_blueprint(github_bp, url_prefix="/api/oauth")

# create/login local user on successful OAuth login
@oauth_authorized.connect_via(github_bp)
def github_logged_in(blueprint, token):
    if not current_user.is_anonymous:
        abort(400, description="Already logged in")
    if not token:
        abort(400, description="Failed to log in with GitHub.")

    resp = blueprint.session.get("/user")
    if not resp.ok:
        abort(500, description="Failed to fetch user info from GitHub.")

    github_info = resp.json()
    github_user_id = str(github_info["id"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name, provider_user_id=github_user_id
    )
    try:
        oauth = query.one()
    except NoResultFound:
        github_user_login = str(github_info["login"])
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=github_user_id,
            provider_user_login=github_user_login,
            token=token,
        )

    if oauth.user:
        # user is not logged in, but token exists
        # -> user wants to log in
        oauth.user.last_login = utcnow()
        db.session.commit()
        login_user(oauth.user)
        return False

    # not logged in, and token is new
    # -> create a new user (email verified), and log in
    name = github_info["name"]
    parts = name.split(maxsplit=1)
    if len(parts) == 2:
        first_name, last_name = parts
    else:
        first_name, last_name = parts[0], ""
    resp = blueprint.session.get("/user/emails")
    if not resp.ok:
        abort(500, description="Failed to fetch user emails from GitHub.")

    email_info = resp.json()
    email = next(email["email"] for email in email_info if email["primary"])

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        email_confirmed=True,
    )
    oauth.user = user
    user.last_login = utcnow()
    db.session.add_all([user, oauth])
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, description="Email already registered")
    login_user(user)

    # Indicate that the backend shouldn't manage creating the OAuth object
    # in the database, since we've already done so!
    return False


# notify on OAuth provider error
@oauth_error.connect_via(github_bp)
def github_error(blueprint, message, response):
    msg = f"OAuth error from {blueprint.name}! message={message} response={response}"
    return abort(500, description=msg)


google_blueprint = make_google_blueprint(
    scope=["profile", "email"],
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user),
)
oauth_bp.register_blueprint(google_blueprint, url_prefix="/api/oauth")


@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not current_user.is_anonymous:
        abort(400, description="Already logged in")
    if not token:
        abort(400, description="Failed to log in with GitHub.")

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        abort(500, description="Failed to fetch user info from GitHub.")

    google_info = resp.json()
    google_user_id = google_info["id"]

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name, provider_user_id=google_user_id
    )
    try:
        oauth = query.one()
    except NoResultFound:
        google_user_login = str(google_info["email"])
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            provider_user_login=google_user_login,
            token=token,
        )

    if oauth.user:
        # user is not logged in, but token exists
        # -> user wants to log in
        oauth.user.last_login = utcnow()
        db.session.commit()
        login_user(oauth.user)
        return False

    # not logged in, and token is new
    # -> create a new user (email verified), and log in
    first_name = google_info["given_name"]
    last_name = google_info["family_name"]
    email = google_info["email"]

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        email_confirmed=True,
    )
    oauth.user = user
    user.last_login = utcnow()
    db.session.add_all([user, oauth])
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, description="Email already registered")
    login_user(user)

    # Indicate that the backend shouldn't manage creating the OAuth object
    # in the database, since we've already done so!
    return False


# notify on OAuth provider error
@oauth_error.connect_via(google_blueprint)
def google_error(blueprint, message, response):
    msg = f"OAuth error from {blueprint.name}! message={message} response={response}"
    return abort(500, description=msg)
