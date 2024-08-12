import click
from getpass import getpass  
from chapa_cli import webhook, transaction
from chapa_cli.utils import save_token, load_token

@click.group()
def cli():
    """Chapa CLI to manage your Chapa integration."""
    pass

@cli.command()
def login():
    """Login to Chapa CLI by providing your secret token."""
    token = getpass("Enter your Chapa secret token: ")
    if token:
        #TODO: validate the token with the server before saving
        
        #store the token
        save_token(token)
        #check if the token is saved
        if load_token():
            click.echo("Login successful!")
        else:
            click.echo("Login failed. Please try again.")
    else:
        click.echo("Token cannot be empty. Please try again.")

# Register the commands
cli.add_command(transaction.transaction)
cli.add_command(webhook.webhook)

if __name__ == "__main__":
    cli()
