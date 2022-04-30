from flask import Blueprint
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequest, NotFound
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from aoiportal.models import db, Contest, Participation
from aoiportal.web_utils import json_response
from aoiportal.cms_bridge import cms
from aoiportal.helpers import create_participation

contests_bp = Blueprint("contests", __name__)


@contests_bp.route("/api/contests")
@login_required
@json_response()
def list_contests():
    q = (
        db.session.query(Contest, Participation)
            .join(Participation, 
                and_(Contest.id == Participation.contest_id, Participation.user_id == current_user.id)
            , isouter=True)
    )
    ret = []
    for contest, part in q:
        joined = part is not None
        can_join = False
        if not joined:
            can_join = contest.public
        if not joined and not can_join:
            continue

        ret.append({
            "id": contest.id,
            "name": contest.cms_name,
            "description": contest.cms_description,
            "joined": joined,
            "can_join": can_join,
        })

    return ret


@contests_bp.route("/api/contests/<int:contest_id>/join", methods=["POST"])
@login_required
@json_response()
def join_contest(contest_id: int):
    existing_part = (
        db.session.query(Participation)
        .filter(Participation.contest_id==contest_id)
        .filter(Participation.user_id==current_user.id)
        .first()
    )
    if existing_part is not None:
        raise BadRequest("Contest already joined.")
    
    contest = Contest.query.filter_by(id=contest_id).first()
    can_join = contest is not None and contest.public
    if not can_join:
        raise NotFound("Contest not found")

    create_participation(current_user, contest)

    if contest.auto_add_to_group is not None:
        try:
            current_user.groups.append(contest.auto_add_to_group)
            db.session.commit()
        except IntegrityError:
            # already in group
            pass

    return {
        "success": True
    }
