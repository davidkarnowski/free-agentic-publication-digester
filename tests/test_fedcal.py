"""The federal calendar: statutory holidays, OPM observed shifts, and
the reduced-publishing classification the /today banner renders."""

from fapd import fedcal


def test_2026_statutory_holidays_present():
    days = fedcal.federal_holidays(2026)
    assert days["2026-01-01"] == "New Year's Day"
    assert days["2026-01-19"] == "Birthday of Martin Luther King, Jr."  # 3rd Mon
    assert days["2026-02-16"] == "Washington's Birthday"                # 3rd Mon
    assert days["2026-05-25"] == "Memorial Day"                        # last Mon
    assert days["2026-06-19"] == "Juneteenth National Independence Day"
    assert days["2026-07-04"] == "Independence Day"
    assert days["2026-09-07"] == "Labor Day"                           # 1st Mon
    assert days["2026-10-12"] == "Columbus Day"                        # 2nd Mon
    assert days["2026-11-11"] == "Veterans Day"
    assert days["2026-11-26"] == "Thanksgiving Day"                    # 4th Thu
    assert days["2026-12-25"] == "Christmas Day"


def test_saturday_holiday_observed_preceding_friday():
    # 2026-07-04 is a Saturday -> observed Friday 2026-07-03.
    days = fedcal.federal_holidays(2026)
    assert days["2026-07-03"] == "Independence Day (observed)"


def test_sunday_holiday_observed_following_monday():
    # 2027-07-04 is a Sunday -> observed Monday 2027-07-05.
    days = fedcal.federal_holidays(2027)
    assert days["2027-07-05"] == "Independence Day (observed)"


def test_new_years_saturday_observed_in_previous_december():
    # 2022-01-01 was a Saturday; OPM observed it Friday 2021-12-31.
    assert fedcal.federal_holidays(2021)["2021-12-31"] == "New Year's Day (observed)"


def test_reduced_publishing_weekend():
    ctx = fedcal.reduced_publishing("2026-08-02")  # a Sunday
    assert ctx["kind"] == "weekend"
    assert ctx["name"] == "Sunday"
    assert "not a federal business day" in ctx["note"]


def test_reduced_publishing_holiday_weekday():
    ctx = fedcal.reduced_publishing("2026-11-26")  # Thanksgiving, a Thursday
    assert ctx["kind"] == "holiday"
    assert ctx["name"] == "Thanksgiving Day"
    assert "federal holiday" in ctx["note"]


def test_observed_holiday_on_a_weekday_counts():
    ctx = fedcal.reduced_publishing("2026-07-03")  # Friday, observed July 4th
    assert ctx["kind"] == "holiday"
    assert ctx["name"] == "Independence Day (observed)"


def test_weekend_wins_over_statutory_holiday_on_saturday():
    # July 4, 2026 IS Saturday: report the weekend; the observed Friday
    # carries the holiday closure.
    ctx = fedcal.reduced_publishing("2026-07-04")
    assert ctx["kind"] == "weekend"


def test_ordinary_weekday_is_none():
    assert fedcal.reduced_publishing("2026-08-05") is None  # a Wednesday
    assert fedcal.reduced_publishing("2026-07-06") is None  # Monday after the observed 4th
