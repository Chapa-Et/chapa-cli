# Chapa CLI – Agent & LLM usage

This file defines safe usage patterns, expected inputs, and error handling for agents and LLMs integrating with Chapa CLI or the underlying API client.

## Safe usage patterns

- **Authentication**: Use `CHAPA_PRIVATE_KEY` or `CHAPA_SECRET_KEY` for the API key. Never log or expose the key.
- **Webhooks**: Use `CHAPA_WEBHOOK_SECRET` for signature verification. Always verify webhook signatures before processing (see `chapa_cli.webhook_verify.verify_webhook_signature`).
- **Amounts**: Use **smallest currency unit** (integer) in API payloads (e.g. 1050 for 10.50 ETB). For base-unit input, use `chapa_cli.amounts.to_smallest_unit(amount, currency)` to avoid floating-point errors.
- **Idempotency**: Create/refund/verify operations may be retried; use stable `merchant_reference` values where the API supports them to aid idempotency.

## Expected inputs

- **Payments**: `amount` (int, smallest unit), `currency` (e.g. ETB), `customer` (phone_number, email, etc.), optional `callback_url`, `return_url`, `merchant_reference`.
- **Payouts**: `amount` (int), `account` (account_number, account_name, bank_slug) or `account_reference`, optional `currency`, `merchant_reference`, `reason`.
- **Refunds**: `payment_reference` (required), optional `amount` (smallest unit), `reason`, `merchant_reference`.
- **Subaccounts**: `subaccount_name`, `account`, `currency`, `split_type`, `split_value`; optional `min_amount`, `max_amount`, `is_primary`.

## Known constraints

- **Rate limits**: Respect API rate limits; the client retries transient network/5xx errors up to a configured number of times.
- **Timeouts**: Default request timeout is 30s; configurable on `ChapaClient(timeout=..., max_retries=...)`.
- **Configuration**: Config is centralized in `chapa_cli.config`. Env var names are overridable (e.g. `get_secret_key(env_var_name="MY_KEY")`).

## Error handling

- All errors are **typed**: `ChapaError` subclasses (`APIError`, `NetworkError`). Never rely on raw exceptions.
- Every error has: `error_code`, `error_type`, `error_message`; optional `details`. Use `e.to_dict()` for a structured result.
- **APIError**: 4xx (client_error) or 5xx (server_error); may include `status_code` and `body` in details.
- **NetworkError**: timeout, connection_failed, retry_exhaustion. Retry with backoff or surface to the user.
- Do not leak internal implementation details in user-facing messages.

## Deterministic outputs

- Use `--json` for script-friendly, parseable output.
- Response structure is stable: success responses include `status`, `message`, and often `data`; list endpoints include `data` (or `data.items`) and optional `pagination`.

## References

- Config: `chapa_cli.config` (env: `CHAPA_PRIVATE_KEY`, `CHAPA_SECRET_KEY`, `CHAPA_WEBHOOK_SECRET`, `CHAPA_BASE_URL`).
- Amounts: `chapa_cli.amounts.to_smallest_unit`, `from_smallest_unit`.
- Webhook verification: `chapa_cli.webhook_verify.verify_webhook_signature`.
- Errors: `chapa_cli.errors.ChapaError`, `APIError`, `NetworkError`.
