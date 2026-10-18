"""Tests for skills/indian-addresses/scripts/india_regions.py."""

import json
import subprocess
import sys

import pytest

from conftest import load_script, script_path

SKILL = "indian-addresses"
reg = load_script(SKILL, "india_regions")
gstin = load_script("indian-id-validation", "gstin_validate")


def test_counts_28_states_8_uts():
    assert sum(s["type"] == "state" for s in reg.STATES_AND_UTS) == 28
    assert sum(s["type"] == "ut" for s in reg.STATES_AND_UTS) == 8
    names = [s["name"] for s in reg.STATES_AND_UTS]
    assert len(set(names)) == 36


def test_gst_codes_and_names_match_gstin_table():
    for s in reg.STATES_AND_UTS:
        assert gstin.STATE_CODES[s["gst_code"]] == s["name"], s


def test_uts_with_legislature():
    leg = {s["name"] for s in reg.STATES_AND_UTS if s.get("legislature")}
    assert leg == {"Delhi", "Jammu and Kashmir", "Puducherry"}


@pytest.mark.parametrize("text,expected", [
    ("Odisha", "Odisha"), ("orissa", "Odisha"), ("Pondicherry", "Puducherry"), ("Uttaranchal", "Uttarakhand"),
    ("NCT of Delhi", "Delhi"), ("new delhi", "Delhi"), ("J&K", "Jammu and Kashmir"),
    ("jammu & kashmir", "Jammu and Kashmir"), ("daman and diu", "Dadra and Nagar Haveli and Daman and Diu"),
    ("Andaman & Nicobar Islands", "Andaman and Nicobar Islands"), ("  tamil   nadu ", "Tamil Nadu"),
    ("TELANGANA", "Telangana"), ("27", "Maharashtra"), ("7", "Delhi"), ("38", "Ladakh"),
])
def test_find_state(text, expected):
    assert reg.find_state(text)["name"] == expected


@pytest.mark.parametrize("text", ["", "Atlantis", "uk", "99", "25", None])
def test_find_state_unknown_or_ambiguous(text):
    assert reg.find_state(text) is None


@pytest.mark.parametrize("pin,region,circle", [
    ("110001", "Northern", "Delhi"), ("160017", "Northern", "Punjab"), ("400001", "Western", "Maharashtra"),
    ("500001", "Southern", "Andhra Pradesh"), ("560001", "Southern", "Karnataka"), ("600001", "Southern", "Tamil Nadu"),
    ("781001", "Eastern", "Assam"), ("800001", "Eastern", "Bihar"), ("900001", "Army Postal Service", "Army Postal Service"),
    ("560 001", "Southern", "Karnataka"),
])
def test_pin_info(pin, region, circle):
    r = reg.pin_info(pin)
    assert r["valid_format"] and r["region"] == region and r["circle"] == circle


def test_pin_info_unlisted_prefix_and_invalid():
    r = reg.pin_info("290001")
    assert r["valid_format"] and r["circle"] is None and "directory" in r["note"]
    assert not reg.pin_info("012345")["valid_format"]
    assert not reg.pin_info("12345")["valid_format"]


def test_cli():
    exe = [sys.executable, str(script_path(SKILL, "india_regions"))]
    r = subprocess.run(exe + ["list"], capture_output=True, text=True)
    assert r.returncode == 0 and len(r.stdout.strip().splitlines()) == 36
    r = subprocess.run(exe + ["state", "Orissa"], capture_output=True, text=True)
    assert json.loads(r.stdout)["gst_code"] == "21"
    assert subprocess.run(exe + ["pin", "000000"], capture_output=True, text=True).returncode == 1
