from typing import Optional

from flask import Flask, jsonify

ERROR_LOGIN_REQUIRED = "login_required"
ERROR_ADMIN_REQUIRED = "admin_required"
ERROR_VALIDATION_ERROR = "validation_error"


class _AOIHTTPError(Exception):
    """Base class of HTTP errors generated.

    These errors are automatically caught by an error handler and converted to
    json responses of the form:

    ```json
    {
        "error": true,
        "error_code": "<error_code>",
        "message": "<msg>"
    }
    ```
    """

    status_code = None

    def __init__(self, message: str, *, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class AOIBadRequest(_AOIHTTPError):
    """A 400 Bad Request HTTP error."""

    status_code = 400


class AOIUnauthorized(_AOIHTTPError):
    """A 401 Unauthorized HTTP error."""

    status_code = 401


class AOIForbidden(_AOIHTTPError):
    """A 403 Forbidden HTTP error."""

    status_code = 403


class AOINotFound(_AOIHTTPError):
    """A 404 Not Found HTTP error."""

    status_code = 404


class AOIConflict(_AOIHTTPError):
    """A 409 Conflict HTTP error."""

    status_code = 409


class AOIInternalServerError(_AOIHTTPError):
    """A 500 Internal Server Error HTTP error."""

    status_code = 500


def _handle_aoi_http_error(err: _AOIHTTPError):
    return (
        jsonify(
            {
                "error": True,
                "error_code": err.error_code,
                "message": err.message,
            }
        ),
        err.status_code,
    )


def init_app(app: Flask):
    app.register_error_handler(_AOIHTTPError, _handle_aoi_http_error)
