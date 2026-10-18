"""Tests for skills/upi-payments/scripts/upi_link.py."""

import json
import subprocess
import sys

import pytest

from conftest import load_script, script_path

SKILL = "upi-payments"
upi = load_script(SKILL, "upi_link")


def cli(*a):
    return subprocess.run([sys.executable, str(script_path(SKILL, "upi_link")), *a],
                          capture_output=True, text=True, timeout=30)


def test_build_basic_static():
    assert upi.build_upi_link("shop@okbank", "Asha Stores") == "upi://pay?pa=shop@okbank&pn=Asha%20Stores&cu=INR"


def test_build_dynamic_and_round_trip():
    uri = upi.build_upi_link("merchant@okbank", "Asha & Sons", am="149.50", tr="ORD-1001", tn="Order #1001")
    assert "pn=Asha%20%26%20Sons" in uri and "tn=Order%20%231001" in uri and "+" not in uri
    r = upi.parse_upi_link(uri, dynamic=True)
    assert r["valid"], r
    assert r["params"] == {"pa": "merchant@okbank", "pn": "Asha & Sons", "am": "149.50", "cu": "INR",
                           "tn": "Order #1001", "tr": "ORD-1001"}


def test_dynamic_requires_am_and_tr():
    r = upi.parse_upi_link("upi://pay?pa=m@okbank&pn=M", dynamic=True)
    assert not r["valid"]
    assert any("'am' is mandatory" in e for e in r["errors"])
    assert any("'tr'" in e for e in r["errors"])


@pytest.mark.parametrize("am", ["0", "-1", "1,000", "₹10", "10.999", "abc", "1e3", ""])
def test_bad_amounts(am):
    with pytest.raises(ValueError):
        upi.build_upi_link("m@okbank", "M", am=am)


@pytest.mark.parametrize("am", ["1", "10.5", "149.50", "100000"])
def test_good_amounts(am):
    assert f"am={am}" in upi.build_upi_link("m@okbank", "M", am=am)


def test_mandatory_fields_and_currency():
    with pytest.raises(ValueError, match="'pn' is mandatory"):
        upi.build_upi_link("m@okbank", "")
    with pytest.raises(ValueError, match="only INR"):
        upi.build_upi_link("m@okbank", "M", cu="USD")


def test_mam_cannot_exceed_am():
    with pytest.raises(ValueError, match="mam"):
        upi.build_upi_link("m@okbank", "M", am="100", mam="200")
    assert "mam=50" in upi.build_upi_link("m@okbank", "M", am="100", mam="50")


def test_url_and_mode_rules():
    with pytest.raises(ValueError, match="url"):
        upi.build_upi_link("m@okbank", "M", url="ftp://x")
    with pytest.raises(ValueError, match="mode"):
        upi.build_upi_link("m@okbank", "M", mode="03")
    assert "mode=04" in upi.build_upi_link("m@okbank", "M", mode="04")


def test_unknown_param_rejected():
    with pytest.raises(ValueError, match="unknown"):
        upi.build_upi_link("m@okbank", "M", foo="bar")


@pytest.mark.parametrize("uri,fragment", [
    ("http://pay?pa=m@okbank&pn=M", "upi://pay"),
    ("upi://collect?pa=m@okbank&pn=M", "upi://pay"),
    ("upi://pay?pa=m@okbank&pn=M&pa=evil@okbank", "duplicate"),
    ("upi://pay?pn=M", "'pa' is mandatory"),
])
def test_parse_rejects(uri, fragment):
    r = upi.parse_upi_link(uri)
    assert not r["valid"] and any(fragment in e for e in r["errors"])


@pytest.mark.parametrize("vpa", ["x@ybl", "name.surname@okaxis", "9876543210@ybl", "a_b-c@paytm", "Shop1@okhdfcbank"])
def test_vpa_valid(vpa):
    r = upi.validate_vpa(vpa)
    assert r["valid"], r
    assert r["psp_handle"] == vpa.split("@")[1].lower()


@pytest.mark.parametrize("vpa", ["", "noatsign", "a@@b", "a@b@c", " a@ybl", "a b@ybl", "@ybl", "a@", "a@1bank",
                                 ".a@ybl", "a@y-bl"])
def test_vpa_invalid(vpa):
    assert not upi.validate_vpa(vpa)["valid"]


def test_cli():
    r = cli("build", "--pa", "merchant@okbank", "--pn", "Asha Stores", "--am", "149.50", "--tr", "ORD1001")
    assert r.returncode == 0 and r.stdout.strip().startswith("upi://pay?pa=merchant@okbank&pn=Asha%20Stores")
    r = cli("parse", r.stdout.strip(), "--dynamic")
    assert r.returncode == 0 and json.loads(r.stdout)["valid"]
    assert cli("vpa", "bad").returncode == 1
    assert cli("build", "--pa", "x", "--pn", "A").returncode == 1
