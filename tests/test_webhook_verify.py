"""Tests for webhook signature verification."""

import hmac
import hashlib

import pytest

from chapa_cli.webhook_verify import verify_webhook_signature, get_signature_header_value


def test_verify_webhook_signature_valid():
    secret = "whsec-test"
    body = b'{"event":"payment.success"}'
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert verify_webhook_signature(body, sig, secret) is True


def test_verify_webhook_signature_invalid():
    body = b'{"event":"payment.success"}'
    assert verify_webhook_signature(body, "wrong-sig", "whsec-test") is False


def test_verify_webhook_signature_empty_secret():
    assert verify_webhook_signature(b"body", "sig", "") is False


def test_verify_webhook_signature_empty_header():
    assert verify_webhook_signature(b"body", "", "secret") is False


def test_get_signature_header_value():
    headers = {"X-Chapa-Signature": "abc123", "Content-Type": "application/json"}
    assert get_signature_header_value(headers) == "abc123"


def test_get_signature_header_value_custom_name():
    headers = {"X-My-Sig": "xyz"}
    assert get_signature_header_value(headers, "X-My-Sig") == "xyz"
