"""Configuration management for Chapa CLI.

Central module for all configuration. Credentials in ~/.chapa-cli/config.json.
Default env vars: CHAPA_PRIVATE_KEY (or CHAPA_SECRET_KEY), CHAPA_WEBHOOK_SECRET,
CHAPA_BASE_URL. Env var names are overridable via optional parameters.
"""

import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_BASE_URL = "https://api.chapa.co"
CONFIG_DIR = Path.home() / ".chapa-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_ENV_SECRET_KEY = "CHAPA_PRIVATE_KEY"
DEFAULT_ENV_SECRET_KEY_ALT = "CHAPA_SECRET_KEY"
DEFAULT_ENV_WEBHOOK_SECRET = "CHAPA_WEBHOOK_SECRET"
DEFAULT_ENV_BASE_URL = "CHAPA_BASE_URL"


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load config from file. Returns empty dict if file does not exist."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(data: dict) -> None:
    """Persist config to file. Creates directory and sets secure permissions."""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(CONFIG_FILE, 0o600)


def get_secret_key(
    env_var_name: Optional[str] = None,
    env_var_name_alt: Optional[str] = None,
) -> Optional[str]:
    """Return API secret key from env or file. Env names overridable via args."""
    first = env_var_name or DEFAULT_ENV_SECRET_KEY
    alt = env_var_name_alt if env_var_name_alt is not None else DEFAULT_ENV_SECRET_KEY_ALT
    key = os.environ.get(first) or os.environ.get(alt)
    if key:
        return key
    return load_config().get("secret_key")


def set_secret_key(key: str) -> None:
    """Store the API secret key in config file (e.g. after login)."""
    cfg = load_config()
    cfg["secret_key"] = key
    save_config(cfg)


def remove_secret_key() -> None:
    """Remove the stored API secret key from config (e.g. logout)."""
    cfg = load_config()
    cfg.pop("secret_key", None)
    save_config(cfg)


def get_base_url(env_var_name: Optional[str] = None) -> str:
    """Return base URL from env or file. Env name overridable via env_var_name."""
    name = env_var_name or DEFAULT_ENV_BASE_URL
    env_url = os.environ.get(name)
    if env_url:
        return env_url.rstrip("/")
    return (load_config().get("base_url") or DEFAULT_BASE_URL).rstrip("/")


def get_webhook_secret(env_var_name: Optional[str] = None) -> Optional[str]:
    """Return webhook signing secret from env or file. Env name overridable."""
    name = env_var_name or DEFAULT_ENV_WEBHOOK_SECRET
    secret = os.environ.get(name)
    if secret:
        return secret
    return load_config().get("webhook_secret")


def set_base_url(url: str) -> None:
    """Store the API base URL in config. Trailing slash is stripped."""
    cfg = load_config()
    cfg["base_url"] = url.rstrip("/")
    save_config(cfg)


def require_secret_key() -> str:
    """Return the secret key or raise SystemExit with a helpful message."""
    key = get_secret_key()
    if not key:
        raise SystemExit(
            "Not authenticated. Run 'chapa login' or set CHAPA_PRIVATE_KEY / CHAPA_SECRET_KEY."
        )
    return key
