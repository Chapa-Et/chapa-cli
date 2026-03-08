"""Bank listing command."""

import click

from chapa_cli.client import ChapaClient
from chapa_cli.errors import ChapaError
from chapa_cli.output import print_error, print_list_response


@click.group()
def banks():
    """View supported banks."""


@banks.command("list")
@click.option("--country", default=None, help="Filter by country code (e.g. ET).")
def list_banks(country):
    """List supported banks."""
    params = {}
    if country:
        params["country"] = country

    try:
        result = ChapaClient().get_banks(params)
        print_list_response(
            result,
            columns=["Slug", "Name", "Country"],
            row_keys=["slug", "name", "country"],
            title="Supported Banks",
        )
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)
