import click
import requests
from chapa_cli.utils import load_token

API_URL = "https://api.chapa.co/v1"



def print_banks_info(response):
    # Check if the response contains the expected keys
    if 'data' not in response:
        print("No bank data available.")
        return

    banks = response['data']
    print(f"\n{response['message']}\n")
    
    for bank in banks:
        print(f"Bank ID: {bank['id']}")
        print(f"Name: {bank['name']}")
        print(f"Slug: {bank['slug']}")
        print(f"SWIFT Code: {bank['swift']}")
        print(f"Account Number Length: {bank['acct_length']}")
        print(f"Currency: {bank['currency']}")
        print(f"Country ID: {bank['country_id']}")
        print(f"Mobile Money: {'Yes' if bank['is_mobilemoney'] else 'No'}")
        print(f"RTGS Enabled: {'Yes' if bank['is_rtgs'] else 'No'}")
        print(f"24 Hours Service: {'Yes' if bank['is_24hrs'] else 'No'}")
        print(f"Active: {'Yes' if bank['is_active'] else 'No'}")
        print(f"Created At: {bank['created_at']}")
        print(f"Updated At: {bank['updated_at']}")
        print("\n" + "-" * 40 + "\n")

def print_transaction_events(response):
    """Prints transaction events in a readable format."""
    if 'data' not in response:
        print("No transaction events available.")
        return

    events = response['data']
    print(f"\n{response['message']}\n")
    
    for event in events:
        print(f"Event Item: {event['item']}")
        print(f"Message: {event['message']}")
        print(f"Type: {event['type']}")
        print(f"Created At: {event['created_at']}")
        print(f"Updated At: {event['updated_at']}")
        print("\n" + "-" * 40 + "\n")

def print_transactions_info(response):
    """Prints transactions in a readable format."""
    if 'data' not in response or 'transactions' not in response['data']:
        print("No transactions available.")
        return

    transactions = response['data']['transactions']
    for transaction in transactions:
        print(f"Status: {transaction['status']}")
        print(f"Reference ID: {transaction['ref_id']}")
        print(f"Type: {transaction['type']}")
        print(f"Created At: {transaction['created_at']}")
        print(f"Currency: {transaction['currency']}")
        print(f"Amount: {transaction['amount']}")
        print(f"Charge: {transaction['charge']}")
        print(f"Transaction ID: {transaction['trans_id']}")
        print(f"Payment Method: {transaction['payment_method']}")
        print("Customer Info:")
        print(f"  - ID: {transaction['customer']['id']}")
        print(f"  - Name: {transaction['customer']['first_name']} {transaction['customer']['last_name']}")
        print(f"  - Email: {transaction['customer']['email']}")
        print(f"  - Mobile: {transaction['customer']['mobile']}")
        print("\n" + "-" * 40 + "\n")

def print_payment_details(response):
    """Prints payment details in a readable format."""
    if 'data' not in response:
        print("No payment details available.")
        return

    data = response['data']
    print(f"Message: {response['message']}")
    print(f"Status: {data['status']}")
    print(f"First Name: {data['first_name']}")
    print(f"Last Name: {data['last_name']}")
    print(f"Email: {data['email']}")
    print(f"Currency: {data['currency']}")
    print(f"Amount: {data['amount']}")
    print(f"Charge: {data['charge']}")
    print(f"Mode: {data['mode']}")
    print(f"Method: {data['method']}")
    print(f"Type: {data['type']}")
    print(f"Reference: {data['reference']}")
    print(f"Transaction Reference: {data['tx_ref']}")
    if data.get('customization'):
        print("Customization:")
        print(f"  Title: {data['customization'].get('title')}")
        print(f"  Description: {data['customization'].get('description')}")
        print(f"  Logo: {data['customization'].get('logo')}")
    print(f"Created At: {data['created_at']}")
    print(f"Updated At: {data['updated_at']}")
    print("\n" + "-" * 40 + "\n")

@click.group()
def transaction():
    """Transaction-related commands."""
    pass

@transaction.command()
@click.option("--amount", required=True, help="The amount for the transaction.")
@click.option("--email", required=False, help="The customer's email.")
@click.option("--phone", required=False, help="The customer's phone number.")
@click.option("--currency", required=False, default="ETB", help="The currency for the transaction.")
@click.option("--tx_ref", required=False, help="Transaction reference (auto-generated if not provided).")
@click.option("--callback_url", required=False, help="URL to redirect to after payment.")
@click.option("--webhook_url", required=False, help="URL to receive transaction events.")
def initialize(amount, email, phone ,currency, tx_ref, callback_url, webhook_url):
    """Initialize a new transaction."""
    token = load_token()
    if not token:
        click.echo("Please login first using the `chapa login` command.")
        return

    data = {
        "amount": amount,
        "currency": currency,
        "email": email,
        "phone_number": phone,
        "tx_ref": tx_ref,
        "callback_url": callback_url ,
        "webhook": webhook_url
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/transaction/initialize", json=data, headers=headers)

    if response.status_code == 200:
        click.echo(f"Transaction initialized successfully: {response.json()}")
    else:
        click.echo(f"Failed to initialize transaction: {response.json()}")

@transaction.command()
@click.argument("reference")
def verify(reference):
    """Verify a transaction by its reference."""
    token = load_token()
    if not token:
        click.echo("Please login first using the `chapa login` command.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/transaction/verify/{reference}", headers=headers)

    if response.status_code == 200:
        click.echo(f"Transaction verified: {response.json()}")
    else:
        click.echo(f"Failed to verify transaction: {response.json()}")
        
@transaction.command()
def banks():
    """Get a list of supported banks."""
    token = load_token()
    if not token:
        click.echo("Please login first using the `chapa login` command.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/banks", headers=headers)

    if response.status_code == 200:
        print_banks_info(response.json())
    else:
        click.echo(f"Failed to get supported banks: {response.json()}")


@transaction.command()
@click.argument('reference')
def events(reference):
    """Get the events for a specific transaction."""
    token = load_token()
    if not token:
        click.echo("Please login first using the `chapa login` command.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_URL}/transaction/events/{reference}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print_transaction_events(response.json())
    else:
        click.echo(f"Failed to get transaction events: {response.json()}")


@transaction.command()
@click.option('--page', default=1, help='Page number for paginated results.')
def getall(page):
    """Get a list of transactions."""
    token = load_token()
    if not token:
        click.echo("Please login first using the `chapa login` command.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_URL}/transactions?page={page}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print_transactions_info(response.json())
    else:
        click.echo(f"Failed to get transactions: {response.json()}")


@transaction.command()
@click.argument('tx_ref')
def verify(tx_ref):
    """Verify a transaction by its reference."""
    token = load_token()
    if not token:
        click.echo("Please login first using the `chapa login` command.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_URL}/transaction/verify/{tx_ref}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print_payment_details(response.json())
    else:
        click.echo(f"Failed to verify transaction: {response.json()}")
