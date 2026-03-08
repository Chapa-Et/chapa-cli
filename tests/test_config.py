"""Tests for config: env overrides, overridable env names."""

import os
from unittest.mock import patch, MagicMock

import pytest

from chapa_cli.config import (
    get_base_url,
    get_secret_key,
    get_webhook_secret,
    load_config,
    DEFAULT_BASE_URL,
)


def test_get_secret_key_from_chapa_private_key():
    with patch.dict(os.environ, {"CHAPA_PRIVATE_KEY": "key-from-private"}, clear=False):
        assert get_secret_key() == "key-from-private"


def test_get_secret_key_from_chapa_secret_key():
    old_private = os.environ.pop("CHAPA_PRIVATE_KEY", None)
    try:
        with patch.dict(os.environ, {"CHAPA_SECRET_KEY": "key-from-secret"}, clear=False):
            assert get_secret_key() == "key-from-secret"
    finally:
        if old_private is not None:
            os.environ["CHAPA_PRIVATE_KEY"] = old_private


def test_get_secret_key_overridable_env_name():
    with patch.dict(os.environ, {"CUSTOM_KEY": "custom-value"}, clear=False):
        assert get_secret_key(env_var_name="CUSTOM_KEY") == "custom-value"


def test_get_base_url_default():
    try:
        os.environ.pop("CHAPA_BASE_URL", None)
    except Exception:
        pass
    with patch("chapa_cli.config.load_config", return_value={}):
        assert get_base_url() == DEFAULT_BASE_URL


def test_get_base_url_from_env():
    with patch.dict(os.environ, {"CHAPA_BASE_URL": "https://custom.api.co"}, clear=False):
        assert get_base_url() == "https://custom.api.co"


def test_get_webhook_secret_from_env():
    with patch.dict(os.environ, {"CHAPA_WEBHOOK_SECRET": "whsec-123"}, clear=False):
        assert get_webhook_secret() == "whsec-123"


def test_get_webhook_secret_overridable_env_name():
    with patch.dict(os.environ, {"MY_WEBHOOK_SECRET": "my-secret"}, clear=False):
        assert get_webhook_secret(env_var_name="MY_WEBHOOK_SECRET") == "my-secret"


def test_load_config_empty_when_no_file():
    with patch("chapa_cli.config.CONFIG_FILE") as p:
        p.exists.return_value = False
        assert load_config() == {}
