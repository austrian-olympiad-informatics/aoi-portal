import datetime

from flask import Blueprint
from flask_login import login_required, current_user
import voluptuous as vol
from aoiportal.const import KEY_ADDRESS_STREET, KEY_ADDRESS_TOWN, KEY_ADDRESS_ZIP, KEY_BIRTHDAY, KEY_FIRST_NAME, KEY_LAST_NAME, KEY_PHONE_NR, KEY_SCHOOL_ADDRESS, KEY_SCHOOL_NAME

from aoiportal.web_utils import json_request, json_response
from aoiportal.models import User, db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/api/profile/info")
@login_required
@json_response()
def profile_info():
    u: User = current_user
    return {
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "last_login": u.last_login.isoformat() if u.last_login is not None else None,
        "is_admin": u.is_admin,
        "birthday": u.birthday.isoformat() if u.birthday is not None else None,
        "phone_nr": u.phone_nr,
        "address_street": u.address_street,
        "address_zip": u.address_zip,
        "address_town": u.address_town,
        "school_name": u.school_name,
        "school_address": u.school_address,
    }

@profile_bp.route("/api/profile/update", methods=["PUT"])
@login_required
@json_request({
    vol.Optional(KEY_FIRST_NAME): vol.All(str, vol.Length(min=1)),
    vol.Optional(KEY_LAST_NAME): vol.All(str, vol.Length(min=1)),
    vol.Optional(KEY_BIRTHDAY): vol.Date(),
    vol.Optional(KEY_PHONE_NR): str,
    vol.Optional(KEY_ADDRESS_STREET): str,
    vol.Optional(KEY_ADDRESS_ZIP): str,
    vol.Optional(KEY_ADDRESS_TOWN): str,
    vol.Optional(KEY_SCHOOL_NAME): str,
    vol.Optional(KEY_SCHOOL_ADDRESS): str,
})
@json_response()
def profile_update(data):
    u: User = current_user

    if KEY_FIRST_NAME in data:
        u.first_name = data[KEY_FIRST_NAME]
    if KEY_LAST_NAME in data:
        u.last_name = data[KEY_LAST_NAME]
    
    if KEY_BIRTHDAY in data:
        dt = datetime.datetime.strptime("%Y-%m-%d", data[KEY_BIRTHDAY])
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

    db.session.commit()
    return {
        "success": True
    }
