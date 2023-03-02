import collections
import json
from typing import Optional

import voluptuous as vol  # type: ignore
from flask import Blueprint, current_app

from aoiportal.auth_util import get_current_user
from aoiportal.const import KEY_SECRET
from aoiportal.error import AOIConflict, AOIUnauthorized
from aoiportal.models import Group, UserDiscordOAuth  # type: ignore
from aoiportal.web_utils import json_api

bot_bp = Blueprint("bot", __name__)


@bot_bp.route("/api/bot/discord", methods=["POST"])
@json_api(
    {
        vol.Required(KEY_SECRET): str,
    }
)
def getData(data):
    if get_current_user() is not None:
        raise AOIConflict("This is for bots. Are you a bot?")

    if data[KEY_SECRET] != current_app.config["DISCORD_BOT_SECRET"]:
        raise AOIUnauthorized("Wrong secret!")

    wien: Optional[Group] = Group.query.filter_by(name="camp-wien").first()
    woergl: Optional[Group] = Group.query.filter_by(name="camp-woergl").first()
    ioi: Optional[Group] = Group.query.filter_by(name="ioi").first()
    ceoi: Optional[Group] = Group.query.filter_by(name="ceoi").first()
    egoi: Optional[Group] = Group.query.filter_by(name="egoi").first()

    ret = collections.defaultdict(int)

    for u in wien.users:
        dis: Optional[UserDiscordOAuth] = UserDiscordOAuth.query.filter_by(
            user_id=u.id
        ).first()
        if dis is not None:
            ret[dis.discord_id] += 16

    for u in woergl.users:
        dis: Optional[UserDiscordOAuth] = UserDiscordOAuth.query.filter_by(
            user_id=u.id
        ).first()
        if dis is not None:
            ret[dis.discord_id] += 8

    for u in ioi.users:
        dis: Optional[UserDiscordOAuth] = UserDiscordOAuth.query.filter_by(
            user_id=u.id
        ).first()
        if dis is not None:
            ret[dis.discord_id] += 4

    for u in ceoi.users:
        dis: Optional[UserDiscordOAuth] = UserDiscordOAuth.query.filter_by(
            user_id=u.id
        ).first()
        if dis is not None:
            ret[dis.discord_id] += 2

    for u in egoi.users:
        dis: Optional[UserDiscordOAuth] = UserDiscordOAuth.query.filter_by(
            user_id=u.id
        ).first()
        if dis is not None:
            ret[dis.discord_id] += 1

    return json.dumps(ret)
