"""Payment commands: hosted checkout, direct charge, verify, list."""

import click

from chapa_cli.client import ChapaClient
from chapa_cli.errors import ChapaError
from chapa_cli.output import print_error, print_list_response, print_response


@click.group()
def payments():
    """Manage payments."""


@payments.command()
@click.option("--amount", required=True, type=int, help="Amount in minor units (min 100).")
@click.option("--currency", required=True, help="Currency code (e.g. ETB).")
@click.option("--email", default=None, help="Customer email.")
@click.option("--phone", default=None, help="Customer phone number.")
@click.option("--first-name", default=None, help="Customer first name.")
@click.option("--last-name", default=None, help="Customer last name.")
@click.option("--reference", default=None, help="Merchant reference.")
@click.option("--callback-url", default=None, help="Callback URL (https).")
@click.option("--return-url", default=None, help="Return URL (https).")
@click.option("--payment-methods", default=None,
              help="Comma-separated preferred payment methods.")
@click.option("--title", default=None, help="Checkout page title.")
@click.option("--description", default=None, help="Checkout page description.")
@click.option("--logo", default=None, help="Checkout page logo URL.")
def hosted(amount, currency, email, phone, first_name, last_name, reference,
           callback_url, return_url, payment_methods, title, description, logo):
    """Initialize a hosted checkout payment."""
    payload: dict = {"amount": amount, "currency": currency}

    customer = {}
    if email:
        customer["email"] = email
    if phone:
        customer["phone_number"] = phone
    if first_name:
        customer["first_name"] = first_name
    if last_name:
        customer["last_name"] = last_name
    if customer:
        payload["customer"] = customer

    if reference:
        payload["merchant_reference"] = reference
    if callback_url:
        payload["callback_url"] = callback_url
    if return_url:
        payload["return_url"] = return_url
    if payment_methods:
        payload["preferred_payment_methods"] = [
            m.strip() for m in payment_methods.split(",")
        ]

    customization = {}
    if title:
        customization["title"] = title
    if description:
        customization["description"] = description
    if logo:
        customization["logo"] = logo
    if customization:
        payload["customization"] = customization

    try:
        result = ChapaClient().initialize_payment(payload)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@payments.command()
@click.option("--method", required=True,
              type=click.Choice(
                  ["telebirr", "mpesa", "cbebirr", "ebirr", "enat_bank", "yaya", "link"],
                  case_sensitive=False,
              ),
              help="Payment method.")
@click.option("--amount", required=True, type=int, help="Amount (min 100).")
@click.option("--currency", required=True, help="Currency code.")
@click.option("--phone", required=True, help="Customer phone number.")
@click.option("--email", default=None, help="Customer email.")
@click.option("--first-name", default=None, help="Customer first name.")
@click.option("--last-name", default=None, help="Customer last name.")
@click.option("--reference", default=None, help="Merchant reference.")
@click.option("--callback-url", default=None, help="Callback URL.")
@click.option("--return-url", default=None, help="Return URL.")
def direct(method, amount, currency, phone, email, first_name, last_name,
           reference, callback_url, return_url):
    """Initialize a direct charge payment."""
    customer: dict = {"phone_number": phone}
    if email:
        customer["email"] = email
    if first_name:
        customer["first_name"] = first_name
    if last_name:
        customer["last_name"] = last_name

    payload: dict = {
        "payment_method": method,
        "amount": amount,
        "currency": currency,
        "customer": customer,
    }
    if reference:
        payload["merchant_reference"] = reference
    if callback_url:
        payload["callback_url"] = callback_url
    if return_url:
        payload["return_url"] = return_url

    try:
        result = ChapaClient().direct_charge(payload)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@payments.command()
@click.argument("reference")
def verify(reference):
    """Verify a payment by reference."""
    try:
        result = ChapaClient().verify_payment(reference)
        print_response(result)
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)


@payments.command("list")
@click.option("--limit", type=int, default=None, help="Number of results (1-100).")
@click.option("--cursor", default=None, help="Pagination cursor.")
@click.option("--reference", default=None, help="Filter by merchant reference.")
@click.option("--status", default=None, help="Filter by status.")
@click.option("--currency", default=None, help="Filter by currency.")
@click.option("--from", "from_date", default=None, help="Start date (ISO format).")
@click.option("--to", "to_date", default=None, help="End date (ISO format).")
@click.option("--min", "min_amount", type=int, default=None, help="Minimum amount.")
@click.option("--max", "max_amount", type=int, default=None, help="Maximum amount.")
def list_payments(limit, cursor, reference, status, currency, from_date, to_date,
                  min_amount, max_amount):
    """List payments with optional filters."""
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
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if min_amount is not None:
        params["min"] = min_amount
    if max_amount is not None:
        params["max"] = max_amount

    try:
        result = ChapaClient().list_payments(params)
        print_list_response(
            result,
            columns=["Reference", "Amount", "Currency", "Status", "Method", "Created"],
            row_keys=[
                "chapa_reference", "amount", "currency", "status",
                "payment_method", "created_at",
            ],
            title="Payments",
        )
    except ChapaError as e:
        print_error(e.error_message, e.to_dict())
        raise SystemExit(1)
