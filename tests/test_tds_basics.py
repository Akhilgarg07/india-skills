"""Tests for skills/tds-basics/scripts/tds_calc.py."""

import json
import subprocess
import sys
from decimal import Decimal as D

import pytest

from conftest import load_script, script_path

SKILL = "tds-basics"
tds = load_script(SKILL, "tds_calc")


def cli(*a):
    return subprocess.run([sys.executable, str(script_path(SKILL, "tds_calc")), *a],
                          capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize("date,act", [("2026-03-31", "Income-tax Act 1961"), ("2026-04-01", "Income-tax Act 2025"),
                                      ("2025-12-01", "Income-tax Act 1961"), ("2027-01-15", "Income-tax Act 2025")])
def test_governing_act_boundary(date, act):
    assert tds.governing_act(date) == act


def test_section_codes_old_and_new():
    assert tds.section_for("contractor", "2026-03-31") == "Income-tax Act 1961, s.194C"
    assert tds.section_for("contractor", "2026-04-30") == "Income-tax Act 2025, s.393(1) [Table: Sl. No. 6(i)]"
    assert tds.section_for("professional", "2026-05-01").endswith("6(iii)]")
    assert tds.section_for("professional", "2025-05-01", pan=False) == "Income-tax Act 1961, s.194J read with s.206AA"
    assert tds.section_for("technical", "2026-05-01", pan=False).endswith("read with s.397(2)")


@pytest.mark.parametrize("payee,rate", [("individual", "1"), ("huf", "1"), ("company", "2"), ("firm", "2"), ("llp", "2")])
def test_contractor_rates(payee, rate):
    r = tds.compute("contractor", "40000", payee_type=payee, event_date="2026-06-01")
    assert r["rate"] == D(rate)
    assert r["tds"] == D("40000") * D(rate) / 100


def test_contractor_thresholds():
    assert tds.compute("contractor", "30000", event_date="2026-06-01")["tds"] == 0          # not > 30,000
    assert tds.compute("contractor", "30001", event_date="2026-06-01")["tds"] == D("600.02")
    # aggregate exactly 1,00,000 -> no TDS; crossing it -> catch-up on earlier untaxed sums
    assert tds.compute("contractor", "20000", paid_earlier_in_year="80000", event_date="2026-06-01")["tds"] == 0
    r = tds.compute("contractor", "20000", paid_earlier_in_year="90000", event_date="2026-06-01")
    assert r["tds_base"] == D("110000") and r["tds"] == D("2200.00")
    # earlier payments already taxed are not taxed again
    r = tds.compute("contractor", "20000", paid_earlier_in_year="90000", tds_base_earlier_in_year="40000",
                    event_date="2026-06-01")
    assert r["tds_base"] == D("70000")


@pytest.mark.parametrize("kind,rate", [("professional", "10"), ("technical", "2"), ("call_centre", "2"), ("film_royalty", "2")])
def test_194j_rates(kind, rate):
    r = tds.compute(kind, "100000", event_date="2026-06-01")
    assert r["rate"] == D(rate) and r["tds"] == D("100000") * D(rate) / 100


def test_194j_threshold_changed_on_1_april_2025():
    assert tds.compute("professional", "40000", event_date="2025-03-31")["tds"] == D("4000.00")  # > 30,000
    assert tds.compute("professional", "40000", event_date="2025-04-01")["tds"] == 0             # <= 50,000
    assert tds.compute("professional", "50000", event_date="2026-04-01")["tds"] == 0
    r = tds.compute("professional", "20000", paid_earlier_in_year="40000", event_date="2026-04-01")
    assert r["tds_base"] == D("60000") and r["tds"] == D("6000.00")


def test_no_pan_twenty_percent():
    r = tds.compute("contractor", "50000", payee_type="individual", pan=False, event_date="2026-06-01")
    assert r["rate"] == D("20") and r["tds"] == D("10000.00")
    r = tds.compute("professional", "60000", pan=False, event_date="2026-06-01")
    assert r["rate"] == D("20")


def test_gst_excluded_from_base():
    r = tds.compute("technical", "118000", gst="18000", event_date="2026-06-01")
    assert r["tds_base"] == D("100000") and r["tds"] == D("2000.00")
    assert r["net_payable"] == D("116000.00")


@pytest.mark.parametrize("kwargs", [
    {"payment_type": "rent", "amount": "1"},
    {"payment_type": "contractor", "amount": "-5"},
    {"payment_type": "contractor", "amount": "100", "gst": "200"},
    {"payment_type": "contractor", "amount": "100", "paid_earlier_in_year": "10", "tds_base_earlier_in_year": "20"},
    {"payment_type": "contractor", "amount": "abc"},
])
def test_invalid(kwargs):
    with pytest.raises(ValueError):
        tds.compute(kwargs.pop("payment_type"), kwargs.pop("amount"), **kwargs)


def test_cli():
    r = cli("contractor", "45000", "--payee", "individual", "--date", "2026-07-01")
    assert r.returncode == 0 and "450.00" in r.stdout and "6(i)" in r.stdout
    r = cli("professional", "60000", "--no-pan", "--date", "2026-05-10", "--json")
    data = json.loads(r.stdout)
    assert data["tds"] == "12000.00" and data["rate"] == "20"
    assert cli("salary", "1").returncode == 2
