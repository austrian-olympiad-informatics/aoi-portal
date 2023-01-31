import json
import urllib.parse
from typing import Optional

import requests
import voluptuous as vol  # type: ignore
from flask import Blueprint, current_app

from aoiportal.auth_util import create_session, get_current_user
from aoiportal.const import KEY_CODE, KEY_REDIRECT_URI
from aoiportal.error import AOIBadRequest, AOIConflict, AOIUnauthorized
from aoiportal.models import User, UserGitHubOAuth, UserDiscordOAuth, UserGoogleOAuth, db  # type: ignore
from aoiportal.utils import utcnow
from aoiportal.web_utils import json_api

oauth_bp = Blueprint("oauth", __name__)


@oauth_bp.route("/api/auth/oauth/github/authorize-url")
@json_api()
def github_authorize_url():
    uri = "https://github.com/login/oauth/authorize"
    url = (
        uri
        + "?"
        + urllib.parse.urlencode(
            {
                "client_id": current_app.config["GITHUB_OAUTH_CLIENT_ID"],
                "scope": "user:email",
            }
        )
    )
    return {
        "url": url,
    }


@oauth_bp.route("/api/oauth/github/auth", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_CODE): str,
    }
)
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
    resp = rsess.post(
        access_token_url, json=payload, headers={"Accept": "application/json"}
    )
    if resp.status_code != 200 or "error" in resp:
        raise AOIBadRequest("Invalid token")
    js = resp.json()
    access_token = js["access_token"]

    obj: Optional[UserGitHubOAuth] = UserGitHubOAuth.query.filter_by(
        access_token=access_token
    ).first()
    if obj is not None:
        # User already has oauth linked, log them in
        _, token = create_session(obj.user)
        return {
            "success": True,
            "token": token,
        }

    # https://docs.github.com/en/rest/users/users#get-the-authenticated-user
    resp = rsess.get(
        "https://api.github.com/user",
        headers={"Authorization": "token " + access_token},
    )
    resp.raise_for_status()
    user_info = resp.json()
    user_login: str = user_info["login"]
    user_name: Optional[str] = user_info["name"]

    # https://docs.github.com/en/rest/users/emails#list-email-addresses-for-the-authenticated-user
    resp = rsess.get(
        "https://api.github.com/user/emails",
        headers={"Authorization": "token " + access_token},
    )
    resp.raise_for_status()
    emails_info = resp.json()
    filtered_emails = [
        e["email"] for e in emails_info if e["primary"] and e["verified"]
    ]
    user_email = filtered_emails[0]

    oauth = UserGitHubOAuth(
        created_at=utcnow(),
        access_token=access_token,
        extra_data=json.dumps(
            {
                "user_info": user_info,
                "emails_info": emails_info,
            }
        ),
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


@oauth_bp.route("/api/auth/oauth/discord/authorize-url")
@json_api()
def discord_authorize_url():
    uri = "https://discord.com/oauth2/authorize"
    url = (
        uri
        + "?"
       + urllib.parse.urlencode(
            {
                "response_type": "code",
                "client_id": current_app.config["DISCORD_OAUTH_CLIENT_ID"],
                "scope": "identify",
                "prompt": "consent",
            }
        )
    )
    return {
        "url": url,
    }

@oauth_bp.route("/api/oauth/discord/auth", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_CODE): str,
        vol.Required(KEY_REDIRECT_URI): str
    }
)
def discord_auth(data):
    if get_current_user() is None:
        raise AOIUnauthorized("You are not logged in.")
    
    access_token_url = "https://discord.com/api/oauth2/token"
    payload = {
        "client_id": current_app.config["DISCORD_OAUTH_CLIENT_ID"],
        "client_secret": current_app.config["DISCORD_OAUTH_CLIENT_SECRET"],
        "code": data[KEY_CODE],
        "grant_type": "authorization_code",
        "redirect_uri": data[KEY_REDIRECT_URI],
    }

    rsess = requests.Session()
    resp = rsess.post(
        access_token_url, data=payload, headers={"Accept": "application/json"}
    )
    if resp.status_code != 200:
        raise AOIBadRequest("Invalid token")
    js = resp.json()
    access_token = js["access_token"]

    obj: Optional[UserDiscordOAuth] = UserDiscordOAuth.query.filter_by(
        access_token=access_token
    ).first()
    if obj is not None:
        # User already has oauth linked, do nothing
        data = json.loads(obj.extra_data)

        if obj.user_id != get_current_user().id:
            raise AOIConflict("Discord username already linked to another account")

        return {
            "success": True,
            "user_id": obj.discord_id,
            "username": data["user_info"]["username"] + "#" + data["user_info"]["discriminator"]
        }

    resp = rsess.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": js["token_type"] + " " + access_token},
    )
    resp.raise_for_status()
    user_info = resp.json()
    
    oauth = UserDiscordOAuth(
        discord_id=user_info["id"],
        user_id=get_current_user().id,
        created_at=utcnow(),
        access_token=access_token,
        token_type=js["token_type"],
        durationInSeconds=js["expires_in"],
        extra_data=json.dumps(
            {
                "user_info": user_info,
            }
        ),
    )

    db.session.add(oauth)
    db.session.commit()

    return {
        "success": True,
        "user_id": user_info["id"],
        "username": user_info["username"] + "#" + user_info["discriminator"] 
    }



@oauth_bp.route("/api/auth/oauth/google/authorize-url")
@json_api()
def google_authorize_url():
    uri = "https://accounts.google.com/o/oauth2/v2/auth"
    url = (
        uri
        + "?"
        + urllib.parse.urlencode(
            {
                "client_id": current_app.config["GOOGLE_OAUTH_CLIENT_ID"],
                "scope": "profile email",
                "response_type": "code",
            }
        )
    )
    return {
        "url": url,
    }


@oauth_bp.route("/api/oauth/google/auth", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_CODE): str,
        vol.Required(KEY_REDIRECT_URI): str,
    }
)
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
    resp = rsess.post(
        access_token_url, data=payload, headers={"Accept": "application/json"}
    )
    if resp.status_code != 200:
        raise AOIBadRequest("Invalid token")
    js = resp.json()
    access_token = js["access_token"]

    obj: Optional[UserGoogleOAuth] = UserGoogleOAuth.query.filter_by(
        access_token=access_token
    ).first()
    if obj is not None:
        # User already has oauth linked, log them in
        _, token = create_session(obj.user)
        return {
            "success": True,
            "token": token,
        }

    resp = rsess.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": "Bearer " + access_token},
    )
    resp.raise_for_status()
    user_info = resp.json()
    first_name = user_info["given_name"]
    last_name = user_info["family_name"]
    user_email = user_info["email"]
    if not user_info.get("verified_email", True):
        raise AOIBadRequest("Email not verified")

    oauth = UserGoogleOAuth(
        created_at=utcnow(),
        access_token=access_token,
        extra_data=json.dumps(
            {
                "user_info": user_info,
            }
        ),
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
