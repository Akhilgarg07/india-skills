"""Tests for skills/gst-invoicing/scripts/invoice_check.py (GSTINs here are synthetic)."""

import copy
import json
import subprocess
import sys

import pytest

from conftest import SKILLS_DIR, load_script, script_path

SKILL = "gst-invoicing"
inv = load_script(SKILL, "invoice_check")

SUP_KA = "29AAACE1234F1Z2"   # synthetic, Karnataka
REC_MH = "27AAACB5678K1ZA"   # synthetic, Maharashtra


def base():
    return copy.deepcopy(inv.EXAMPLE)


def errors_of(invoice):
    return inv.check_invoice(invoice)["errors"]


def test_vendored_gstin_validator_is_identical_copy():
    a = (SKILLS_DIR / "indian-id-validation" / "scripts" / "gstin_validate.py").read_bytes()
    b = (SKILLS_DIR / "gst-invoicing" / "scripts" / "gstin_validate.py").read_bytes()
    assert a == b, "re-copy indian-id-validation/scripts/gstin_validate.py into gst-invoicing"


def test_example_is_valid_inter_state():
    r = inv.check_invoice(base())
    assert r["ok"], r
    assert r["supply_type"] == "inter-state"


@pytest.mark.parametrize("sup,pos,kw,expected", [
    ("29", "27", {}, "inter-state"), ("29", "29", {}, "intra-state"),
    ("29", "29", {"sez": True}, "inter-state"), ("07", "96", {"export": True}, "inter-state"),
])
def test_supply_type(sup, pos, kw, expected):
    assert inv.supply_type(sup, pos, **kw) == expected


def test_state_tax_name_utgst():
    assert inv.state_tax_name("04") == "UTGST"   # Chandigarh
    assert inv.state_tax_name("07") == "SGST"    # Delhi has a legislature
    assert inv.state_tax_name("34") == "SGST"    # Puducherry


def test_general_place_of_supply():
    pos = inv.general_place_of_supply
    assert pos("services", recipient_registered=True, recipient_state="27", supplier_state="29") == "27"
    assert pos("services", recipient_registered=False, supplier_state="29") == "29"
    assert pos("goods", recipient_registered=True, recipient_state="27", delivery_state="24") == "24"
    assert pos("goods", recipient_registered=False, recipient_state="33", supplier_state="29") == "33"
    with pytest.raises(ValueError):
        pos("other", recipient_registered=True)


def test_igst_on_intra_state_is_error():
    i = base()
    i["place_of_supply"] = "29"
    i["supply_type"] = "intra-state"
    i["recipient"]["gstin"] = SUP_KA
    errs = errors_of(i)
    assert any("must charge CGST + SGST" in e for e in errs)


def test_intra_state_correct_split_passes():
    i = base()
    i["place_of_supply"] = "29"
    i["supply_type"] = "intra-state"
    i["lines"][0].pop("igst")
    i["lines"][0].update({"cgst": "9000.00", "sgst": "9000.00"})
    assert inv.check_invoice(i)["ok"]


def test_cgst_sgst_on_inter_state_is_error():
    i = base()
    i["lines"][0].update({"cgst": "9000.00", "sgst": "9000.00"})
    i["lines"][0].pop("igst")
    assert any("IGST only" in e for e in errors_of(i))


def test_wrong_tax_amount():
    i = base()
    i["lines"][0]["igst"] = "21240.00"
    assert any("IGST should be 18000.00" in e for e in errors_of(i))


def test_declared_supply_type_mismatch():
    i = base()
    i["supply_type"] = "intra-state"
    assert any("make it 'inter-state'" in e for e in errors_of(i))


@pytest.mark.parametrize("number,ok", [("INV/2026-27/0042", True), ("A1", True),
                                       ("INV/2026-27/00042", False), ("INV 001", False),
                                       ("INV#001", False), ("", False)])
def test_invoice_number_rules(number, ok):
    i = base()
    i["invoice_number"] = number
    has_err = any("invoice_number" in e for e in errors_of(i))
    assert has_err is (not ok)


def test_hsn_digits_by_turnover():
    i = base()
    i["lines"][0]["hsn"] = "9983"
    assert inv.check_invoice(i)["ok"]          # AATO 3 crore, 4 digits OK
    i["supplier_aato"] = "60000000"            # 6 crore
    i["irn"], i["qr_code"] = "x" * 64, "qr"
    assert any("at least 6 digits" in e for e in errors_of(i))
    i["lines"][0]["hsn"] = "99831"
    assert any("4, 6 or 8 digits" in e for e in errors_of(i))


def test_goods_need_quantity_and_unit():
    i = base()
    i["lines"][0].update({"hsn": "8471", "description": "Laptop"})
    assert any("quantity and unit" in e for e in errors_of(i))
    i["lines"][0].update({"quantity": 2, "unit": "NOS"})
    assert inv.check_invoice(i)["ok"]


def test_reverse_charge_flag_required():
    i = base()
    del i["reverse_charge"]
    assert any("reverse_charge" in e for e in errors_of(i))


def test_unregistered_recipient_50000_rule():
    i = base()
    i["recipient"] = {"name": "Ravi"}
    errs = errors_of(i)
    assert any("Rs 50,000 or more" in e for e in errs)
    i["recipient"] = {"name": "Ravi", "address": "Pune", "delivery_address": "Pune", "state_code": "27"}
    assert not any("Rs 50,000" in e for e in errors_of(i))
    small = base()
    small["recipient"] = {}
    small["lines"][0].update({"taxable_value": "1000.00", "igst": "180.00"})
    assert not any("Rs 50,000" in e for e in errors_of(small))


def test_e_invoice_required_above_5_crore():
    i = base()
    i["supplier_aato"] = "60000000"
    assert any("IRN" in e for e in errors_of(i))
    i["irn"], i["qr_code"] = "a" * 64, "signedqr"
    r = inv.check_invoice(i)
    assert r["ok"] and not any("30 days" in w for w in r["warnings"])
    i["supplier_aato"] = "120000000"
    assert any("30 days" in w for w in inv.check_invoice(i)["warnings"])


def test_e_invoice_exempt_category_and_b2c():
    i = base()
    i["supplier_aato"] = "600000000"
    i["supplier"]["e_invoice_exempt_category"] = "banking_company"
    assert inv.check_invoice(i)["ok"]
    b2c = base()
    b2c["supplier_aato"] = "600000000"
    b2c["recipient"] = {"name": "A", "address": "B", "delivery_address": "B", "state_code": "27"}
    assert not any("IRN" in e for e in errors_of(b2c))


def test_export_with_urp_and_pos_96():
    i = base()
    i["recipient"] = {"name": "Foreign Co", "address": "London", "gstin": "URP"}
    i["place_of_supply"] = "96"
    i["supply_type"] = "inter-state"
    r = inv.check_invoice(i)
    assert r["supply_type"] == "inter-state"
    assert any("SUPPLY MEANT FOR EXPORT" in w for w in r["warnings"])


def test_invalid_gstins_reported():
    i = base()
    i["supplier"]["gstin"] = "29AAACE1234F1Z3"
    i["recipient"]["gstin"] = "27AAACB5678K1ZB"
    errs = errors_of(i)
    assert any(e.startswith("supplier.gstin invalid") for e in errs)
    assert any(e.startswith("recipient.gstin invalid") for e in errs)


def test_utgst_warning_for_chandigarh_supplier():
    i = base()
    i["supplier"]["gstin"] = "04AAACD3456M1ZO"
    i["place_of_supply"] = "04"
    i["supply_type"] = "intra-state"
    i["recipient"]["gstin"] = "04AAACD3456M1ZO"
    i["lines"][0].pop("igst")
    i["lines"][0].update({"cgst": "9000.00", "utgst": "9000.00"})
    r = inv.check_invoice(i)
    assert r["ok"] and any("UTGST" in w for w in r["warnings"])


def test_cli(tmp_path):
    p = tmp_path / "inv.json"
    p.write_text(json.dumps(base()))
    exe = [sys.executable, str(script_path(SKILL, "invoice_check"))]
    assert subprocess.run(exe + [str(p)], capture_output=True, text=True).returncode == 0
    bad = base()
    bad["lines"][0]["igst"] = "1"
    p.write_text(json.dumps(bad))
    r = subprocess.run(exe + [str(p)], capture_output=True, text=True)
    assert r.returncode == 1 and "ERROR" in r.stdout
    r = subprocess.run(exe + ["--example"], capture_output=True, text=True)
    assert json.loads(r.stdout)["supplier"]["gstin"] == SUP_KA
