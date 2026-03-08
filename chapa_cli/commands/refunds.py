"""Refund commands: create, list, verify."""

import click

from chapa_cli.client import ChapaClient
from chapa_cli.errors import ChapaError
from chapa_cli.output import print_error, print_list_response, print_response


@click.group()
def refunds():
    """Manage refunds."""


@refunds.command()
@click.option("--payment-reference", required=True,
              help="Reference of the payment to refund.")
@click.option("--amount", type=int, default=None,
              help="Refund amount (omit for full refund, min 100).")
@click.option("--reason", default=None, help="Reason for the refund (max 400 chars).")
@click.option("--reference", default=None, help="Merchant reference for this refund.")
def create(payment_reference, amount, reason, reference):
    """Create a refund for a payment."""
    payload: dict = {"payment_reference": payment_reference}
    if amount is not None:
        payload["amount"] = amount
    if reason:
        payload["reason"] = reason
    if reference:
        payload["merchant_reference"] = reference

    try:
        result = ChapaClient().create_refund(payload)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@refunds.command("list")
@click.option("--limit", type=int, default=None, help="Number of results (1-100).")
@click.option("--cursor", default=None, help="Pagination cursor.")
@click.option("--reference", default=None, help="Filter by refund reference.")
@click.option("--status", default=None, help="Filter by status.")
@click.option("--from", "from_date", default=None, help="Start date (ISO format).")
@click.option("--to", "to_date", default=None, help="End date (ISO format).")
@click.option("--min", "min_amount", type=int, default=None, help="Minimum amount.")
@click.option("--max", "max_amount", type=int, default=None, help="Maximum amount.")
def list_refunds(limit, cursor, reference, status, from_date, to_date,
                 min_amount, max_amount):
    """List refunds with optional filters."""
    params = {}
    if limit is not None:
        params["limit"] = limit
    if cursor:
        params["cursor"] = cursor
    if reference:
        params["reference"] = reference
    if status:
        params["status"] = status
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if min_amount is not None:
        params["min"] = min_amount
    if max_amount is not None:
        params["max"] = max_amount

    try:
        result = ChapaClient().list_refunds(params)
        print_list_response(
            result,
            columns=["Reference", "Payment Ref", "Amount", "Status", "Reason", "Created"],
            row_keys=[
                "chapa_reference", "payment_reference", "amount",
                "status", "reason", "created_at",
            ],
            title="Refunds",
        )
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@refunds.command()
@click.argument("reference")
def verify(reference):
    """Verify a refund by reference."""
    try:
        result = ChapaClient().verify_refund(reference)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)
