"""Chapa CLI entry point."""

import click

from chapa_cli import __version__
from chapa_cli.commands.auth import login, logout, config
from chapa_cli.commands.payments import payments
from chapa_cli.commands.payouts import payouts
from chapa_cli.commands.banks import banks
from chapa_cli.commands.subaccounts import subaccounts
from chapa_cli.commands.refunds import refunds
from chapa_cli.commands.webhook import webhook


@click.group()
@click.option("--json", "json_output", is_flag=True, default=False,
              help="Output raw JSON (for scripting/piping).")
@click.version_option(version=__version__, prog_name="chapa")
@click.pass_context
def cli(ctx, json_output):
    """Chapa CLI - interact with the Chapa Payment API v2 from your terminal."""
    ctx.ensure_object(dict)
    ctx.params["json_output"] = json_output


cli.add_command(login)
cli.add_command(logout)
cli.add_command(config)
cli.add_command(payments)
cli.add_command(payouts)
cli.add_command(banks)
cli.add_command(subaccounts)
cli.add_command(refunds)
cli.add_command(webhook)


if __name__ == "__main__":
    cli()
