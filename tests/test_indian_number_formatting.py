"""Tests for skills/indian-number-formatting/scripts/{inr_format,amount_in_words}.py."""

import shutil
import subprocess
import sys
from decimal import Decimal

import pytest

from conftest import load_script, script_path

SKILL = "indian-number-formatting"
fmt = load_script(SKILL, "inr_format")
words = load_script(SKILL, "amount_in_words")


@pytest.mark.parametrize("n,expected", [(0, "0"), (7, "7"), (999, "999"), (1000, "1,000"), (99999, "99,999"),
                                        (100000, "1,00,000"), (1234567, "12,34,567"), (10000000, "1,00,00,000"),
                                        (123456789, "12,34,56,789"), (1000000000000, "10,00,00,00,00,000"),
                                        ("0001000", "1,000")])
def test_group_indian(n, expected):
    assert fmt.group_indian(n) == expected


def test_group_indian_rejects_non_digits():
    with pytest.raises(ValueError):
        fmt.group_indian("-5")


@pytest.mark.parametrize("value,kw,expected", [
    ("1234567.5", {}, "₹12,34,567.50"),
    (120000, {"decimals": 0}, "₹1,20,000"),
    (-1500, {}, "-₹1,500.00"),
    ("0.005", {}, "₹0.01"),
    ("-0.001", {}, "₹0.00"),
    ("999.999", {}, "₹1,000.00"),
    (100, {"symbol": False}, "100.00"),
    (100, {"space": True}, "₹ 100.00"),
])
def test_format_inr(value, kw, expected):
    assert fmt.format_inr(value, **kw) == expected


def test_format_indian_keeps_decimals():
    assert fmt.format_indian("1234567.891") == "12,34,567.891"
    assert fmt.format_indian(0.1 + 0.2, decimals=2) == "0.30"


@pytest.mark.parametrize("text,expected", [("₹12,34,567.50", "1234567.50"), ("Rs. 1,20,000/-", "120000"),
                                           ("INR 500", "500"), ("1,234,567", "1234567"), ("-₹500", "-500"),
                                           ("₹ -500", "-500"), ("120000", "120000")])
def test_parse_indian(text, expected):
    assert fmt.parse_indian(text) == Decimal(expected)


@pytest.mark.parametrize("bad", ["", "abc", "1.2 lakh", "1..2", "₹", "12a"])
def test_parse_indian_rejects(bad):
    with pytest.raises(ValueError):
        fmt.parse_indian(bad)


@pytest.mark.parametrize("value,expected", [(1250000, "12.5 lakh"), (100000, "1 lakh"), (25000000, "2.5 crore"),
                                            (12345678901, "1,234.57 crore"), (99999, "99,999"), (-150000, "-1.5 lakh"),
                                            (9999999, "1 crore"), (9994999, "99.95 lakh")])
def test_short_lakh_crore(value, expected):
    assert fmt.short_lakh_crore(value) == expected


def test_short_lakh_crore_abbrev():
    assert fmt.short_lakh_crore(1250000, long_words=False) == "12.5L"


@pytest.mark.parametrize("amount,expected", [
    (0, "Zero Rupees Only"), (1, "One Rupee Only"), ("0.01", "One Paisa Only"), ("0.5", "Fifty Paise Only"),
    (21, "Twenty One Rupees Only"), (105, "One Hundred Five Rupees Only"),
    (1000, "One Thousand Rupees Only"), (100000, "One Lakh Rupees Only"),
    (120000, "One Lakh Twenty Thousand Rupees Only"), (118000, "One Lakh Eighteen Thousand Rupees Only"),
    ("1050.50", "One Thousand Fifty Rupees and Fifty Paise Only"),
    (1234567, "Twelve Lakh Thirty Four Thousand Five Hundred Sixty Seven Rupees Only"),
    (10000000, "One Crore Rupees Only"),
    (123456789, "Twelve Crore Thirty Four Lakh Fifty Six Thousand Seven Hundred Eighty Nine Rupees Only"),
    (1000000000, "One Hundred Crore Rupees Only"), (10**12, "One Lakh Crore Rupees Only"),
    ("₹1,20,000", "One Lakh Twenty Thousand Rupees Only"), ("-500", "Minus Five Hundred Rupees Only"),
    ("10.005", "Ten Rupees and One Paisa Only"),
])
def test_amount_in_words(amount, expected):
    assert words.amount_in_words(amount) == expected


def test_prefix_style_and_options():
    assert words.amount_in_words(120000, style="prefix") == "Rupees One Lakh Twenty Thousand Only"
    assert words.amount_in_words("0.50", style="prefix") == "Paise Fifty Only"
    assert words.amount_in_words(105, use_and=True) == "One Hundred and Five Rupees Only"
    assert words.amount_in_words(100005, use_and=True) == "One Lakh and Five Rupees Only"
    assert words.amount_in_words(100, only=False) == "One Hundred Rupees"


def test_words_reject_bad_input():
    for bad in ("abc", "NaN"):
        with pytest.raises(ValueError):
            words.amount_in_words(bad)
    with pytest.raises(ValueError):
        words.amount_in_words(1, style="other")
    with pytest.raises(ValueError):
        words.number_to_words(-1)


def test_every_number_up_to_100000_has_words_without_double_spaces():
    for n in range(0, 100001, 7):
        w = words.number_to_words(n)
        assert "  " not in w and w == w.strip()


def test_cli():
    r = subprocess.run([sys.executable, str(script_path(SKILL, "inr_format")), "1250000", "--short"],
                       capture_output=True, text=True)
    assert r.stdout.strip() == "12.5 lakh"
    r = subprocess.run([sys.executable, str(script_path(SKILL, "amount_in_words")), "120000"],
                       capture_output=True, text=True)
    assert r.stdout.strip() == "One Lakh Twenty Thousand Rupees Only"


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize("n", ["0", "999", "1000", "100000", "1234567.5", "123456789.25", "1000000000000"])
def test_matches_intl_numberformat_en_in(n):
    js = (f'console.log(new Intl.NumberFormat("en-IN",{{style:"currency",currency:"INR"}}).format("{n}"))')
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True).stdout.strip()
    assert out == fmt.format_inr(n)
