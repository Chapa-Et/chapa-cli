import click
import ssl
import socket
import requests
import hmac
import hashlib
from flask import Flask, request
from pyngrok import ngrok
from urllib.parse import urlparse

app = Flask(__name__)

@click.group()
def webhook():
    """Webhook-related commands."""
    pass

def verify_webhook_url(url, secret_key=None):
    """Verify the webhook URL: reachability, POST method, and SSL certificate."""
    try:
        click.echo("Pinging URL to check if it is reachable...")
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            click.echo(click.style(f"URL is not reachable. Status code: {response.status_code}", fg="red"))
            return False

        click.echo(click.style("URL is reachable.", fg="green"))

        click.echo("Sending POST request to check method support...")
        test_data = {
            "event": "cli.test",
            "message": "Selam from chapa-cli"
        }
        
        headers = {}
        if secret_key:
            payload = str(test_data)
            hash = hmac.new(secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
            cshash = hmac.new(secret_key.encode(), secret_key.encode(), hashlib.sha256).hexdigest()
            headers = {
                'Chapa-Signature': cshash,
                'x-chapa-signature': hash,
            }

        post_response = requests.post(url, json=test_data, headers=headers, timeout=5)
        if post_response.status_code != 200:
            click.echo(click.style(f"POST request failed. Status code: {post_response.status_code}", fg="red"))
            return False

        click.echo(click.style("URL is reachable and supports POST method.", fg="green"))

        click.echo("Checking SSL certificate...")
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        if parsed_url.scheme != "https":
            click.echo(click.style("Only HTTPS URLs are supported for Chapa Webhook URL verification.", fg="red"))
            return False

        context = ssl.create_default_context()

        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                click.echo(click.style("SSL certificate is valid.", fg="green"))

                click.echo("Checking SSL Subject...")
                click.echo(click.style(f"Subject: {dict(x[0] for x in cert['subject'])}", fg="green"))

                click.echo("Checking SSL Issuer...")
                click.echo(click.style(f"Issuer: {dict(x[0] for x in cert['issuer'])}", fg="green"))

                click.echo("Checking SSL Validity Period...")
                click.echo(click.style(f"Valid From: {cert['notBefore']}", fg="green"))
                click.echo(click.style(f"Valid Until: {cert['notAfter']}", fg="green"))

        return True

    except requests.RequestException as e:
        click.echo(click.style(f"Failed to reach URL: {str(e)}", fg="red"))
        return False
    except ssl.SSLError as e:
        click.echo(click.style(f"SSL certificate verification failed: {str(e)}", fg="red"))
        return False
    except Exception as e:
        click.echo(click.style(f"An error occurred: {str(e)}", fg="red"))
        return False


@webhook.command()
@click.argument("url")
def listen(url):
    """Listen to a webhook endpoint."""
    # Extract the path from the URL
    if not url.startswith('/'):
        if '//' in url:
            url = url.split('//', 1)[-1]
        url = '/' + url.split('/', 1)[-1]
    
    @app.route(url, methods=['POST'])
    def chapa_webhook():
        data = request.json
        click.echo(click.style(f"Webhook received: {data}", fg="green"))
        return "", 200

    port = int(url.split(':')[-1]) if ':' in url else 5000
    app.run(port=port)

@webhook.command()
@click.argument("url")
def ping(url):
    """Ping a webhook endpoint to test connectivity."""
    data = {
        "event": "ping",
        "message": "Webhook test ping"
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        click.echo(click.style(f"Ping successful: {response.json()}", fg="green"))
    else:
        click.echo(click.style(f"Ping failed: {response.status_code}", fg="red"))

@webhook.command()
@click.argument("url")
@click.option('--usekey', help='The secret key for signing the request.')
def verifywebhook(url, usekey):
    """Verify the webhook URL by checking reachability, POST method, and SSL using Chapa's standard webhook protocol."""
    if verify_webhook_url(url, secret_key=usekey):
        click.echo(click.style("Webhook URL verified successfully.", fg="green"))
    else:
        click.echo(click.style("Webhook URL verification failed.", fg="red"))

@webhook.command()
@click.argument('port')
def tunnel(port):
    """Create a tunnel for the specified port."""
    try:
        # Start ngrok tunnel
        public_url = ngrok.connect(port)
        click.echo(click.style(f"Ngrok tunnel started at {public_url}", fg="green"))

        # Optional: You can keep the tunnel open until the user stops it manually
        click.echo("Press Ctrl+C to stop the tunnel...")
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()

    except Exception as e:
        click.echo(click.style(f"Failed to start ngrok tunnel: {str(e)}", fg="red"))

if __name__ == "__main__":
    webhook()
