import datetime

import voluptuous as vol  # type: ignore
from flask import Blueprint

from aoiportal.auth_util import get_current_user, login_required
from aoiportal.const import (
    KEY_ADDRESS_STREET,
    KEY_ADDRESS_TOWN,
    KEY_ADDRESS_ZIP,
    KEY_BIRTHDAY,
    KEY_FIRST_NAME,
    KEY_LAST_NAME,
    KEY_PHONE_NR,
    KEY_SCHOOL_ADDRESS,
    KEY_SCHOOL_NAME,
    KEY_ELIGIBILITY
)
from aoiportal.models import User, db  # type: ignore
from aoiportal.web_utils import json_api

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/api/profile/info")
@login_required
@json_api()
def profile_info():
    u: User = get_current_user()

    # For now this will work. lsb = ioi flag, lsb+1 = egoi_flag
    # Todo: make this a proper bitset.
    elig = None

    if u.eligibility == 0:
        elig = "none"
    elif u.eligibility == 1:
        elig = "ioi"
    elif u.eligibility == 3:
        elig = "ioi_egoi"

    return {
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "is_admin": u.is_admin,
        "birthday": u.birthday.isoformat() if u.birthday is not None else None,
        "phone_nr": u.phone_nr,
        "address_street": u.address_street,
        "address_zip": u.address_zip,
        "address_town": u.address_town,
        "school_name": u.school_name,
        "school_address": u.school_address,
        "eligibility": elig,
    }


@profile_bp.route("/api/profile/update", methods=["PUT"])
@login_required
@json_api(
    {
        vol.Optional(KEY_FIRST_NAME): vol.All(str, vol.Length(min=1)),
        vol.Optional(KEY_LAST_NAME): vol.All(str, vol.Length(min=1)),
        vol.Optional(KEY_BIRTHDAY): vol.Any(None, vol.Date()),
        vol.Optional(KEY_PHONE_NR): vol.Any(None, str),
        vol.Optional(KEY_ADDRESS_STREET): vol.Any(None, str),
        vol.Optional(KEY_ADDRESS_ZIP): vol.Any(None, str),
        vol.Optional(KEY_ADDRESS_TOWN): vol.Any(None, str),
        vol.Optional(KEY_SCHOOL_NAME): vol.Any(None, str),
        vol.Optional(KEY_SCHOOL_ADDRESS): vol.Any(None, str),
        vol.Optional(KEY_ELIGIBILITY): vol.Any(None, str)
    }
)
def profile_update(data):
    u: User = get_current_user()

    if KEY_FIRST_NAME in data:
        u.first_name = data[KEY_FIRST_NAME]
    if KEY_LAST_NAME in data:
        u.last_name = data[KEY_LAST_NAME]

    if KEY_BIRTHDAY in data:
        if data[KEY_BIRTHDAY] is None:
            u.birthday = None
        else:
            dt = datetime.datetime.strptime(data[KEY_BIRTHDAY], "%Y-%m-%d")
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

    if KEY_ELIGIBILITY in data:
        # For now this will work. lsb = ioi flag, lsb+1 = egoi_flag
        # Todo: make this a proper bitset.
        if data[KEY_ELIGIBILITY] == "ioi":
            u.eligibility = 1
        elif data[KEY_ELIGIBILITY] == "ioi_egoi":
            u.eligibility = 3
        elif data[KEY_ELIGIBILITY] == "none":
            u.eligibility = 0

    db.session.commit()
    return {"success": True}
