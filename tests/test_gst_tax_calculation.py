"""Tests for skills/gst-tax-calculation/scripts/gst_calc.py."""

import json
import subprocess
import sys
from decimal import Decimal as D

import pytest

from conftest import load_script, script_path

SKILL = "gst-tax-calculation"
gst = load_script(SKILL, "gst_calc")


def cli(*args):
    return subprocess.run([sys.executable, str(script_path(SKILL, "gst_calc")), *args],
                          capture_output=True, text=True, timeout=30)


def test_exclusive_intra_state_18():
    r = gst.calculate("100000", 18)
    assert (r["taxable_value"], r["cgst"], r["sgst"], r["igst"]) == (D("100000.00"), D("9000.00"), D("9000.00"), D("0.00"))
    assert r["total"] == D("118000.00") and r["cgst_rate"] == D(9)


def test_exclusive_inter_state_18():
    r = gst.calculate("100000", 18, inter_state=True)
    assert r["igst"] == D("18000.00") and r["cgst"] == r["sgst"] == D("0.00")
    assert r["total"] == D("118000.00")


@pytest.mark.parametrize("inter", [False, True])
def test_inclusive_back_calculation(inter):
    r = gst.calculate("118000", 18, inclusive=True, inter_state=inter)
    assert r["taxable_value"] == D("100000.00")
    assert r["total_tax"] == D("18000.00")
    assert r["total"] == D("118000.00")


@pytest.mark.parametrize("price,rate", [("101", 18), ("99.99", 5), ("1", 18), ("1234.56", 40), ("0.01", 18), ("333", 3)])
def test_inclusive_always_sums_to_price_and_halves_equal(price, rate):
    r = gst.calculate(price, rate, inclusive=True)
    assert r["taxable_value"] + r["cgst"] + r["sgst"] == D(price).quantize(D("0.01"))
    assert r["cgst"] == r["sgst"]


def test_inclusive_never_applies_rate_to_gross():
    r = gst.calculate("118", 18, inclusive=True)
    assert r["total_tax"] == D("18.00")  # not 21.24


@pytest.mark.parametrize("rate,half", [(5, "2.5"), (18, "9"), (40, "20"), (3, "1.5"), ("0.25", "0.125"), ("1.5", "0.75")])
def test_current_rates_split(rate, half):
    r = gst.calculate("1000", rate)
    assert r["cgst_rate"] == D(half) and not r["warnings"]


def test_paise_rounding_half_up():
    # 999.99 * 2.5% = 24.99975 -> 25.00
    r = gst.calculate("999.99", 5)
    assert r["cgst"] == D("25.00")
    # 10.10 * 9% = 0.909 -> 0.91
    assert gst.calculate("10.10", 18)["cgst"] == D("0.91")
    # 0.05 * 9% = 0.0045 -> 0.00
    assert gst.calculate("0.05", 18)["cgst"] == D("0.00")


def test_float_input_does_not_leak_binary_error():
    assert gst.calculate(0.1, 18)["total"] == D("0.12")
    assert gst.calculate(0.1 + 0.2, 18)["taxable_value"] == D("0.30")


@pytest.mark.parametrize("amount,expected", [("10.49", "10"), ("10.50", "11"), ("10.51", "11"), ("0.49", "0"), ("-10.50", "-11")])
def test_round_rupee_section_170(amount, expected):
    assert gst.round_rupee(amount) == D(expected)


def test_round_total_adds_round_off_line_not_tax_change():
    r = gst.calculate("999.99", 5, round_total=True)
    assert r["total"] == D("1050.00") and r["round_off"] == D("0.01")
    assert r["cgst"] == D("25.00")


def test_reverse_charge_supplier_does_not_collect_tax():
    r = gst.calculate("5000", 18, reverse_charge=True)
    assert r["total_tax"] == D("900.00")
    assert r["total"] == D("5000.00") and r["tax_paid_by"] == "recipient"


def test_legacy_rate_warns_or_rejects():
    r = gst.calculate("100", 12)
    assert r["warnings"] and r["cgst"] == D("6.00")
    with pytest.raises(ValueError):
        gst.calculate("100", 28, strict=True)


@pytest.mark.parametrize("bad", [("-1", 18), ("abc", 18), ("100", 41), ("100", -5), ("NaN", 18), ("100", "x")])
def test_invalid_inputs(bad):
    with pytest.raises(ValueError):
        gst.calculate(*bad)


def test_amount_with_rupee_symbol_and_indian_commas():
    assert gst.calculate("₹1,18,000", 18, inclusive=True)["taxable_value"] == D("100000.00")


def test_invoice_sums_per_line():
    # 0.05 at 18%: each line's CGST rounds to 0.00, so 3 lines total 0.00, whereas
    # recomputing on the 0.15 total would give 0.01. Totals must equal the sum of lines.
    inv = gst.calculate_invoice([{"amount": "0.05", "rate": 18}] * 3)
    assert inv["cgst"] == sum(l["cgst"] for l in inv["lines"]) == D("0.00")
    assert inv["total"] == inv["taxable_value"] + inv["total_tax"]


def test_invoice_mixed_rates_and_round_off():
    inv = gst.calculate_invoice([{"amount": "100", "rate": 5}, {"amount": "59", "rate": 18, "inclusive": True}],
                                round_total=True)
    assert inv["lines"][1]["taxable_value"] == D("50.00") and inv["lines"][1]["cgst"] == D("4.50")
    assert inv["total"] == D("164.00") and inv["round_off"] == D("0.00")


def test_cli_text_and_json():
    r = cli("118000", "--rate", "18", "--inclusive", "--inter-state")
    assert r.returncode == 0 and "100000.00" in r.stdout and "IGST" in r.stdout
    r = cli("100", "--rate", "18", "--json")
    data = json.loads(r.stdout)
    assert data["cgst"] == "9.00" and data["total"] == "118.00"
    assert cli("100", "--rate", "12", "--strict").returncode == 2
