import datetime


UTC = datetime.timezone.utc


def utcnow():
    return datetime.datetime.now(UTC)


def as_utc(dt: datetime.datetime) -> datetime.datetime:
    if dt.tzinfo == UTC:
        return dt
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)
