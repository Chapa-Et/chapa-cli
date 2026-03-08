"""Authentication and configuration commands."""

import click

from chapa_cli.config import (
    get_base_url,
    get_secret_key,
    remove_secret_key,
    set_base_url,
    set_secret_key,
)
from chapa_cli.output import print_error, print_success


@click.command()
def login():
    """Authenticate with your Chapa secret key."""
    key = click.prompt("Enter your Chapa secret key", hide_input=True)
    if not key.strip():
        print_error("Secret key cannot be empty.")
        raise SystemExit(1)

    set_secret_key(key.strip())
    print_success("Logged in successfully. Key stored in ~/.chapa-cli/config.json")


@click.command()
def logout():
    """Remove stored credentials."""
    if get_secret_key() is None:
        print_error("Not currently logged in.")
        raise SystemExit(1)

    remove_secret_key()
    print_success("Logged out. Credentials removed.")


@click.group()
def config():
    """Manage CLI configuration."""


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a configuration value.

    \b
    Supported keys:
      base-url    The API base URL (default: https://api.chapa.co)
    """
    if key == "base-url":
        set_base_url(value)
        print_success(f"Base URL set to {value}")
    else:
        print_error(f"Unknown config key: {key}. Supported: base-url")
        raise SystemExit(1)


@config.command("get")
@click.argument("key")
def config_get(key):
    """Get a configuration value.

    \b
    Supported keys:
      base-url    The API base URL
    """
    if key == "base-url":
        click.echo(get_base_url())
    else:
        print_error(f"Unknown config key: {key}. Supported: base-url")
        raise SystemExit(1)
