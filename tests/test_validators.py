import pytest

from src.validators import map_statecode, normalize_email, parse_datetime, split_name

@pytest.mark.parametrize("raw, expected", [
    ("2023-01-15T10:30:00Z", "2023-01-15T10:30:00Z"), # alrteady ISO 8601
    ("2023-02-20 14:15:00", "2023-02-20T14:15:00Z"), # space, no timezone
    ("2023-03-05", "2023-03-05T00:00:00Z"), # date only
])
def test_parse_datetime_normalize_known_formats(raw, expected):
    assert parse_datetime(raw) == expected

def test_parse_datetime_invalid_returns_none():
    assert parse_datetime("not-a-date") is None

def test_normalize_email_lowercase():
    assert normalize_email("JOHN.SMITH@DOMAIN.COM") == "john.smith@domain.com"

@pytest.mark.parametrize("raw", ["invalid-email-format", "", None, "a@b"])
def test_normalize_email_invalid_returns_none(raw):
    assert normalize_email(raw) == None

@pytest.mark.parametrize("raw, expected", [
    ("active", 0), ("inactive", 1), ("ACTIVE", 0), (" Inactive ", 1),
])
def test_map_statecode(raw, expected):
    assert map_statecode(raw) == expected


def test_map_statecode_unknown_returns_none():
    assert map_statecode("deleted") is None


@pytest.mark.parametrize("raw, expected", [
    ("Jane Doe", ("Jane", "Doe")),
    (" Charlie Brown", ("Charlie", "Brown")),       # leading space from raw data
    ("Mary Ann Lee", ("Mary", "Ann Lee")),          # rest goes into lastname
    ("Cher", ("Cher", "")),
    ("", ("", "")),
])
def test_split_name(raw, expected):
    assert split_name(raw) == expected