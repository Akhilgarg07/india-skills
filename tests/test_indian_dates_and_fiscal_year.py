"""Tests for skills/indian-dates-and-fiscal-year/scripts/fiscal_year.py."""

import datetime as dt
import json
import subprocess
import sys
from zoneinfo import ZoneInfo

import pytest

from conftest import load_script, script_path

SKILL = "indian-dates-and-fiscal-year"
fy = load_script(SKILL, "fiscal_year")


@pytest.mark.parametrize("d,label,q,month", [
    (dt.date(2026, 3, 31), "2025-26", "Q4", 12), (dt.date(2026, 4, 1), "2026-27", "Q1", 1),
    (dt.date(2026, 6, 30), "2026-27", "Q1", 3), (dt.date(2026, 7, 1), "2026-27", "Q2", 4),
    (dt.date(2026, 12, 31), "2026-27", "Q3", 9), (dt.date(2027, 1, 1), "2026-27", "Q4", 10),
    (dt.date(2000, 1, 15), "1999-00", "Q4", 10), (dt.date(2028, 2, 29), "2027-28", "Q4", 11),
])
def test_financial_year(d, label, q, month):
    r = fy.financial_year(d)
    assert (r["label"], r["quarter"], r["month_of_fy"]) == (label, q, month)


def test_assessment_year_vs_tax_year_boundary():
    old = fy.financial_year(dt.date(2026, 3, 31))
    assert old["income_tax_act"] == "Income-tax Act 1961"
    assert old["assessment_year"] == "2026-27" and old["tax_year"] is None
    new = fy.financial_year(dt.date(2026, 4, 1))
    assert new["income_tax_act"] == "Income-tax Act 2025"
    assert new["tax_year"] == "Tax Year 2026-27" and new["assessment_year"] is None
    assert fy.financial_year(dt.date(2024, 5, 1))["assessment_year"] == "2025-26"


def test_fy_bounds():
    r = fy.financial_year("2026-10-18")
    assert (r["start"], r["end"]) == ("2026-04-01", "2027-03-31")


def test_aware_datetime_is_bucketed_in_ist():
    late_utc = dt.datetime(2026, 3, 31, 20, 15, tzinfo=dt.timezone.utc)   # 01:45 IST on 1 Apr
    assert fy.financial_year(late_utc)["label"] == "2026-27"
    early_utc = dt.datetime(2026, 3, 31, 18, 29, tzinfo=dt.timezone.utc)  # 23:59 IST on 31 Mar
    assert fy.financial_year(early_utc)["label"] == "2025-26"


@pytest.mark.parametrize("q,first,last", [(1, "2026-04-01", "2026-06-30"), (2, "2026-07-01", "2026-09-30"),
                                          (3, "2026-10-01", "2026-12-31"), (4, "2027-01-01", "2027-03-31")])
def test_quarter_range(q, first, last):
    a, b = fy.quarter_range(2026, q)
    assert (a.isoformat(), b.isoformat()) == (first, last)


def test_quarter_range_invalid():
    with pytest.raises(ValueError):
        fy.quarter_range(2026, 5)


@pytest.mark.parametrize("text,expected", [("01/04/2026", dt.date(2026, 4, 1)), ("31-03-2026", dt.date(2026, 3, 31)),
                                           ("29.02.2028", dt.date(2028, 2, 29)), (" 15/08/1947 ", dt.date(1947, 8, 15))])
def test_parse_ddmmyyyy(text, expected):
    assert fy.parse_ddmmyyyy(text) == expected


@pytest.mark.parametrize("text", ["1/4/2026", "04/31/2026", "31/04/2026", "29/02/2027", "2026-04-01",
                                  "01/04/26", "01/04-2026", "", "13/13/2026"])
def test_parse_ddmmyyyy_rejects(text):
    with pytest.raises(ValueError):
        fy.parse_ddmmyyyy(text)


def test_format_ddmmyyyy_and_parse_date():
    assert fy.format_ddmmyyyy(dt.date(2026, 4, 1)) == "01/04/2026"
    assert fy.format_ddmmyyyy(dt.date(2026, 4, 1), "-") == "01-04-2026"
    assert fy.parse_date("2026-04-01") == fy.parse_date("01/04/2026")


def test_to_ist_matches_zoneinfo_and_rejects_naive():
    t = dt.datetime(2026, 3, 31, 20, 15, tzinfo=dt.timezone.utc)
    assert fy.to_ist(t).isoformat() == "2026-04-01T01:45:00+05:30"
    assert fy.to_ist(t).utcoffset() == t.astimezone(ZoneInfo("Asia/Kolkata")).utcoffset()
    with pytest.raises(ValueError):
        fy.to_ist(dt.datetime(2026, 1, 1))


def test_kolkata_has_no_dst_in_tzdata():
    offsets = {dt.datetime(2026, m, 15, tzinfo=ZoneInfo("Asia/Kolkata")).utcoffset() for m in range(1, 13)}
    assert offsets == {dt.timedelta(hours=5, minutes=30)}


def test_cli():
    exe = [sys.executable, str(script_path(SKILL, "fiscal_year"))]
    r = subprocess.run(exe + ["fy", "31/03/2026"], capture_output=True, text=True)
    assert json.loads(r.stdout)["assessment_year"] == "2026-27"
    r = subprocess.run(exe + ["ist", "2026-03-31T20:15:00Z"], capture_output=True, text=True)
    assert r.stdout.strip() == "2026-04-01T01:45:00+05:30"
    assert subprocess.run(exe + ["fy", "04/31/2026"], capture_output=True, text=True).returncode == 2
