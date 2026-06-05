# env-parser

A lightweight `.env` parser, environment loader, and exporter built in pure Python with no third-party runtime dependencies.

This project was created as a learning exercise to understand how environment configuration systems and secret handling work internally before using production tools such as `python-dotenv`.

---

## Features

* Parse `.env` files into typed Python dictionaries
* Automatic type conversion:
  * `True` / `False` → `bool`
  * integers → `int`
  * floats → `float`
  * quoted values → `str` (with quotes stripped)
* Preserve `#` inside quoted strings
* Strip inline comments safely
* Track full-line comments and inline comments separately
* Load variables into `os.environ`
* Unified `get()` API for environment access
* Required key validation with full error reporting
* Secret detection and optional masking
* Export environment data back to `.env` files
* Safe file writing with overwrite protection
* Pytest test suite covering parsing edge cases
* Static security scan validated with Bandit (clean report)
* No external runtime dependencies

---

## Installation

```bash
git clone <repo-url>
cd env-parser
```

Optional testing dependency:

```bash
pip install pytest
```

Optional security check:

```bash
pip install bandit
```

Run security scan:

```bash
bandit -r .
```

---

## Usage

```python
from main import load_env, get, require

# Load a .env file into os.environ
load_env(".env")

# Validate required keys exist
require(["DATABASE_URL", "API_KEY", "SECRET_KEY"])

# Retrieve a value
print(get("DATABASE_URL"))

# Retrieve a sensitive value (auto-masked based on key name)
print(get("API_KEY"))

# Force masking regardless of key name
print(get("SOME_VAR", masked=True))
```

---

## Exporting environment data

You can write parsed or modified environment data back to a file:

```python
from main import write_env

data = {"PORT": 5432, "DEBUG": False}
write_env(".env.backup", data, overwrite=False)
```

### Overwrite protection

If the file already exists and `overwrite=False`, the function prints a message and returns `None` instead of raising an exception:

```python
result = write_env(".env", data, overwrite=False)
if result is None:
    print("File already exists, skipping.")
```

---

## Secret masking

Keys containing sensitive substrings (`password`, `secret`, `key`, `token`, `api`) are automatically masked. The first 4 characters are preserved; the rest are replaced with `*`.

```python
print(get("API_KEY"))
# Output: abcd******
```

Explicit masking can also be forced:

```python
print(get("SOME_VAR", masked=True))
```

---

## Supported `.env` syntax

```env
# full line comment

DEBUG=False
PORT=5432

DATABASE_URL=postgres://localhost/db

TOKEN=abc=123=xyz

API_KEY=secret123 # production key

NAME="John # Smith"

EMPTY=
```

---

## API Reference

### `read_and_parse(file_path)`
Reads a `.env` file and returns a tuple of `(data, comments)`.
- `data`: dict of parsed key-value pairs with automatic type conversion
- `comments`: dict tracking full-line and inline comments

### `load_env(file_path)`
Parses a `.env` file and loads all variables into `os.environ`.

### `get(key, default=None, masked=False)`
Retrieves a value from `os.environ`. Returns `default` if the key is not found. Automatically masks values for sensitive keys; set `masked=True` to force masking.

### `require(key_list)`
Validates that all keys in `key_list` exist in `os.environ`. Prints missing keys and calls `sys.exit(1)` if any are missing.

### `write_env(file_path, data, overwrite=False)`
Writes a dictionary of key-value pairs to a `.env` file. Returns `True` on success, `None` if the file exists and `overwrite=False`.

---

## Testing

Run all tests:

```bash
pytest
```

Run specific file:

```bash
pytest test_parser.py
```

### Test coverage

* Normal key/value parsing
* Empty values
* Multiple `=` handling
* Inline comment stripping
* Quotes with `#` inside
* Type conversion (`bool`, `int`, `float`, `str`)
* Secret masking
* Sensitive key detection
* File write with and without overwrite protection

---

## Security

This project is periodically scanned using:

* Bandit (static security analysis)

Current status:

> ✅ Clean report (no known security issues detected in current codebase)

---

## Implementation Notes

### Comment parsing strategy

Inline comments are handled using a single-pass parser that tracks whether the cursor is inside quotes.

This ensures that:

```env
NAME="John # Smith"
```

does not incorrectly treat `# Smith` as a comment.

### Type conversion

Values are converted in the following order:
1. Empty string → `""`
2. `"true"` / `"false"` (case-insensitive) → `bool`
3. Quoted strings (`"..."` or `'...'`) → inner string
4. Valid integers → `int`
5. Valid floats → `float`
6. Everything else → `str`

### Write system

The exporter converts dictionary data into `.env` format:

```python
KEY=value
```

It supports safe file creation with overwrite protection:

```python
if file_check(file_path) and not overwrite:
    print(f"this file {file_path} already exists")
    return None
```

### Design philosophy

This project follows a simple processing pipeline:

```
Parse → Validate → Load → Mask → Export
```