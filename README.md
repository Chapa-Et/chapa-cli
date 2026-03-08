# Chapa CLI

Command-line tool for the Chapa Payment API v2. Manage payments, payouts, subaccounts, refunds, and webhooks directly from your terminal.

## Installation

### From PyPI

```bash
pip install --upgrade chapa-cli
```

### From Source

```bash
git clone https://github.com/Chapa-Et/chapa-cli.git
cd chapa-cli
pip install -e .
```

## Quick Start

### 1. Login

```bash
chapa login
# You will be prompted for your Chapa secret key
```

Or set the environment variable:

```bash
export CHAPA_PRIVATE_KEY=CHASECK-xxxxxxxxxxxxxxxx
# or
export CHAPA_SECRET_KEY=CHASECK-xxxxxxxxxxxxxxxx
```

### 2. Try a Command

```bash
chapa banks list
chapa payments list --limit 5
```

## Configuration

Credentials are stored in `~/.chapa-cli/config.json`.

### Environment Variables

| Variable | Description |
|---|---|
| `CHAPA_PRIVATE_KEY` or `CHAPA_SECRET_KEY` | API secret key (overrides stored config) |
| `CHAPA_WEBHOOK_SECRET` | Webhook signing secret for signature verification |
| `CHAPA_BASE_URL` | API base URL (default: `https://api.chapa.co`) |

### Set Base URL

```bash
chapa config set base-url https://api.chapa.co
chapa config get base-url
```

## Global Options

| Flag | Description |
|---|---|
| `--json` | Output raw JSON for scripting/piping |
| `--version` | Show CLI version |
| `--help` | Show help for any command |

## Commands

### Payments

**Initialize a hosted checkout:**

```bash
chapa payments hosted \
  --amount 1000 \
  --currency ETB \
  --email customer@example.com \
  --phone 0911112233 \
  --first-name John \
  --last-name Doe \
  --callback-url https://example.com/callback \
  --return-url https://example.com/return \
  --title "My Store" \
  --description "Order #123"
```

**Initialize a direct charge:**

```bash
chapa payments direct \
  --method telebirr \
  --amount 500 \
  --currency ETB \
  --phone 0911112233
```

Supported payment methods: `telebirr`, `mpesa`, `cbebirr`, `ebirr`, `enat_bank`, `yaya`, `link`

**Verify a payment:**

```bash
chapa payments verify REF123
```

**List payments:**

```bash
chapa payments list
chapa payments list --limit 20 --status success --currency ETB
chapa payments list --from 2025-01-01 --to 2025-12-31
```

### Payouts

**Create a payout:**

```bash
chapa payouts create \
  --amount 5000 \
  --account-number 1000123456789 \
  --account-name "John Doe" \
  --bank-slug cbe \
  --currency ETB \
  --reason "Vendor payment"
```

**Verify a payout:**

```bash
chapa payouts verify REF456
```

**List payouts:**

```bash
chapa payouts list
chapa payouts list --limit 10 --status success --bank-slug cbe
```

**Bulk payouts from a JSON file:**

```bash
chapa payouts bulk --file payouts.json
```

The JSON file format:

```json
{
  "items": [
    {
      "amount": 1000,
      "account": {
        "account_number": "1000123456789",
        "account_name": "John Doe",
        "bank_slug": "cbe"
      }
    },
    {
      "amount": 2000,
      "account": {
        "account_number": "1000987654321",
        "account_name": "Jane Doe",
        "bank_slug": "awash"
      }
    }
  ],
  "currency": "ETB"
}
```

### Banks

**List supported banks:**

```bash
chapa banks list
chapa banks list --country ET
```

### Subaccounts

**Create a subaccount:**

```bash
chapa subaccounts create \
  --name "Partner Store" \
  --account-number 1000123456789 \
  --account-name "Partner Inc" \
  --bank-slug cbe \
  --currency ETB \
  --split-type percentage \
  --split-value 10
```

**List subaccounts:**

```bash
chapa subaccounts list
chapa subaccounts list --currency ETB --active
```

**Update a subaccount:**

```bash
chapa subaccounts update SUB_REF --split-value 15
chapa subaccounts update SUB_REF --account-number 1000999999999 --bank-slug awash
```

### Refunds

**Create a refund:**

```bash
chapa refunds create --payment-reference PAY_REF
chapa refunds create --payment-reference PAY_REF --amount 500 --reason "Customer request"
```

**List refunds:**

```bash
chapa refunds list
chapa refunds list --status success --limit 20
```

**Verify a refund:**

```bash
chapa refunds verify REF789
```

### Webhooks

**Listen for webhooks locally:**

```bash
chapa webhook listen /pay/chapa-webhook
chapa webhook listen /webhook --port 8080
```

This starts a local Flask server that prints incoming webhook payloads to your terminal.

**Ping a webhook URL:**

```bash
chapa webhook ping https://example.com/webhook
chapa webhook ping https://example.com/webhook --data '{"event": "test"}'
```

## JSON Mode

All commands support `--json` for script-friendly output:

```bash
chapa --json payments list --limit 5 | jq '.data.items[].status'
chapa --json payments verify REF123 > result.json
```

## Error handling

Errors are structured and include `error_code`, `error_type`, and `error_message`. In JSON mode you get a consistent shape:

```bash
chapa --json payments verify INVALID_REF
# {"status": "error", "message": "...", "details": {"error_code": "...", "error_type": "client_error", "error_message": "..."}}
```

In code, catch `ChapaError` (or `APIError` / `NetworkError` from `chapa_cli.errors`) and use `e.error_message` and `e.to_dict()` for details. Never rely on raw exceptions.

## Webhook verification

For production webhooks, verify the signature using your webhook secret:

```python
from flask import request
from chapa_cli.config import get_webhook_secret
from chapa_cli.webhook_verify import verify_webhook_signature

@app.route("/webhook", methods=["POST"])
def webhook():
    secret = get_webhook_secret()
    if not secret or not verify_webhook_signature(
        request.data,
        request.headers.get("X-Chapa-Signature", ""),
        secret,
    ):
        return {"error": "Invalid signature"}, 401
    # Process payload...
    return {"status": "received"}, 200
```

Set `CHAPA_WEBHOOK_SECRET` in your environment or store it in `~/.chapa-cli/config.json` (key: `webhook_secret`).

## Amounts

Amounts in API payloads and CLI options (e.g. `--amount`) are in **smallest currency unit** (integer), e.g. 1050 for 10.50 ETB. To convert from base unit without floating-point errors, use the provided helper:

```python
from chapa_cli.amounts import to_smallest_unit
to_smallest_unit(10.50, "ETB")  # 1050
```

## Version compatibility

- **Python**: 3.9+
- **Chapa API**: v2. Compatibility with the Chapa v2 API is maintained; check [developer.chapa.co](https://developer.chapa.co) for API changes.

## Contributing

1. Fork the repository and create a feature branch.
2. Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
3. Add tests for new behavior; run tests with `pytest` (install with `pip install -e ".[test]"`).
4. Ensure the codebase passes linting and formatting (follow project language best practices).
5. Submit a pull request; reference any related issue IDs.

## Logout

```bash
chapa logout
```

## License

MIT License. See [LICENSE](LICENSE) for details.
