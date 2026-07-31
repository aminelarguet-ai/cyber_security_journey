
# env-parser 🐍

A lightweight `.env` file parser and tooling for safe configuration and logging — a mix of pure-Python parsers and a dotenv-backed parser for convenience. I built this as a learning project to understand configuration management, safe handling of secrets, and production-grade logging.

## What's inside?

| File | What it does | Best for |
|------|-------------|----------|
| `main.py` | Simple functional API: `load_env`, `get`, `require`, `write_env` | Quick scripts, beginners |
| `env_parser.py` | OOP: `Parser`, `EnvStore`, `EnvFile` (pure Python implementation) | Bigger projects, OOP practice, no external deps |
| `dotenv_parser.py` | Parser + writer using `python-dotenv` (`dotenv_values`, `set_key`) | `.env` standard compatibility / `python-dotenv` |
| `secure_logging.py` | JSON logs that auto-hide secrets (deep redaction) | Production / learning logging |
| `logger.py` | Basic file logging (naive) | Seeing the "before" version |

## Why two parser styles?

- **`env_parser.py`**: pure-Python implementation with no third-party dependencies. Good for learning and when you want total control.
- **`dotenv_parser.py`**: uses `python-dotenv` for parsing and writing. Good for interoperability and when you want to rely on a well-tested library.

## Quick Start

### Install (recommended)

```bash
pip install python-dotenv pytest bandit pip-audit
```

### The simple way (functions in `main.py`)

```python
from main import load_env, get, require
from secure_logging import get_secure_logger
```

**1. Load your `.env` file into the environment**

```python
load_env(".env")
```

**2. Make sure the important stuff is there**

```python
require(["DATABASE_URL", "API_KEY", "SECRET_KEY"])
```

**3. Grab values when you need them**

```python
print(get("DATABASE_URL"))          # normal value
print(get("API_KEY"))               # auto-masked (shows abcd****)
print(get("PORT", default="8080"))  # fallback if not set
```

**4. Log stuff safely — secrets get hidden automatically!**

```python
logger = get_secure_logger(name)
logger.info(
    "Database connected",
    extra={
        "extra_data": {
            "host": get("DATABASE_URL"),
            "api_key": get("API_KEY")  # shows as REDACTED in logs
        }
    }
)
```

## Using the dotenv-backed parser (`dotenv_parser.py`)

The `dotenv_parser` module uses `python-dotenv` for parsing (`.env` compatibility) and `set_key` for writing.

```python
from dotenv_parser import read_and_parse, write_env
from secure_logging import get_secure_logger

logger = get_secure_logger(name)
```

### Read and parse

Returns a data dictionary and a comments dictionary:

```python
data, comments = read_and_parse(".env")
```

### Use values

Values are converted to `bool`, `int`, `float`, or `str` when possible:

```python
logger.info("Config loaded", extra={"extra_data": {"keys": len(data)}})
```

### Write a dict back to a `.env` file

Uses `python-dotenv`'s `set_key`:

```python
write_env(".env.backup", data, overwrite=False)
```

## What syntax is supported?

```bash
# This is a full-line comment — it's saved separately
DEBUG=False
PORT=5432
DATABASE_URL=postgres://localhost/db

# Only the FIRST = is the delimiter — the rest are part of the value
TOKEN=abc=123=xyz

# Inline comments get stripped from the value (unless inside quotes)
API_KEY=secret123 # production key

# But # inside quotes is kept as-is!
NAME="John # Smith"

# Empty values are allowed
EMPTY=

# You can reference other variables with ${VAR}
BASE_URL=https://example.com
API_URL=${BASE_URL}/api/v1
```

## Important: parsing and expansion order

### Type conversion order

This applies when values are converted automatically:

1. Empty string → `""`
2. `"true"` / `"false"` (case-insensitive) → `bool`
3. Quoted strings (`'...'` or `"..."`) → `str` (quotes stripped)
4. Integers → `int`
5. Floats → `float`
6. Everything else → `str`

### Why this order matters

- If you convert numbers before handling quoted strings, `"001"` or quoted numeric-looking values could be converted unexpectedly.
- Booleans are recognized before numeric conversion so values like `"false"` won't become strings or numbers by mistake.
- Variable expansion (`${VAR}`) is applied after initial conversion in these modules. Circular references are detected and expansion stops to avoid infinite loops.
- When you write custom parsing logic or change the converter, keep this order in mind: it preserves expected behavior (e.g., quoted strings remain strings; boolean literals become booleans).

## API Cheatsheet

### `main.py` — Functions

| Function | What it does |
|----------|-------------|
| `load_env(path)` | Reads `.env` and loads everything into `os.environ` |
| `read_and_parse(path)` | Reads `.env` and returns `(data_dict, comments_dict)` without touching `os.environ` |
| `get(key, default=None, masked=False)` | Gets a value. Auto-masks secrets by key name when appropriate. |
| `require(["KEY1", "KEY2"])` | Checks keys exist. If any are missing, prints what's missing and exits. |
| `write_env(path, data, overwrite=False)` | Saves a dict back to `.env` format. Won't overwrite unless you say so! |
| `expand(data)` | Replaces `${VAR}` with actual values. Detects circular references so it won't loop forever. |

### `env_parser.py` — Classes (pure-Python)

| Class | What it does |
|-------|-------------|
| `Parser()` | Turns lines of text into a clean dictionary (handles inline comments, quoting, expansion) |
| `EnvStore()` | Holds the data and gives you `get()` / `require()` with masking |
| `EnvFile(path)` | Reads/writes the actual file on disk (pure-Python writer) |

### `dotenv_parser.py` — dotenv-backed parser

- Uses `python-dotenv`'s `dotenv_values(file_path, interpolate=False)` to read values.
  - Note: `interpolate` is disabled at read time to allow our controlled expansion step (we perform explicit expansion to detect circular refs).
- Uses `set_key` from `python-dotenv` to write values reliably to a `.env` file.
- Ideal when you want `python-dotenv` compatibility and a simpler writing API.

### `secure_logging.py` — Safe Logging

```python
from secure_logging import get_secure_logger

logger = get_secure_logger("myapp")

# Simple message
logger.info("Server started")

# Message with extra info
logger.warning(
    "Slow query",
    extra={
        "extra_data": {
            "query_time_ms": 1234,
            "table": "users"
        }
    }
)

# If something breaks, include the traceback
logger.error("Auth failed", exc_info=True)
```

**What the log looks like (JSON):**

```json
{
  "timestamp": "2026-07-30T14:47:21.123456+00:00",
  "level": "INFO",
  "logger": "myapp",
  "message": "Server started",
  "module": "app",
  "line": 42,
  "extra": {
    "user": "alice",
    "password": "REDACTED"
  }
}
```

## Secret Masking — How it works

### When you `get()` a value

If the key name contains words in the sensitive set (`password`, `secret`, `key`, `token`, `api`), the value gets masked automatically:

- Values longer than 4 chars: shows first 4, then `*` (e.g. `abcd******`)
- Values 4 chars or less: fully masked (e.g. `****`)

### When you log something

The logger scans every field name in your `extra_data`. If it matches a sensitive name, the value becomes `"REDACTED"` — even if it's nested.

## Security

### Static analysis

The code is scanned with Bandit:

```bash
pip install bandit
bandit -r .
```

### Dependency scanning

`pip-audit` is available to find vulnerable dependencies:

```bash
pip install pip-audit
pip-audit
```

## CI pipeline — what changed and why order matters

CI now runs a set of automated checks on every push and PR. The pipeline includes (in the order chosen to fail-fast and keep feedback loops short):

1. **Unit tests** — `pytest` (quick functional checks)
2. **Dependency audit** — `pip-audit` (fail early on vulnerable dependencies)
3. **SAST scan** — `bandit` (deep static analysis; runs after deps check)
4. **Optional additional checks**: linters, pre-commit checks (`gitleaks` for secrets), packaging checks

### Why the change?

Moving dependency audit earlier causes the pipeline to fail fast when there are known vulnerable packages, saving the time of running longer SAST/lint checks on code that should not be merged until dependencies are fixed.

The order of checks in CI is intentional: quick correctness checks (tests) first → fail-fast security checks (dependency audit) → deeper SAST and policy checks.

> **Note:** For your own projects, tune ordering to your priorities (fast feedback vs. security depth).

## Testing

You'll need `pytest`:

```bash
pip install pytest
```

Run everything:

```bash
pytest
```

Run specific files:

```bash
pytest test_parser.py   # parsing, masking, expansion, file I/O
pytest test_logging.py  # JSON logs, redaction, nested data
```

### What's tested?

| Area | Covered? |
|------|----------|
| Normal values, empty values, multiple `=` signs | ✅ |
| Inline comments, quoted `#`, full-line comments | ✅ |
| `bool`, `int`, `float`, `str` conversion | ✅ |
| Masking short/long values, key name detection | ✅ |
| Writing files, overwrite protection | ✅ |
| Expansion: single, nested, missing vars, circular refs | ✅ |
| JSON format, nested redaction, case-insensitive matching | ✅ |

## Security (developer notes)

- **No secrets in source code** — designed to keep them in `.env` files
- **Auto-masking** — secrets get hidden without you doing anything
- **Circular reference protection** — expansion can't infinite-loop
- **Overwrite protection** — writer functions will not overwrite files unless explicitly allowed
- **Deep redaction** — sensitive fields hidden at any nesting depth in logs
- **Pre-commit hooks** — `gitleaks` scans for secrets before commit
- **CI pipeline** — automated tests + dependency & security scans on every push

## Exporting back to `.env`

Got a dictionary and want to save it as a `.env` file?

```python
from dotenv_parser import write_env

data = {"HOST": "localhost", "PORT": 5432, "DEBUG": False}
write_env(".env.backup", data)
```

**Result:**

```bash
HOST=localhost
PORT=5432
DEBUG=False
```

By default, `write_env` will not overwrite an existing file. Pass `overwrite=True` if you mean it.

## Installation (repo)

```bash
git clone <repo>
cd mod01
```

Optional but recommended:

```bash
pip install pytest        # for testing
pip install bandit        # for security scanning
pip install python-dotenv # required by dotenv_parser
pip install pip-audit
```

## Notes for contributors

- If you modify parsing code, keep the **Type Conversion Order** and expansion behavior consistent, otherwise tests and user expectations can break.
- If you change CI order, consider the trade-offs: moving dependency checks earlier gives faster security feedback; moving SAST earlier may catch code smells earlier but costs time.
- Tests exist for both `env_parser.py` (pure-Python) and `dotenv_parser.py` (dotenv-backed). Run tests after any change.

## Finally

This is a test I ran locally and its result:

```
Detect hardcoded secrets.................................................Failed
- hook id: gitleaks
- exit code: 1

○
    │╲
    │ ○
    ○ ░
    ░    gitleaks

Finding:     ...S_SECRET_ACCESS_KEY=REDACTED67890
Secret:      REDACTED
RuleID:      aws-access-token
Entropy:     3.584184
File:        mod01/scratch_secret.txt
Line:        1
Fingerprint: mod01/scratch_secret.txt:aws-access-token:1

10:18PM INF 1 commits scanned.
10:18PM INF scan completed in 7.44ms
10:18PM WRN leaks found: 1
```

