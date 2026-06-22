"""Standard US holiday/observance calc — mirrors the /today skill's list."""

from datetime import date


def _nth_weekday(year, month, weekday, n):
    """nth (1-indexed) occurrence of `weekday` (Mon=0) in year/month."""
    d = date(year, month, 1)
    offset = (weekday - d.weekday()) % 7
    return date(year, month, 1 + offset + 7 * (n - 1))


def _last_weekday_of_month(year, month, weekday):
    from calendar import monthrange
    last_day = monthrange(year, month)[1]
    d = date(year, month, last_day)
    while d.weekday() != weekday:
        d = date(d.year, d.month, d.day - 1)
    return d


def standard_holiday(today: date) -> str | None:
    year = today.year
    fixed = {
        (1, 1): "New Year's Day",
        (2, 14): "Valentine's Day",
        (7, 4): "Independence Day",
        (10, 31): "Halloween",
        (11, 11): "Veterans Day",
        (12, 25): "Christmas Day",
        (12, 31): "New Year's Eve",
    }
    if (today.month, today.day) in fixed:
        return fixed[(today.month, today.day)]

    computed = {
        "Mother's Day": _nth_weekday(year, 5, 6, 2),  # 2nd Sunday in May
        "Memorial Day": _last_weekday_of_month(year, 5, 0),  # last Monday in May
        "Father's Day": _nth_weekday(year, 6, 6, 3),  # 3rd Sunday in June
        "Labor Day": _nth_weekday(year, 9, 0, 1),  # 1st Monday in September
        "Thanksgiving": _nth_weekday(year, 11, 3, 4),  # 4th Thursday in November
    }
    for name, d in computed.items():
        if d == today:
            return name
    return None
