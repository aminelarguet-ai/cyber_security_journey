"""
secure_logging.py — JSON structured logging with automatic sensitive-field redaction.
Module 1 deliverable: logging that is safe by default, not by developer discipline.
"""

import json
import logging
from datetime import datetime, timezone

# Case-insensitive denylist of field names to redact wherever they appear,
# at any nesting depth, in the `extra` payload.
SENSITIVE_KEYS = {
    "password", "passwd", "pwd",
    "token", "access_token", "refresh_token",
    "secret", "api_key", "apikey",
    "authorization", "auth",
    "ssn", "social_security_number",
    "credit_card", "card_number", "cvv",
    "private_key",
}

REDACTED = "REDACTED"


def redact(obj):
    """
    Recursively walk a dict/list structure and replace the value of any
    key matching SENSITIVE_KEYS (case-insensitive) with REDACTED.
    Returns a new structure; does not mutate the input.
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(k, str) and k.lower() in SENSITIVE_KEYS:
                out[k] = REDACTED
            else:
                out[k] = redact(v)
        return out
    elif isinstance(obj, list):
        return [redact(item) for item in obj]
    else:
        return obj


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Anything passed via logging.info("msg", extra={"foo": "bar"})
        # lands as attributes on the record, not in a clean dict — so we
        # only pull out what the caller explicitly namespaced under `extra_data`.
        extra_data = getattr(record, "extra_data", None)
        if extra_data is not None:
            payload["extra"] = redact(extra_data)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def get_secure_logger(name: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:  # avoid duplicate handlers on re-import
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = get_secure_logger(__name__)

logger.info("User login attempt", extra={"extra_data": {
    "user": "alice",
    "auth": {"password": "hunter2"}
}})
