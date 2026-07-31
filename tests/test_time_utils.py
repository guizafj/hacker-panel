from datetime import datetime

from src.utils.time_utils import utcnow


def test_utcnow_returns_naive_datetime():
    result = utcnow()
    assert isinstance(result, datetime)
    assert result.tzinfo is None


def test_utcnow_is_close_to_now():
    from datetime import timezone

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    result = utcnow()
    # El helper devuelve datetime naive en UTC; comparar directamente evita
    # depender de la zona horaria del sistema (que rompería .timestamp())
    diff = abs(now_utc - result)
    assert diff.total_seconds() < 5
