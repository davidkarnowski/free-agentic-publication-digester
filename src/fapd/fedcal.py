"""The federal working calendar, mechanically (GUIDE §3: the publication
day is Washington's day; this module knows which of those days Washington
is at work).

Pure functions, zero dependencies, zero I/O. Consumed by the /today
renderer to explain quiet days — most federal publishers issue few or no
documents on weekends and federal holidays, and a live page showing one
item on a Sunday reads as "broken" without saying why (observed live,
2026-08-02: a Sunday /today with exactly one item and no explanation).

The holiday list is the eleven federal holidays of 5 U.S.C. 6103 with
OPM's in-lieu-of observance shifts (a holiday falling on Saturday is
observed the preceding Friday; on Sunday, the following Monday).
Inauguration Day is deliberately excluded: it is a holiday only for
federal employees in the D.C. area and does not close the publishers
nationwide.
"""

import datetime as dt

# (month, day) fixed-date holidays.
_FIXED = (
    (1, 1, "New Year's Day"),
    (6, 19, "Juneteenth National Independence Day"),
    (7, 4, "Independence Day"),
    (11, 11, "Veterans Day"),
    (12, 25, "Christmas Day"),
)

# (month, weekday, ordinal, name): ordinal >= 1 counts from the month's
# start; -1 is the last such weekday. weekday is Monday=0 (date.weekday()).
_FLOATING = (
    (1, 0, 3, "Birthday of Martin Luther King, Jr."),
    (2, 0, 3, "Washington's Birthday"),
    (5, 0, -1, "Memorial Day"),
    (9, 0, 1, "Labor Day"),
    (10, 0, 2, "Columbus Day"),
    (11, 3, 4, "Thanksgiving Day"),
)


def _nth_weekday(year, month, weekday, ordinal):
    if ordinal > 0:
        first = dt.date(year, month, 1)
        offset = (weekday - first.weekday()) % 7
        return first + dt.timedelta(days=offset + 7 * (ordinal - 1))
    next_month = dt.date(year + (month == 12), month % 12 + 1, 1)
    last = next_month - dt.timedelta(days=1)
    return last - dt.timedelta(days=(last.weekday() - weekday) % 7)


def federal_holidays(year):
    """{'YYYY-MM-DD': name} for one year — statutory dates plus observed
    shifts. An observed entry carries "(observed)" in its name; the
    statutory Saturday/Sunday date is included too (it is still the
    holiday, and it is already a non-publishing day as a weekend)."""
    days = {}
    for month, day, name in _FIXED:
        date = dt.date(year, month, day)
        days[date.isoformat()] = name
        if date.weekday() == 5:  # Saturday -> preceding Friday
            days[(date - dt.timedelta(days=1)).isoformat()] = f"{name} (observed)"
        elif date.weekday() == 6:  # Sunday -> following Monday
            days[(date + dt.timedelta(days=1)).isoformat()] = f"{name} (observed)"
    for month, weekday, ordinal, name in _FLOATING:
        days[_nth_weekday(year, month, weekday, ordinal).isoformat()] = name
    # A January 1 falling on Saturday is observed on the PREVIOUS year's
    # December 31; make each year's table self-contained by looking one
    # year ahead.
    next_jan1 = dt.date(year + 1, 1, 1)
    if next_jan1.weekday() == 5:
        days[dt.date(year, 12, 31).isoformat()] = "New Year's Day (observed)"
    return days


_WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                  "Saturday", "Sunday")


def reduced_publishing(date_str):
    """Why `date_str` (a publication-clock day, 'YYYY-MM-DD') is a
    reduced-publishing day, or None for an ordinary federal business day.

    Returns {"kind": "weekend"|"holiday", "name": ..., "note": ...} —
    the note is one neutral, factual sentence shared by the /today banner
    and today.json's day_context field, so the human and agent surfaces
    can never say different things."""
    date = dt.date.fromisoformat(date_str)
    holidays = federal_holidays(date.year)
    name = holidays.get(date_str)
    # A weekend day is reported as the weekend even when it is also the
    # statutory holiday (e.g. 2026-07-04, a Saturday): the observed shift
    # carries the closure, and "Saturday" already explains the quiet.
    if date.weekday() >= 5:
        day_name = _WEEKDAY_NAMES[date.weekday()]
        return {
            "kind": "weekend",
            "name": day_name,
            "note": (
                f"{day_name} is not a federal business day. Most federal"
                " publishers issue few or no documents on weekends and"
                " federal holidays; this stream may stay short until the"
                " next business day."
            ),
        }
    if name:
        return {
            "kind": "holiday",
            "name": name,
            "note": (
                f"Today is {name}, a federal holiday. Most federal"
                " publishers issue few or no documents on federal"
                " holidays; this stream may stay short until the next"
                " business day."
            ),
        }
    return None
