import logging
import re
from datetime import datetime, timezone

from dateutil.tz.win import valuestodict

logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
STATECODE_MAP = {"active": 0, "inactive":1}
DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%SZ",   # 2023-01-15T10:30:00Z
    "%Y-%m-%d %H:%M:%S",    # 2023-02-20 14:15:00
    "%Y-%m-%d",             # 2023-03-05
]

def split_name(full_name: str) -> tuple[str, str]:
    """Split a full name into (firstname, lastname).
    First word = firstname, the rest = lastname."""
    parts = (full_name or "").strip().split()
    if not parts:
        return "", ""
    return parts[0], " ".join(parts[1:])


def normalize_email(email: str, record_id: str = "") -> str | None:
    """Lowercase and validate an email. Invalid emails return None and are logged."""
    value = (email or "").strip().lower()
    if EMAIL_PATTERN.match(value):
        return value
    logger.warning("Invalid email for %s: %r -> set to null", record_id, email)
    return None

def parse_datetime(value: str, record_id: str = "") -> str | None:
    """Parse known date formats and return ISO 8601 (YYY-MM-DDTHH:MM:SSZ).
    Assumption: values without timezone are UTC, dates without time are 00:00:00."""
    raw = (value or "").strip()
    for fmt in DATETIME_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue
    logger.warning("Unparsable date for %s: %r -> set to null", record_id, value)
    return None


def map_statecode(status: str, record_id: str = "") -> int | None:
    """Map 'active' -> 0 und 'inactive' -> 1 (case-insensitive). Unknown values return None."""
    key = (status or "").strip().lower()
    if key in STATECODE_MAP:
        return STATECODE_MAP[key]
    logger.warning("Unknown status for %s: %r -> set to null", record_id, status)
    return None