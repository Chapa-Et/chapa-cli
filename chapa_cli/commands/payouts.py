"""Payout commands: create, verify, list, bulk."""

import json
from pathlib import Path

import click

from chapa_cli.client import ChapaClient
from chapa_cli.errors import ChapaError
from chapa_cli.output import print_error, print_list_response, print_response


@click.group()
def payouts():
    """Manage payouts."""


@payouts.command()
@click.option("--amount", required=True, type=int, help="Amount (min 100).")
@click.option("--account-number", default=None, help="Recipient account number.")
@click.option("--account-name", default=None, help="Recipient account name.")
@click.option("--bank-slug", default=None, help="Bank slug (e.g. cbe, awash).")
@click.option("--currency", default=None, help="Currency code (defaults to ETB).")
@click.option("--reference", default=None, help="Merchant reference.")
@click.option("--reason", default=None, help="Payout reason.")
# FIX: mutually exclusive with detail opts
@click.option("--account-reference", default=None,
              help="Saved account reference (instead of account details).")
def create(amount, account_number, account_name, bank_slug, currency,
           reference, reason, account_reference):
    """Create a single payout.

    Provide either --account-reference OR all of --account-number,
    --account-name, and --bank-slug.
    """
    has_details = any([account_number, account_name, bank_slug])
    if account_reference and has_details:
        print_error("Provide --account-reference OR account details, not both.")
        raise SystemExit(1)
    if not account_reference and not all([account_number, account_name, bank_slug]):
        print_error("Provide --account-number, --account-name, and --bank-slug (or use --account-reference).")
        raise SystemExit(1)

    payload: dict = {"amount": amount}
    if account_reference:
        payload["account_reference"] = account_reference
    else:
        payload["account"] = {
            "account_number": account_number,
            "account_name": account_name,
            "bank_slug": bank_slug,
        }
    if currency:
        payload["currency"] = currency
    if reference:
        payload["merchant_reference"] = reference
    if reason:
        payload["reason"] = reason

    try:
        result = ChapaClient().create_payout(payload)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@payouts.command()
@click.argument("reference")
def verify(reference):
    """Verify a payout by reference."""
    try:
        result = ChapaClient().verify_payout(reference)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@payouts.command("list")
@click.option("--limit", type=int, default=None, help="Number of results (1-100).")
@click.option("--cursor", default=None, help="Pagination cursor.")
@click.option("--reference", default=None, help="Filter by merchant reference.")
@click.option("--status", default=None, help="Filter by status.")
@click.option("--currency", default=None, help="Filter by currency.")
@click.option("--bank-slug", default=None, help="Filter by bank slug.")
@click.option("--account-number", default=None, help="Filter by account number.")
@click.option("--from", "from_date", default=None, help="Start date (ISO format).")
@click.option("--to", "to_date", default=None, help="End date (ISO format).")
@click.option("--min", "min_amount", type=int, default=None, help="Minimum amount.")
@click.option("--max", "max_amount", type=int, default=None, help="Maximum amount.")
def list_payouts(limit, cursor, reference, status, currency, bank_slug,
                 account_number, from_date, to_date, min_amount, max_amount):
    """List payouts with optional filters."""
    params = {}
    if limit is not None:
        params["limit"] = limit
    if cursor:
        params["cursor"] = cursor
    if reference:
        params["reference"] = reference
    if status:
        params["status"] = status
    if currency:
        params["currency"] = currency
    if bank_slug:
        params["bank_slug"] = bank_slug
    if account_number:
        params["account_number"] = account_number
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if min_amount is not None:
        params["min"] = min_amount
    if max_amount is not None:
        params["max"] = max_amount

    try:
        result = ChapaClient().list_payouts(params)
        print_list_response(
            result,
            columns=["Reference", "Amount", "Currency", "Status", "Bank", "Account", "Created"],
            row_keys=[
                "chapa_reference", "amount", "currency", "status",
                "account.bank_slug", "account.account_number", "created_at",
            ],
            title="Payouts",
        )
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@payouts.command()
@click.option("--file", "file_path", required=True, type=click.Path(exists=True),
              help="Path to JSON file containing bulk payout items.")
def bulk(file_path):
    """Create bulk payouts from a JSON file.

    \b
    The JSON file should have this structure:
    {
      "items": [
        {
          "amount": 100,
          "account": {
            "account_number": "1000...",
            "account_name": "John Doe",
            "bank_slug": "cbe"
          }
        }
      ],
      "currency": "ETB"
    }
    """
    path = Path(file_path)
    try:
        payload = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print_error(f"Failed to read JSON file: {e}")
        raise SystemExit(1)

    if "items" not in payload:
        print_error("JSON file must contain an 'items' array.")
        raise SystemExit(1)

    try:
        result = ChapaClient().bulk_payout(payload)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)
