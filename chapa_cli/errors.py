"""Structured error types for the Chapa CLI/SDK.

All errors include error_code, error_type, and error_message per SDK standards.
Never raise raw exceptions; use these typed error classes.
"""

from typing import Any, Dict, Optional


class ChapaError(Exception):
    """Base exception for all Chapa SDK/CLI errors.

    All errors returned or thrown include:
    - error_code: Machine-readable code (e.g. API code or internal code).
    - error_type: Category (e.g. network_error, api_error).
    - error_message: Human-readable description.

    Never leak internal implementation details in error_message.
    """

    def __init__(
        self,
        error_code: str,
        error_type: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.error_type = error_type
        self.error_message = error_message
        self.details = details or {}
        super().__init__(error_message)

    def to_dict(self) -> Dict[str, Any]:
        """Return a strictly typed result structure for API/CLI consumers."""
        out: Dict[str, Any] = {
            "error_code": self.error_code,
            "error_type": self.error_type,
            "error_message": self.error_message,
        }
        if self.details:
            out["details"] = self.details
        return out


class NetworkError(ChapaError):
    """Raised when a network-level failure occurs (DNS, timeout, connection, retry exhaustion)."""

    def __init__(
        self,
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            error_type="network_error",
            error_message=error_message,
            details=details,
        )


class APIError(ChapaError):
    """Raised when the Chapa API returns 4xx/5xx or a malformed response.

    Attributes:
        status_code: HTTP status code (if available).
        body: Raw response body (dict or str) for debugging; not exposed in error_message.
    """

    def __init__(
        self,
        error_code: str,
        error_type: str,
        error_message: str,
        status_code: Optional[int] = None,
        body: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.body = body
        d = dict(details) if details else {}
        if status_code is not None:
            d["status_code"] = status_code
        super().__init__(
            error_code=error_code,
            error_type=error_type,
            error_message=error_message,
            details=d,
        )


def api_error_from_response(status_code: int, body: Any) -> APIError:
    """Build an APIError from an API response with error_code, error_type, error_message."""
    error_type = "client_error" if 400 <= status_code < 500 else "server_error"
    error_code = "unknown"
    error_message = "An error occurred"

    if isinstance(body, dict):
        error_code = str(body.get("error_code", body.get("code", "unknown")))
        error_message = str(
            body.get("error_message")
            or body.get("message")
            or body.get("error")
            or error_message
        )
        if body.get("error_type"):
            error_type = str(body["error_type"])
    else:
        error_type = "malformed_response"
        error_code = "malformed_response"
        error_message = str(body) if body else "Empty or non-JSON response"

    return APIError(
        error_code=error_code,
        error_type=error_type,
        error_message=error_message,
        status_code=status_code,
        body=body,
    )


def network_error_from_exception(exc: Exception) -> NetworkError:
    """Map a requests (or similar) exception to a structured NetworkError."""
    msg = str(exc) or type(exc).__name__
    code = "network_error"
    if "timeout" in msg.lower() or "timed out" in msg.lower():
        code = "timeout"
    elif "connection" in msg.lower() or "dns" in msg.lower() or "name resolution" in msg.lower():
        code = "connection_failed"
    elif "retry" in msg.lower() or "max retries" in msg.lower():
        code = "retry_exhaustion"
    return NetworkError(
        error_code=code,
        error_message=msg,
        details={"cause": type(exc).__name__},
    )
