import click
import requests
from flask import Flask, request
from pyngrok import ngrok

app = Flask(__name__)

@click.group()
def webhook():
    """Webhook-related commands."""
    pass

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
        click.echo(f"Webhook received: {data}")
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
        click.echo(f"Ping successful: {response.json()}")
    else:
        click.echo(f"Ping failed: {response.status_code}")
   
   
@webhook.command()
@click.argument('port')
def tunnel(port):
    """Create a tunnel for the specified port."""
    try:
        # Start ngrok tunnel
        public_url = ngrok.connect(port)
        click.echo(f"Ngrok tunnel started at {public_url}")

        # Optional: You can keep the tunnel open until the user stops it manually
        click.echo("Press Ctrl+C to stop the tunnel...")
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()

    except Exception as e:
        click.echo(f"Failed to start ngrok tunnel: {str(e)}")
             
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
