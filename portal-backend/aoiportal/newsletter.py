import hmac
import secrets
import urllib.parse
from typing import Optional

import voluptuous as vol  # type: ignore
from flask import Blueprint, current_app, render_template
from sqlalchemy.exc import IntegrityError

from aoiportal.const import KEY_EMAIL, KEY_TOKEN
from aoiportal.error import AOIBadRequest, AOIConflict
from aoiportal.mail import Address, send_email
from aoiportal.models import NewsletterSubscription, db  # type: ignore
from aoiportal.web_utils import json_api

newsletter_bp = Blueprint("newsletter", __name__)


def gen_unsubscribe_link(sub: NewsletterSubscription) -> str:
    base_url = current_app.config["BASE_URL"]
    return f"{base_url}/newsletter/unsubscribe?" + urllib.parse.urlencode(
        {
            "email": sub.email,
            "token": sub.unsubscribe_token,
        }
    )


@newsletter_bp.route("/api/newsletter/signup", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_EMAIL): vol.Email(),
    }
)
def newsletter_signup(data):
    sub = NewsletterSubscription(
        email=data[KEY_EMAIL],
        unsubscribe_token=secrets.token_urlsafe(12),
    )
    db.session.add(sub)
    try:
        db.session.commit()
    except IntegrityError:
        raise AOIConflict("Already signed up")

    unsubscribe_link = gen_unsubscribe_link(sub)
    send_email(
        to=Address(sub.email),
        subject="TODO Thanks for signing up",
        content_html=render_template("newsletter_signup.html"),
        unsubscribe_link=unsubscribe_link,
    )
    return {"success": True}


@newsletter_bp.route("/api/newsletter/unsubscribe", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_EMAIL): vol.Email(),
        vol.Required(KEY_TOKEN): str,
    }
)
def newsletter_unsubscribe(data):
    sub: Optional[NewsletterSubscription] = NewsletterSubscription.query.filter_by(
        email=data[KEY_EMAIL]
    ).first()
    if sub is None:
        raise AOIBadRequest("Invalid email or token")
    if not hmac.compare_digest(sub.email, data[KEY_TOKEN]):
        raise AOIBadRequest("Invalid email or token")
    db.session.delete(sub)
    db.session.commit()
    return {"success": True}
