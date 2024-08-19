import click
import sys 
import requests
from chapa_cli.utils import load_token

from rich.console import Console
from rich.table import Table 
from datetime import datetime
from rich import print as rprint
from rich.panel import Panel


API_URL = "https://api.chapa.co/v1"

#Create a console object
console = Console()

# Function to format the dates
def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")


def print_banks_info(response):
    # Check if the response contains the expected keys
    if 'data' not in response:
        print("No bank data available.")
        return

    banks = response['data']
    # print(f"\n{response['message']}\n")

    table = Table(title="List of Supported Banks Information")

    # Add columns to the table with adjusted width
    table.add_column("Bank ID", justify="right", style="cyan", no_wrap=True, width=8)
    table.add_column("Name", style="magenta", width=20)
    table.add_column("SWIFT", style="green", width=8)
    table.add_column("Acc. Length", justify="right", width=6)
    table.add_column("Currency", style="blue", width=8)
    table.add_column("Mobile", justify="center", width=10)
    table.add_column("RTGS", justify="center", width=5)
    table.add_column("24Hrs", justify="center", width=4)
    table.add_column("Active", justify="center", width=8)
    table.add_column("Created", justify="center", width=10)
    table.add_column("Updated", justify="center", width=10)
    

    # Add rows to the table
    for bank in banks:
        table.add_row(
            str(bank["id"]),
            bank["name"],
            bank["swift"],
            str(bank["acct_length"]),
            bank["currency"],
            "Y" if bank["is_mobilemoney"] else "N",
            "Y" if bank["is_rtgs"] else "N",
            "Y" if bank["is_24hrs"] else "N",
            "Y" if bank["is_active"] else "N",
            format_date(bank["created_at"]),
            format_date(bank["updated_at"])
        )
    # Print the table
    console.print(table)

def print_transaction_events(response):
    """Prints transaction events in a readable format."""
    if 'data' not in response:
        print("No transaction events available.")
        return

    events = response['data']
    
    #print(f"\n{response['message']}\n")
    table = Table(title="Transaction Events Fetched")


    table.add_column("Event Item",justify="right",style="cyan",no_wrap=True, width=10)
    table.add_column("Message",style="magenta",justify="left",no_wrap=True,width=60)
    table.add_column("Type",style="green",no_wrap=True,width=5)
    
    # type color green if it is log and red if it is error
    table.add_column("Created At:",style="yellow",no_wrap=True,width=11)
    table.add_column("Updated At:",style="blue",no_wrap=True,width=11)
    
    for event in events:
        table.add_row(str(event['item']),
                      str(event['message']),
                      event['type'], 
                      format_date(event['created_at']),
                      format_date(event['updated_at']))
        
    
    console.print(table)


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
    
    table = Table(show_header=True, header_style="bold magenta",title=f"{response['message']}".capitalize())
    
    table.add_column("Information",justify="left",style="cyan",no_wrap=True, width=25)
    table.add_column("Result",justify="right",style="cyan",no_wrap=True, width=25)
    
    table.add_row("Status",f"{data['status']}")
    for key,value in data.items():
        if key == 'customization':
            # Add customization details as separate rows
            table.add_row("Customization Title", str(data['customization']['title']))
            table.add_row("Customization Description", str(data['customization']['description']))
            table.add_row("Customization Logo", str(data['customization']['logo']))
            
        if key in ['created_at','updated_at']:
            table.add_row(key.replace("_", " ").capitalize(),format_date(str(value)))

        if not key in ['customization','created_at','updated_at']:
            table.add_row(key.replace("_", " ").capitalize(), str(value))
    
    rprint(table)

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
    table = Table.grid()
    table.add_column(justify="left", style="bold")
    table.add_column(justify="left")
    
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

    data = response.json()
    if response.status_code == 200:
        for key,value in data.items():
            if key != "data":
                table.add_row(f"{key.capitalize()}:", str(value))
                
        if 'data' in data and 'checkout_url' in data['data']:
            checkout_url = data['data']['checkout_url']
            table.add_row("Checkout URL:", checkout_url)
        rprint(Panel(table, title="[bold green]Transaction initialized successfully[/bold green]"))
        #click.echo(f"Transaction initialized successfully: {response.json()}")
    else:
        for key,value in response.json().items():
            table.add_row(f"{key.capitalize()}: ", str(value))
        rprint(Panel(table, title="[bold red]Failed to initialize transaction[/bold red]"))

@transaction.command()
@click.argument("reference")
def verify(reference):
    table = Table.grid()
    table.add_column(justify="left", style="bold")
    table.add_column(justify="left")

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
        for key,value in response.json().items():
           table.add_row(f"{key.capitalize()}: ", str(value))
        rprint(Panel(table, title="[bold red]Failed to verify transaction[/bold red]"))
        # click.echo(f"Failed to verify transaction: {response.json()}"
        
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
    table = Table.grid()
    table.add_column(justify="left", style="bold")
    table.add_column(justify="left")
    
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
        for key,value in response.json().items():
           table.add_row(f"{key.capitalize()}: ", str(value))
        rprint(Panel(table, title="[bold red]Failed to get transaction events[/bold red]"))
        #click.echo(f"Failed to get transaction events: {response.json()}")


@transaction.command()
@click.option('--page', default=1, help='Page number for paginated results.')
def getall(page):
    table = Table.grid()
    table.add_column(justify="left", style="bold")
    table.add_column(justify="left")

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
        #for key,value in response.items():
        #    table.add_row(key.capitalize(), str(value))
        click.echo(f"Failed to get transactions: {response.json()}")


@transaction.command()
@click.argument('tx_ref')
def verify(tx_ref):
    table = Table.grid()
    table.add_column(justify="left", style="bold")
    table.add_column(justify="left")
    
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
        for key,value in response.json().items():
            table.add_row(f"{key.capitalize()}: ", str(value))
            
        rprint(Panel(table, title="[bold red]Failed to verify transaction[/bold red]"))
        #click.echo(f"Failed to verify transaction: {response.json()}")
