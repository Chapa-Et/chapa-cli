"""Webhook signature verification.

Verify that incoming webhook payloads are signed by Chapa using CHAPA_WEBHOOK_SECRET.
Use this in production before trusting webhook body content.
"""

import hmac
import hashlib
from typing import Optional


def verify_webhook_signature(
    payload_body: bytes,
    signature_header: str,
    secret: str,
    algorithm: str = "sha256",
) -> bool:
    """Verify the webhook signature using HMAC.

    Compares the provided signature header (e.g. X-Chapa-Signature) against
    HMAC(secret, payload_body). Use constant-time comparison to avoid timing attacks.

    Args:
        payload_body: Raw request body bytes (do not use parsed JSON).
        signature_header: Value of the signature header from the request.
        secret: Webhook secret (e.g. from CHAPA_WEBHOOK_SECRET).
        algorithm: Hash algorithm for HMAC (default sha256).

    Returns:
        True if the signature is valid, False otherwise.

    Example:
        # In a Flask route:
        secret = get_webhook_secret()
        if not secret or not verify_webhook_signature(
            request.data,
            request.headers.get("X-Chapa-Signature", ""),
            secret,
        ):
            return {"error": "Invalid signature"}, 401
    """
    if not signature_header or not secret:
        return False
    hash_fn = getattr(hashlib, algorithm, None)
    if not hash_fn:
        return False
    expected = hmac.new(
        secret.encode("utf-8"),
        payload_body,
        hash_fn,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header.strip())


def get_signature_header_value(headers: dict, header_name: Optional[str] = None) -> str:
    """Get signature from request headers. Default header: X-Chapa-Signature."""
    name = (header_name or "X-Chapa-Signature").lower()
    for k, v in headers.items():
        if k.lower() == name:
            return v if isinstance(v, str) else ""
    return ""
