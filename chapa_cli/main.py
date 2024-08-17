import click
from getpass import getpass  
from chapa_cli import webhook, transaction
from chapa_cli.utils import save_token, load_token

from time import sleep
from rich.console import Console
from rich.text import Text
from rich.theme import Theme

#create a console object 
console = Console()





sucess_theme = Theme({"highlight":"bold Green"})
error_theme = Theme({"highlight":"bold red"})


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
            try:
                with console.status(f"[bold white][/bold white]", spinner="dots"):
                    #Simulate some work
                    sleep(1)
            finally:
                # Ensure the cursor is visible again
                console.show_cursor(True)

            sucess_console = Console(theme=sucess_theme)
            success_text = Text("Login successful!")
            success_text.highlight_words(["Login successful!"], style="highlight")
            sucess_console.print(success_text)
        else:
            error_console = Console(theme=error_theme)
            error_text = Text("Login failed. Please try again.")
            error_text.highlight_words(["Login failed."], style="highlight")
            error_console.print(error_text)
            
    else:
        error_console = Console(theme=error_theme)
        empty_text = Text("Token cannot be empty. Please try again.")
        empty_text.highlight_words(["Token cannot be empty."], style="highlight")
        error_console.print(empty_text)

# Register the commands
cli.add_command(transaction.transaction)
cli.add_command(webhook.webhook)

if __name__ == "__main__":
    cli()