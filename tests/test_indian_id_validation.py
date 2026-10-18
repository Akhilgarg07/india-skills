"""Tests for skills/indian-id-validation/scripts/*.

Valid GSTINs below are real registrations published by the businesses themselves or
shown on public GSTIN lookups (see the skill's references/sources.md). Aadhaar values
are synthetic: generated with a Verhoeff check digit, never real numbers.
"""

import subprocess
import sys

import pytest

from conftest import load_script, script_path

SKILL = "indian-id-validation"
verhoeff = load_script(SKILL, "verhoeff")
aadhaar = load_script(SKILL, "aadhaar_validate")
gstin = load_script(SKILL, "gstin_validate")
pan = load_script(SKILL, "pan_validate")
ifsc = load_script(SKILL, "ifsc_validate")
mobile = load_script(SKILL, "mobile_validate")
pincode = load_script(SKILL, "pincode_validate")


def run_cli(script, *args, stdin=None):
    return subprocess.run(
        [sys.executable, str(script_path(SKILL, script)), *args],
        input=stdin, capture_output=True, text=True, timeout=30,
    )


# ---------------------------------------------------------------- Verhoeff

@pytest.mark.parametrize("payload,digit", [("236", "3"), ("12345", "1"), ("0", "4")])
def test_verhoeff_known_vectors(payload, digit):
    assert verhoeff.check_digit(payload) == digit
    assert verhoeff.is_valid(payload + digit)


@pytest.mark.parametrize("number", ["2364", "123450", "", "12a4", "١٢٣"])
def test_verhoeff_rejects(number):
    assert not verhoeff.is_valid(number)


def test_verhoeff_catches_every_single_digit_error_and_adjacent_swap():
    base = "23412341234"
    good = base + verhoeff.check_digit(base)
    for i in range(len(good)):
        for d in "0123456789":
            if d != good[i]:
                assert not verhoeff.is_valid(good[:i] + d + good[i + 1:])
    for i in range(len(good) - 1):
        if good[i] != good[i + 1]:
            swapped = good[:i] + good[i + 1] + good[i] + good[i + 2:]
            assert not verhoeff.is_valid(swapped)


def test_verhoeff_check_digit_rejects_non_digits():
    with pytest.raises(ValueError):
        verhoeff.check_digit("12x")


def test_verhoeff_cli():
    assert run_cli("verhoeff", "check", "2363").returncode == 0
    assert run_cli("verhoeff", "check", "2364").returncode == 1
    r = run_cli("verhoeff", "digit", "236")
    assert r.returncode == 0 and r.stdout.strip() == "3"


# ---------------------------------------------------------------- Aadhaar

SYNTHETIC_BASE = "23412341234"
SYNTHETIC = SYNTHETIC_BASE + verhoeff.check_digit(SYNTHETIC_BASE)


@pytest.mark.parametrize("value", [SYNTHETIC, f"{SYNTHETIC[:4]} {SYNTHETIC[4:8]} {SYNTHETIC[8:]}",
                                   f"{SYNTHETIC[:4]}-{SYNTHETIC[4:8]}-{SYNTHETIC[8:]}"])
def test_aadhaar_valid_formats(value):
    r = aadhaar.validate(value)
    assert r["valid"], r
    assert r["masked"] == f"XXXX XXXX {SYNTHETIC[-4:]}"


@pytest.mark.parametrize("value,reason", [
    (SYNTHETIC[:-1] + str((int(SYNTHETIC[-1]) + 1) % 10), "checksum"),
    (SYNTHETIC[:-1], "12 digits"),
    (SYNTHETIC + "0", "12 digits"),
    ("2341A2341234", "only digits"),
    ("", "12 digits"),
])
def test_aadhaar_invalid(value, reason):
    r = aadhaar.validate(value)
    assert not r["valid"]
    assert any(reason in e for e in r["errors"])


def test_uidai_sandbox_test_uid_fails_verhoeff():
    # Documented in SKILL.md: test modes need a checksum bypass.
    assert not aadhaar.is_valid("999999990019")


def test_aadhaar_result_never_contains_full_number():
    bad = SYNTHETIC[:-1] + str((int(SYNTHETIC[-1]) + 1) % 10)
    for value in (SYNTHETIC, bad):
        r = aadhaar.validate(value)
        assert value not in repr(r)
        assert value[:8] not in repr(r)


def test_aadhaar_mask_never_leaks_partial_input():
    assert aadhaar.mask("12345") == "XXXX XXXX XXXX"
    assert aadhaar.mask(SYNTHETIC, mask_char="*") == f"**** **** {SYNTHETIC[-4:]}"


def test_aadhaar_cli_reads_stdin_and_prints_masked_only():
    r = run_cli("aadhaar_validate", stdin=SYNTHETIC + "\n")
    assert r.returncode == 0
    assert SYNTHETIC not in r.stdout and SYNTHETIC[-4:] in r.stdout


def test_aadhaar_cli_refuses_argv():
    r = run_cli("aadhaar_validate", SYNTHETIC)
    assert r.returncode == 2
    assert SYNTHETIC not in r.stdout + r.stderr


# ---------------------------------------------------------------- GSTIN

REAL_GSTINS = [
    "27AABCE6624L1ZG", "07AABCE6624L1ZI", "29AABCE6624L1ZC", "33AABCE6624L1ZN",
    "29AACCN6194P2ZK", "07AACCN6194P2ZQ", "27AACCN6194P1ZP", "29AABCA0522B1ZG",
    "33AABCA0522B1ZR", "07AABCA0522B1ZM", "07AABCI2726B1Z4", "27AABCI2726B1Z2",
    "29AABCI2726B1ZY", "33AABCI2726B1Z9", "07AABCI2726B2Z3", "29AABCA0522B1DP",
    "27AABCA0522B1DT", "27AABCI2726B1CD",
]


@pytest.mark.parametrize("value", REAL_GSTINS)
def test_gstin_real_values_pass(value):
    r = gstin.validate(value)
    assert r["valid"], r
    assert r["registration_kind"] == "pan-based"
    assert r["pan"] == value[2:12]


def test_gstin_check_char_and_parse():
    assert gstin.check_char("27AABCE6624L1Z") == "G"
    r = gstin.validate("  27aabce6624l1zg ")
    assert r["valid"] and r["normalized"] == "27AABCE6624L1ZG"
    assert r["state_name"] == "Maharashtra" and r["state_code"] == "27"


def test_gstin_14th_char_need_not_be_z():
    assert gstin.is_valid("27AABCI2726B1CD")
    assert gstin.is_valid("29AABCA0522B1DP")


@pytest.mark.parametrize("value,fragment", [
    ("27AABCE6624L1ZH", "check character should be 'G'"),
    ("40AABCE6624L1ZG", "not a GST state code"),
    ("27AABCE6624L1Z", "15 characters"),
    ("27AABCE6624L1Z-", "only digits"),
    ("27AABCE 6624L1ZG", "15 characters"),
])
def test_gstin_invalid(value, fragment):
    r = gstin.validate(value)
    assert not r["valid"]
    assert any(fragment in e for e in r["errors"]), r["errors"]


def test_every_single_char_substitution_is_caught():
    good = "27AABCE6624L1ZG"
    for i in range(14):
        for c in gstin.ALPHABET:
            if c != good[i]:
                mutated = good[:i] + c + good[i + 1:]
                assert gstin.check_char(mutated[:14]) != "G", mutated


def test_gstin_tan_based_registration():
    first14 = "07DELM12345L1D"  # synthetic tax-deductor style body (TAN in 3-12)
    r = gstin.validate(first14 + gstin.check_char(first14))
    assert r["valid"] and r["registration_kind"].startswith("tan-based")
    assert r["tan"] == "DELM12345L"


def test_gstin_other_body_is_warning_not_error():
    first14 = "9917USA29002OS"  # neither PAN nor TAN shaped
    r = gstin.validate(first14 + gstin.check_char(first14))
    assert r["valid"] and r["registration_kind"] == "other" and r["warnings"]


def test_gstin_historical_code_warns():
    first14 = "28AABCE6624L1Z"
    r = gstin.validate(first14 + gstin.check_char(first14))
    assert r["valid"] and r["warnings"]


def test_state_codes_complete():
    expected = {f"{n:02d}" for n in range(1, 39)} | {"97", "99"}
    assert set(gstin.STATE_CODES) == expected


def test_gstin_cli():
    assert run_cli("gstin_validate", "27AABCE6624L1ZG").returncode == 0
    r = run_cli("gstin_validate", "--json", "27AABCE6624L1ZH")
    assert r.returncode == 1 and '"valid": false' in r.stdout


# ---------------------------------------------------------------- PAN / TAN

@pytest.mark.parametrize("value,holder", [
    ("ALWPG5809L", "Individual"), ("AAACI1234F", "Company"), ("AABCE6624L", "Company"),
    ("AAAHA1234B", "Hindu Undivided Family (HUF)"), ("AAAFB1234C", "Firm / Limited Liability Partnership"),
    ("AAATC1234D", "Trust"), ("AAAGG0001E", "Government Agency"), (" alwpg5809l ", "Individual"),
])
def test_pan_valid(value, holder):
    r = pan.validate_pan(value)
    assert r["valid"], r
    assert r["holder_type"] == holder


@pytest.mark.parametrize("value", ["ALWXG5809L", "ALWPG58091", "ALWPG5809", "ALWPG5809LL",
                                   "1LWPG5809L", "ALWPG0000L", "ALW PG5809L", ""])
def test_pan_invalid(value):
    assert not pan.is_valid_pan(value)


def test_tan():
    assert pan.is_valid_tan("DELM12345L")
    for bad in ("DEL123456L", "DELM1234L", "DELM00000L", "DELM12345"):
        assert not pan.is_valid_tan(bad)


def test_pan_cli():
    assert run_cli("pan_validate", "ALWPG5809L").returncode == 0
    assert run_cli("pan_validate", "--tan", "DELM12345L").returncode == 0
    assert run_cli("pan_validate", "ALWXG5809L").returncode == 1
    assert run_cli("pan_validate").returncode == 2


# ---------------------------------------------------------------- IFSC

@pytest.mark.parametrize("value", ["RBIS0NDPA01", "RBIS0GWPA01", "RBIS0AZPA01", " rbis0ndpa01 "])
def test_ifsc_valid(value):
    r = ifsc.validate(value)
    assert r["valid"], r
    assert r["bank_code"] == "RBIS"


def test_ifsc_letter_o_gets_hint_not_autocorrect():
    r = ifsc.validate("RBISONDPA01")
    assert not r["valid"] and r["hints"]
    assert r["normalized"] == "RBISONDPA01"


@pytest.mark.parametrize("value", ["RBIS1NDPA01", "RB1S0NDPA01", "RBIS0NDPA0", "RBIS0NDPA011", "RBIS0NDPA-1"])
def test_ifsc_invalid(value):
    assert not ifsc.is_valid(value)


def test_ifsc_cli():
    assert run_cli("ifsc_validate", "RBIS0NDPA01").returncode == 0
    assert run_cli("ifsc_validate", "RBISONDPA01").returncode == 1


# ---------------------------------------------------------------- Mobile

@pytest.mark.parametrize("value", ["9876543210", "+91 98765 43210", "+91-98765-43210", "919876543210",
                                   "09876543210", "00919876543210", "(+91) 98765 43210"])
def test_mobile_valid_forms(value):
    r = mobile.validate(value)
    assert r["valid"], r
    assert r["e164"] == "+919876543210"


@pytest.mark.parametrize("value", ["6000000000", "7012345678", "8123456789"])
def test_mobile_6_7_8_series(value):
    assert mobile.is_valid(value)


@pytest.mark.parametrize("value", ["5876543210", "1123456789", "987654321", "98765432101",
                                   "+1 9876543210", "+9198765432", "98765abcde", "", "+91 0987654321"])
def test_mobile_invalid(value):
    assert not mobile.is_valid(value)


def test_mobile_cli():
    assert run_cli("mobile_validate", "+919876543210").returncode == 0
    assert run_cli("mobile_validate", "5876543210").returncode == 1


# ---------------------------------------------------------------- PIN code

@pytest.mark.parametrize("value,region", [("110001", "1"), ("560 001", "5"), ("380020", "3"), ("999999", "9")])
def test_pincode_valid(value, region):
    r = pincode.validate(value)
    assert r["valid"] and r["region_digit"] == region


def test_pincode_army_postal_service():
    assert pincode.validate("900001")["is_army_postal_service"] is True
    assert pincode.validate("110001")["is_army_postal_service"] is False


@pytest.mark.parametrize("value", ["011000", "11000", "1100011", "11000a", "", "56 0001", "110 00 1"])
def test_pincode_invalid(value):
    assert not pincode.is_valid(value)


def test_pincode_cli():
    assert run_cli("pincode_validate", "110001").returncode == 0
    assert run_cli("pincode_validate", "011000").returncode == 1
