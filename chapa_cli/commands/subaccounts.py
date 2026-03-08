"""Subaccount commands: create, list, update."""

import click

from chapa_cli.client import ChapaClient
from chapa_cli.errors import ChapaError
from chapa_cli.output import print_error, print_list_response, print_response


@click.group()
def subaccounts():
    """Manage subaccounts."""


@subaccounts.command()
@click.option("--name", required=True, help="Subaccount name.")
@click.option("--account-number", required=True, help="Bank account number.")
@click.option("--account-name", required=True, help="Bank account holder name.")
@click.option("--bank-slug", required=True, help="Bank slug (e.g. cbe).")
@click.option("--currency", required=True, help="Currency code (e.g. ETB).")
@click.option("--split-type", required=True,
              type=click.Choice(["percentage", "flat"], case_sensitive=False),
              help="Split type.")
@click.option("--split-value", required=True, type=int, help="Split value.")
@click.option("--min-amount", type=int, default=None, help="Minimum transaction amount.")
@click.option("--max-amount", type=int, default=None, help="Maximum transaction amount.")
@click.option("--primary", is_flag=True, default=False, help="Set as primary subaccount.")
def create(name, account_number, account_name, bank_slug, currency,
           split_type, split_value, min_amount, max_amount, primary):
    """Create a new subaccount."""
    payload: dict = {
        "subaccount_name": name,
        "account": {
            "account_number": account_number,
            "account_name": account_name,
            "bank_slug": bank_slug,
        },
        "currency": currency,
        "split_type": split_type,
        "split_value": split_value,
    }
    if min_amount is not None:
        payload["min_amount"] = min_amount
    if max_amount is not None:
        payload["max_amount"] = max_amount
    if primary:
        payload["is_primary"] = True

    try:
        result = ChapaClient().create_subaccount(payload)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@subaccounts.command("list")
@click.option("--limit", type=int, default=None, help="Number of results (1-100).")
@click.option("--cursor", default=None, help="Pagination cursor.")
@click.option("--reference", default=None, help="Filter by subaccount reference.")
@click.option("--currency", default=None, help="Filter by currency.")
@click.option("--bank-slug", default=None, help="Filter by bank slug.")
@click.option("--active/--inactive", "is_active", default=None,
              help="Filter by active status.")
def list_subaccounts(limit, cursor, reference, currency, bank_slug, is_active):
    """List subaccounts with optional filters."""
    params = {}
    if limit is not None:
        params["limit"] = limit
    if cursor:
        params["cursor"] = cursor
    if reference:
        params["reference"] = reference
    if currency:
        params["currency"] = currency
    if bank_slug:
        params["bank_slug"] = bank_slug
    if is_active is not None:
        params["is_active"] = str(is_active).lower()

    try:
        result = ChapaClient().list_subaccounts(params)
        print_list_response(
            result,
            columns=["Reference", "Name", "Bank", "Account", "Split", "Currency", "Active"],
            row_keys=[
                "subaccount_reference", "subaccount_name", "account.bank_slug",
                "account.account_number", "split_type", "currency", "is_active",
            ],
            title="Subaccounts",
        )
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@subaccounts.command()
@click.argument("reference")
@click.option("--split-type",
              type=click.Choice(["percentage", "flat"], case_sensitive=False),
              default=None, help="New split type.")
@click.option("--split-value", type=int, default=None, help="New split value.")
@click.option("--account-number", default=None, help="New account number.")
@click.option("--account-name", default=None, help="New account name.")
@click.option("--bank-slug", default=None, help="New bank slug.")
def update(reference, split_type, split_value, account_number, account_name, bank_slug):
    """Update a subaccount by reference."""
    payload: dict = {}

    account = {}
    if account_number:
        account["account_number"] = account_number
    if account_name:
        account["account_name"] = account_name
    if bank_slug:
        account["bank_slug"] = bank_slug
    if account:
        payload["account"] = account

    if split_type:
        payload["split_type"] = split_type
    if split_value is not None:
        payload["split_value"] = split_value

    if not payload:
        print_error("Provide at least one field to update.")
        raise SystemExit(1)

    try:
        result = ChapaClient().update_subaccount(reference, payload)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)
