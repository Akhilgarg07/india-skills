"""Tests for skills/razorpay-integration/scripts/razorpay_signature.py."""

import hashlib
import hmac
import json
import os
import subprocess
import sys
from decimal import Decimal

import pytest

from conftest import load_script, script_path

SKILL = "razorpay-integration"
rz = load_script(SKILL, "razorpay_signature")
SECRET = "test_secret_EXAMPLE"


def cli(*a, env=None):
    e = {k: v for k, v in os.environ.items() if not k.startswith("RAZORPAY_")}
    e.update(env or {})
    return subprocess.run([sys.executable, str(script_path(SKILL, "razorpay_signature")), *a],
                          capture_output=True, text=True, timeout=30, env=e)


def test_sign_matches_rfc4231_test_case_2():
    # RFC 4231 HMAC-SHA256 test case 2
    assert rz.sign("what do ya want for nothing?", "Jefe") == \
        "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"


def test_payment_signature_format_order_pipe_payment():
    sig = hmac.new(SECRET.encode(), b"order_IEIaMR65cu6nz3|pay_IH4NVgf4Dreq1l", hashlib.sha256).hexdigest()
    assert rz.verify_payment("order_IEIaMR65cu6nz3", "pay_IH4NVgf4Dreq1l", sig, SECRET)
    # swapped order / wrong secret / tampered signature all fail
    assert not rz.verify_payment("pay_IH4NVgf4Dreq1l", "order_IEIaMR65cu6nz3", sig, SECRET)
    assert not rz.verify_payment("order_IEIaMR65cu6nz3", "pay_IH4NVgf4Dreq1l", sig, "other")
    assert not rz.verify_payment("order_IEIaMR65cu6nz3", "pay_IH4NVgf4Dreq1l", sig[:-1] + "0", SECRET)
    assert not rz.verify_payment("order_IEIaMR65cu6nz3", "pay_IH4NVgf4Dreq1l", "", SECRET)


def test_signature_case_and_whitespace_tolerant():
    sig = rz.sign("order_1|pay_1", SECRET)
    assert rz.verify_payment("order_1", "pay_1", f" {sig.upper()} ", SECRET)


def test_subscription_signature_payment_first():
    sig = rz.sign("pay_1|sub_1", SECRET)
    assert rz.verify_subscription("pay_1", "sub_1", sig, SECRET)
    assert not rz.verify_subscription("sub_1", "pay_1", sig, SECRET)


def test_payment_link_signature():
    sig = rz.sign("plink_1|ref_42|paid|pay_9", SECRET)
    assert rz.verify_payment_link("plink_1", "ref_42", "paid", "pay_9", sig, SECRET)
    assert not rz.verify_payment_link("plink_1", "ref_42", "created", "pay_9", sig, SECRET)


def test_webhook_raw_body_vs_reserialised():
    raw = b'{"entity":"event","event":"payment.captured",  "payload":{"x":1}}'
    sig = hmac.new(b"whsec", raw, hashlib.sha256).hexdigest()
    assert rz.verify_webhook(raw, sig, "whsec")
    reserialised = json.dumps(json.loads(raw)).encode()
    assert not rz.verify_webhook(reserialised, sig, "whsec")  # why the raw body matters
    with pytest.raises(TypeError):
        rz.verify_webhook(raw.decode(), sig, "whsec")


@pytest.mark.parametrize("rupees,paise", [("499", 49900), ("499.00", 49900), ("1,499.50", 149950),
                                          ("₹10.05", 1005), (Decimal("0.01"), 1), ("100000", 10000000)])
def test_rupees_to_paise(rupees, paise):
    assert rz.rupees_to_paise(rupees) == paise


@pytest.mark.parametrize("bad", ["0", "-1", "10.005", "abc", "NaN"])
def test_rupees_to_paise_rejects(bad):
    with pytest.raises(ValueError):
        rz.rupees_to_paise(bad)


def test_rupees_to_paise_rejects_float():
    with pytest.raises(TypeError):
        rz.rupees_to_paise(499.99)


def test_paise_to_rupees():
    assert rz.paise_to_rupees(149950) == Decimal("1499.50")
    with pytest.raises(TypeError):
        rz.paise_to_rupees(1.5)


def test_cli_payment_uses_env_secret(tmp_path):
    sig = rz.sign("order_1|pay_1", SECRET)
    assert cli("payment", "order_1", "pay_1", sig, env={"RAZORPAY_KEY_SECRET": SECRET}).returncode == 0
    assert cli("payment", "order_1", "pay_1", "bad", env={"RAZORPAY_KEY_SECRET": SECRET}).returncode == 1
    assert cli("payment", "order_1", "pay_1", sig).returncode == 2       # no secret in env


def test_cli_webhook_and_paise(tmp_path):
    body = tmp_path / "body.json"
    body.write_bytes(b'{"event":"order.paid"}')
    sig = rz.sign(body.read_bytes(), "whsec")
    assert cli("webhook", str(body), sig, env={"RAZORPAY_WEBHOOK_SECRET": "whsec"}).returncode == 0
    r = cli("paise", "1,499.50")
    assert r.returncode == 0 and r.stdout.strip() == "149950"
    assert cli("paise", "1.234").returncode == 2
