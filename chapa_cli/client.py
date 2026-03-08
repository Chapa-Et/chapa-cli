"""HTTP client for the Chapa v2 API.

Handles network errors (DNS, timeouts, connection drops, retry exhaustion)
and API errors (4xx, 5xx, malformed responses) via structured exceptions.
"""

from typing import Any, Dict, Optional

import requests

from chapa_cli.config import get_base_url, require_secret_key
from chapa_cli.errors import (
    APIError,
    api_error_from_response,
    network_error_from_exception,
)

API_VERSION = "/v2"
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 2


class ChapaClient:
    """Thin wrapper around the Chapa v2 REST API.

    All public methods take at most two arguments (payload/params and optional
    reference). Network and API errors are raised as structured ChapaError
    subclasses (NetworkError, APIError) with error_code, error_type,
    error_message. Raw exceptions are never thrown.
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRIES,
    ):
        """Initialize the client with base URL and secret key from config.

        Args:
            timeout: Request timeout in seconds.
            max_retries: Number of retries for connection/5xx before raising.

        Raises:
            SystemExit: If secret key is not configured (via require_secret_key).
        """
        self.base_url = get_base_url()
        self.secret_key = require_secret_key()
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _url(self, path: str) -> str:
        return f"{self.base_url}{API_VERSION}{path}"

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                return self.session.request(method, url, **kwargs)
            except requests.RequestException as e:
                last_exc = e
                if attempt == self.max_retries:
                    raise network_error_from_exception(e) from e
                continue
        if last_exc:
            raise network_error_from_exception(last_exc) from last_exc
        raise network_error_from_exception(RuntimeError("Unexpected request loop"))

    def _handle(self, resp: requests.Response) -> Dict[str, Any]:
        """Parse response body and raise APIError on 4xx/5xx. Returns JSON body as dict."""
        try:
            body = resp.json()
        except ValueError:
            body = resp.text

        if resp.status_code >= 400:
            raise api_error_from_response(resp.status_code, body)
        return body if isinstance(body, dict) else {"data": body}

    # ── Payments ─────────────────────────────────────────────

    def initialize_payment(self, payload: dict) -> dict:
        """Initialize a hosted checkout. Args: payload (amount, currency, etc.). Returns: API response. Raises: NetworkError, APIError."""
        return self._handle(self._request("POST", self._url("/payments/hosted"), json=payload))

    def verify_payment(self, reference: str) -> dict:
        """Verify a payment by reference. Raises: NetworkError, APIError."""
        return self._handle(self._request("GET", self._url(f"/payments/{reference}/verify")))

    def list_payments(self, params: dict) -> dict:
        """List payments with optional filters. Raises: NetworkError, APIError."""
        return self._handle(self._request("GET", self._url("/payments"), params=params))

    def direct_charge(self, payload: dict) -> dict:
        """Create a direct charge. Raises: NetworkError, APIError."""
        return self._handle(self._request("POST", self._url("/payments/direct"), json=payload))

    # ── Payouts ──────────────────────────────────────────────

    def create_payout(self, payload: dict) -> dict:
        return self._handle(self._request("POST", self._url("/payouts"), json=payload))

    def verify_payout(self, reference: str) -> dict:
        return self._handle(self._request("GET", self._url(f"/payouts/{reference}/verify")))

    def list_payouts(self, params: dict) -> dict:
        return self._handle(self._request("GET", self._url("/payouts"), params=params))

    def bulk_payout(self, payload: dict) -> dict:
        return self._handle(self._request("POST", self._url("/payouts/bulk"), json=payload))

    def get_banks(self, params: dict) -> dict:
        return self._handle(self._request("GET", self._url("/payouts/banks"), params=params))

    # ── Subaccounts ──────────────────────────────────────────

    def create_subaccount(self, payload: dict) -> dict:
        return self._handle(self._request("POST", self._url("/subaccounts"), json=payload))

    def list_subaccounts(self, params: dict) -> dict:
        return self._handle(self._request("GET", self._url("/subaccounts"), params=params))

    def update_subaccount(self, reference: str, payload: dict) -> dict:
        return self._handle(self._request("PUT", self._url(f"/subaccounts/{reference}"), json=payload))

    # ── Refunds ──────────────────────────────────────────────

    def create_refund(self, payload: dict) -> dict:
        return self._handle(self._request("POST", self._url("/refunds"), json=payload))

    def list_refunds(self, params: dict) -> dict:
        return self._handle(self._request("GET", self._url("/refunds"), params=params))

    def verify_refund(self, reference: str) -> dict:
        return self._handle(self._request("GET", self._url(f"/refunds/{reference}/verify")))


__all__ = ["ChapaClient", "APIError", "API_VERSION", "DEFAULT_TIMEOUT", "DEFAULT_RETRIES"]
