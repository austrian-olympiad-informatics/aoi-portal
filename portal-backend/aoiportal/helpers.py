import secrets
from typing import Optional, cast

from aoiportal.cms_bridge import cms
from aoiportal.models import Contest, Participation, User, db  # type: ignore


def create_cms_user(user: User) -> int:
    res = cms.create_user(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    user.cms_id = res.cms_id
    user.cms_username = res.cms_username
    db.session.commit()
    return user.cms_id


def create_participation(
    user: User, contest: Contest, *, manual_password: Optional[str] = None
) -> Participation:
    if user.cms_id is None:
        create_cms_user(user)

    res = cms.create_participation(
        user_id=cast(int, user.cms_id),
        contest_id=contest.cms_id,
        manual_password=manual_password,
    )
    part = Participation(
        cms_id=res,
        user_id=user.id,
        contest_id=contest.id,
        manual_password=manual_password,
    )
    db.session.add(part)
    db.session.commit()
    return part


def random_password(*, length: int = 12) -> str:
    # excluding lookalive characters "lBGIO0168"
    ALLOWED_CHARS = "abcdefghijkmnopqrstuvwxyzACDEFHJKLMNPQRSTUVWXYZ234579"
    return "".join(secrets.choice(ALLOWED_CHARS) for _ in range(length))
