"""Webhook commands: listen for incoming webhooks and ping a URL."""

import json
from datetime import datetime, timezone

import click
import requests as http_requests

from chapa_cli.output import console, print_error, print_json, print_success


@click.group()
def webhook():
    """Webhook utilities."""


@webhook.command()
@click.argument("path")
@click.option("--port", type=int, default=5000, help="Port to listen on (default 5000).")
# FIX: was 0.0.0.0; default to localhost
@click.option("--host", default="127.0.0.1", help="Host to bind to (use 0.0.0.0 for all interfaces).")
def listen(path, port, host):
    """Start a local server to receive and display webhook payloads.

    PATH is the URL path to listen on (e.g. /webhook or /pay/chapa-webhook).
    """
    try:
        from flask import Flask, request as flask_request
    except ImportError:
        print_error("Flask is required for webhook listener. Install it: pip install flask")
        raise SystemExit(1)

    if not path.startswith("/"):
        path = "/" + path

    app = Flask("chapa-webhook-listener")

    @app.route(path, methods=["POST"])
    def handle_webhook():
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        console.print(f"\n[bold cyan]--- Webhook received at {timestamp} ---[/]")

        console.print("[dim]Headers:[/]")
        for key, value in flask_request.headers:
            if key.lower().startswith(("x-", "content-", "chapa")):
                console.print(f"  {key}: {value}")

        try:
            body = flask_request.get_json(force=True)
        except Exception:
            body = flask_request.data.decode("utf-8", errors="replace")

        console.print("[dim]Body:[/]")
        if isinstance(body, dict):
            print_json(body)
        else:
            console.print(f"  {body}")

        console.print("[bold cyan]--- End ---[/]\n")
        return {"status": "received"}, 200

    console.print(
        f"[bold green]Listening for webhooks[/] on "
        f"[bold]http://{host}:{port}{path}[/]"
    )
    console.print("[yellow]Warning: This is a development tool. No signature verification is performed.[/]")
    console.print("[dim]Press Ctrl+C to stop.[/]\n")

    app.run(host=host, port=port, debug=False)


@webhook.command()
@click.argument("url")
@click.option("--data", default=None, help="JSON payload to send (string).")
def ping(url, data):
    """Send a test POST request to a webhook URL."""
    payload = {
        "event": "ping",
        "message": "Test webhook from Chapa CLI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if data:
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            print_error("Invalid JSON in --data argument.")
            raise SystemExit(1)

    try:
        resp = http_requests.post(url, json=payload, timeout=10)
        print_success(f"POST {url} -> {resp.status_code}")
        try:
            print_json(resp.json())
        except ValueError:
            console.print(resp.text)
    except http_requests.RequestException as e:
        print_error(f"Request failed: {e}")
        raise SystemExit(1)
