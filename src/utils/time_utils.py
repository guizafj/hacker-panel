from datetime import datetime, timezone


def utcnow() -> datetime:
    """Devuelve la hora UTC actual como datetime naive.

    datetime.utcnow() está deprecado desde Python 3.12. Este helper conserva
    el comportamiento (naive, en UTC) para ser compatible con columnas
    db.DateTime de SQLAlchemy.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
