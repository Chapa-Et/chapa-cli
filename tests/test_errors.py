"""Tests for structured error types (error_code, error_type, error_message)."""

import pytest

from chapa_cli.errors import (
    APIError,
    ChapaError,
    NetworkError,
    api_error_from_response,
    network_error_from_exception,
)


def test_chapa_error_has_required_fields():
    e = ChapaError(
        error_code="test_code",
        error_type="test_type",
        error_message="Test message",
    )
    assert e.error_code == "test_code"
    assert e.error_type == "test_type"
    assert e.error_message == "Test message"
    assert str(e) == "Test message"
    d = e.to_dict()
    assert d["error_code"] == "test_code"
    assert d["error_type"] == "test_type"
    assert d["error_message"] == "Test message"


def test_chapa_error_with_details():
    e = ChapaError("c", "t", "m", details={"key": "value"})
    assert e.to_dict()["details"] == {"key": "value"}


def test_network_error():
    e = NetworkError("timeout", "Connection timed out")
    assert e.error_type == "network_error"
    assert e.error_code == "timeout"
    assert e.error_message == "Connection timed out"


def test_api_error_from_response_dict():
    e = api_error_from_response(400, {"message": "Bad request", "code": "invalid"})
    assert e.error_type == "client_error"
    assert e.error_code == "invalid"
    assert e.error_message == "Bad request"
    assert e.status_code == 400
    assert e.body == {"message": "Bad request", "code": "invalid"}
    d = e.to_dict()
    assert d["details"].get("status_code") == 400


def test_api_error_from_response_5xx():
    e = api_error_from_response(500, {"error": "Internal error"})
    assert e.error_type == "server_error"
    assert e.status_code == 500
    assert "Internal error" in e.error_message


def test_api_error_from_response_malformed():
    e = api_error_from_response(400, "plain text")
    assert e.error_type == "malformed_response"
    assert e.error_code == "malformed_response"
    assert e.body == "plain text"


def test_network_error_from_exception():
    exc = Exception("Connection timed out")
    e = network_error_from_exception(exc)
    assert e.error_code == "timeout"
    assert e.error_type == "network_error"
    assert "timed out" in e.error_message
