"""
secure_logging.py — JSON structured logging with automatic sensitive-field redaction.

Module 1 deliverable:
Logging that is safe by default, not dependent on developer discipline.
"""

import json
import logging
from datetime import datetime, timezone


REDACTED = "REDACTED"

_SECRET_PATTERNS = (
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "ssn",
    "social_security_number",
    "credit_card",
    "card_number",
    "cvv",
    "private_key",
    "privatekey",
)


def _is_secret_key(key: str) -> bool:
    """
    Check whether a dictionary key contains sensitive information.
    Matching is case-insensitive.
    """
    if not isinstance(key, str):
        return False

    normalized = key.lower()

    return any(
        pattern in normalized
        for pattern in _SECRET_PATTERNS
    )


def redact(obj):
    """
    Recursively redact sensitive values in dictionaries/lists/tuples.

    Returns a new structure.
    Original object is not modified.
    """

    if isinstance(obj, dict):
        output = {}

        for key, value in obj.items():
            if _is_secret_key(key):
                # If the secret key holds a nested mapping/sequence, redact inside it
                # instead of replacing the whole structure with the REDACTED string.
                if isinstance(value, (dict, list, tuple)):
                    output[key] = redact(value)
                else:
                    output[key] = REDACTED
            else:
                output[key] = redact(value)

        return output

    elif isinstance(obj, (list, tuple)):
        return [
            redact(item)
            for item in obj
        ]

    else:
        return obj


class JSONFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:

        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                timezone.utc
            ).isoformat(),

            "level": record.levelname,

            "logger": record.name,

            "message": record.getMessage(),

            "module": record.module,

            "line": record.lineno,
        }

        extra_data = getattr(
            record,
            "extra_data",
            None
        )

        if extra_data is not None:

            # Handle JSON stored as string
            if isinstance(extra_data, str):

                try:
                    extra_data = json.loads(extra_data)

                except json.JSONDecodeError:
                    extra_data = {
                        "value": extra_data
                    }

            payload["extra"] = redact(extra_data)

        if record.exc_info:

            payload["exception"] = (
                self.formatException(record.exc_info)
            )

        return json.dumps(
            payload,
            default=str
        )


def get_secure_logger(
    name: str,
    level=logging.INFO
) -> logging.Logger:

    logger = logging.getLogger(name)

    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.handlers:

        handler = logging.StreamHandler()

        handler.setFormatter(
            JSONFormatter()
        )

        logger.addHandler(handler)

        logger.propagate = False

    return logger


logger = get_secure_logger(__name__)


if __name__ == "__main__":

    logger.info(                                  
        "User login attempt",
        extra={
            "extra_data": {
                "user": "alice",
                "auth": {
                    "password": "hunter2" #nosec
                },
                "metadata": {
                    "ip": "127.0.0.1"
                }
            }
        }
    )

    try:
        1 / 0
    except Exception:
        logger.exception(
            "Application error",
            extra={
                "extra_data": {
                    "api_key": "123456"
                }
            }
        )
