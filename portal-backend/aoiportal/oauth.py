import json
from typing import Optional
import urllib.parse

from flask import Blueprint, current_app
import voluptuous as vol
import requests

from aoiportal.const import KEY_CODE, KEY_REDIRECT_URI
from aoiportal.error import AOIBadRequest, AOIConflict
from aoiportal.utils import utcnow
from aoiportal.web_utils import json_api
from aoiportal.auth_util import get_current_user, create_session
from aoiportal.models import UserGoogleOAuth, db, User, UserGitHubOAuth

oauth_bp = Blueprint("oauth", __name__)

@oauth_bp.route("/api/auth/oauth/github/authorize-url")
@json_api()
def github_authorize_url():
    uri = "https://github.com/login/oauth/authorize"
    url = uri + '?' + urllib.parse.urlencode({
        "client_id": current_app.config["GITHUB_OAUTH_CLIENT_ID"],
        "scope": "user:email",
    })
    return {
        "url": url,
    }


@oauth_bp.route("/api/oauth/github/auth", methods=["POST"])
@json_api({
    vol.Required(KEY_CODE): str,
})
def github_auth(data):
    if get_current_user() is not None:
        raise AOIConflict("Already logged in")
    access_token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": current_app.config["GITHUB_OAUTH_CLIENT_ID"],
        "client_secret": current_app.config["GITHUB_OAUTH_CLIENT_SECRET"],
        "code": data[KEY_CODE],
    }
    rsess = requests.Session()
    resp = rsess.post(access_token_url, json=payload, headers={"Accept": "application/json"})
    if resp.status_code != 200 or "error" in resp:
        raise AOIBadRequest("Invalid token")
    js = resp.json()
    access_token = js["access_token"]

    obj: Optional[UserGitHubOAuth] = UserGitHubOAuth.query.filter_by(access_token=access_token).first()
    if obj is not None:
        # User already has oauth linked, log them in
        _, token = create_session(obj.user)
        return {
            "success": True,
            "token": token,
        }

    # https://docs.github.com/en/rest/users/users#get-the-authenticated-user
    resp = rsess.get("https://api.github.com/user", headers={'Authorization': 'token ' + access_token})
    resp.raise_for_status()
    user_info = resp.json()
    user_id: int = user_info["id"]
    user_login: str = user_info["login"]
    user_name: Optional[str] = user_info["name"]

    # https://docs.github.com/en/rest/users/emails#list-email-addresses-for-the-authenticated-user
    resp = rsess.get("https://api.github.com/user/emails", headers={'Authorization': 'token ' + access_token})
    resp.raise_for_status()
    emails_info = resp.json()
    filtered_emails = [
        e["email"]
        for e in emails_info
        if e["primary"] and e["verified"]
    ]
    user_email = filtered_emails[0]

    oauth = UserGitHubOAuth(
        created_at=utcnow(),
        access_token=access_token,
        extra_data=json.dumps({
            "user_info": user_info,
            "emails_info": emails_info,
        }),
    )

    user: Optional[User] = User.query.filter_by(email=user_email).first()
    if user is not None:
        # User already exists, just link the token
        oauth.user = user
        db.session.add(oauth)
        db.session.commit()

        _, token = create_session(user)
        return {
            "success": True,
            "token": token,
        }

    if user_name is not None:
        parts = user_name.split(maxsplit=1)
        if len(parts) == 2:
            first_name, last_name = parts
        else:
            first_name, last_name = parts[0], ""
    else:
        first_name, last_name = user_login, ""

    # User does not exist
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=user_email,
        password_hash=None,
        created_at=utcnow(),
    )
    oauth.user = user
    db.session.add(user)
    db.session.add(oauth)
    db.session.commit()

    _, token = create_session(user)
    return {
        "success": True,
        "token": token,
    }


@oauth_bp.route("/api/auth/oauth/google/authorize-url")
@json_api()
def google_authorize_url():
    uri = "https://accounts.google.com/o/oauth2/v2/auth"
    url = uri + '?' + urllib.parse.urlencode({
        "client_id": current_app.config["GOOGLE_OAUTH_CLIENT_ID"],
        "scope": "profile email",
        "response_type": "code",
    })
    return {
        "url": url,
    }


@oauth_bp.route("/api/oauth/google/auth", methods=["POST"])
@json_api({
    vol.Required(KEY_CODE): str,
    vol.Required(KEY_REDIRECT_URI): str,
})
def google_auth(data):
    if get_current_user() is not None:
        raise AOIConflict("Already logged in")
    access_token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": current_app.config["GOOGLE_OAUTH_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
        "code": data[KEY_CODE],
        "grant_type": "authorization_code",
        "redirect_uri": data[KEY_REDIRECT_URI],
    }
    rsess = requests.Session()
    resp = rsess.post(access_token_url, data=payload, headers={"Accept": "application/json"})
    if resp.status_code != 200:
        raise AOIBadRequest("Invalid token")
    js = resp.json()
    access_token = js["access_token"]

    obj: Optional[UserGoogleOAuth] = UserGoogleOAuth.query.filter_by(access_token=access_token).first()
    if obj is not None:
        # User already has oauth linked, log them in
        _, token = create_session(obj.user)
        return {
            "success": True,
            "token": token,
        }

    resp = rsess.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={'Authorization': 'Bearer ' + access_token})
    resp.raise_for_status()
    user_info = resp.json()
    user_id = user_info["id"]
    first_name = user_info["given_name"]
    last_name = user_info["family_name"]
    user_email = user_info["email"]
    if not user_info.get("verified_email", True):
        raise AOIBadRequest("Email not verified")

    oauth = UserGoogleOAuth(
        created_at=utcnow(),
        access_token=access_token,
        extra_data=json.dumps({
            "user_info": user_info,
        }),
    )

    user: Optional[User] = User.query.filter_by(email=user_email).first()
    if user is not None:
        # User already exists, just link the token
        oauth.user = user
        db.session.add(oauth)
        db.session.commit()

        _, token = create_session(user)
        return {
            "success": True,
            "token": token,
        }

    # User does not exist
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=user_email,
        password_hash=None,
        created_at=utcnow(),
    )
    oauth.user = user
    db.session.add(user)
    db.session.add(oauth)
    db.session.commit()

    _, token = create_session(user)
    return {
        "success": True,
        "token": token,
    }
