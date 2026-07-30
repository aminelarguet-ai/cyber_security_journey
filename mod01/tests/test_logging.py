import json
import logging
import io
from secure_logging import JSONFormatter, redact

def test_redact_nested_password():
    data = {"user": "alice", "auth": {"password": "hunter2"}}
    result = redact(data)
    assert result["auth"]["password"] == "REDACTED"
    assert result["user"] == "alice"

def test_redact_case_insensitive():
    data = {"Password": "hunter2", "API_KEY": "sk-123"}
    result = redact(data)
    assert result["Password"] == "REDACTED"
    assert result["API_KEY"] == "REDACTED"

def test_no_secret_leaks_in_json_output():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    logger = logging.getLogger("test_leak")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)

    logger.info("login", extra={"extra_data": {"auth": {"password": "hunter2"}}})

    output = stream.getvalue()
    parsed = json.loads(output)
    assert "hunter2" not in output
    assert parsed["extra"]["auth"]["password"] == "REDACTED"