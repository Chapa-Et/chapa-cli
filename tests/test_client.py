"""Tests for ChapaClient: success, APIError, and error structure."""

from unittest.mock import patch, MagicMock

import pytest
import requests

from chapa_cli.client import ChapaClient
from chapa_cli.errors import APIError, NetworkError


@pytest.fixture
def mock_config():
    with patch("chapa_cli.client.get_base_url", return_value="https://api.chapa.co"), \
         patch("chapa_cli.client.require_secret_key", return_value="test-key"):
        yield


@pytest.fixture
def client(mock_config):
    return ChapaClient(timeout=5, max_retries=0)


def test_handle_raises_api_error_with_structure(client):
    resp = MagicMock()
    resp.status_code = 400
    resp.json.return_value = {"message": "Invalid amount", "code": "validation_error"}
    with pytest.raises(APIError) as exc_info:
        client._handle(resp)
    e = exc_info.value
    assert e.error_code == "validation_error"
    assert e.error_type == "client_error"
    assert "Invalid amount" in e.error_message
    assert e.status_code == 400
    d = e.to_dict()
    assert d["error_code"] == "validation_error"
    assert "details" in d


def test_handle_returns_body_on_success(client):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"status": "success", "data": {}}
    out = client._handle(resp)
    assert out["status"] == "success"
    assert "data" in out


def test_request_raises_network_error_on_connection_failure(client):
    with patch.object(client.session, "request", side_effect=requests.ConnectionError("Connection refused")):
        with pytest.raises(NetworkError) as exc_info:
            client._request("GET", "https://api.chapa.co/v2/payments")
    e = exc_info.value
    assert e.error_type == "network_error"
    assert "error_code" in e.to_dict()
