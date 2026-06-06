# env-parser

A lightweight `.env` file parser, environment loader, and exporter written in pure Python — no third-party runtime dependencies required.

Built as a learning exercise to understand how environment configuration and secret handling work under the hood, before reaching for production tools like `python-dotenv`.

-----

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported Syntax](#supported-env-syntax)
- [API Reference](#api-reference)
- [Secret Masking](#secret-masking)
- [Exporting Data](#exporting-environment-data)
- [Testing](#testing)
- [Security](#security)
- [How It Works](#how-it-works)

-----

## Features

- Parse `.env` files into typed Python dictionaries
- Automatic type conversion:
  - `true` / `false` → `bool`
  - whole numbers → `int`
  - decimal numbers → `float`
  - quoted strings → `str` (quotes stripped)
- Handle `#` characters safely inside quoted strings
- Strip inline comments without breaking values
- Track full-line and inline comments separately
- Variable expansion with `${VAR}` syntax
- Circular reference detection during expansion
- Load variables directly into `os.environ`
- Simple `get()` API with default value support
- Required key validation with full error reporting before exit
- Automatic secret detection and masking by key name
- Export environment data back to `.env` files
- Overwrite protection on file writes
- No external runtime dependencies

-----

## Installation

```bash
git clone <repo-url>
cd env-parser
```

Optional — install test runner:

```bash
pip install pytest
```

Optional — install static security scanner:

```bash
pip install bandit
```

-----

## Quick Start

```python
from main import load_env, get, require

# 1. Load a .env file into os.environ
load_env(".env")

# 2. Validate that required keys are present (exits on failure)
require(["DATABASE_URL", "API_KEY", "SECRET_KEY"])

# 3. Retrieve values
print(get("DATABASE_URL"))         # plain retrieval
print(get("API_KEY"))              # auto-masked (sensitive key name)
print(get("PORT", default="8080")) # with fallback default
print(get("SOME_VAR", masked=True))# force masking regardless of key name
```

-----

## Supported `.env` Syntax

```env
# Full-line comments are preserved separately

DEBUG=False
PORT=5432
DATABASE_URL=postgres://localhost/db

# Multiple = signs: only the first is treated as the delimiter
TOKEN=abc=123=xyz

# Inline comments are stripped from the value
API_KEY=secret123  # production key

# # inside quoted strings is preserved as-is
NAME="John # Smith"

# Empty values are recorded with a descriptive message
EMPTY=

# Variable expansion using ${VAR} syntax
BASE_URL=https://example.com
API_URL=${BASE_URL}/api/v1
```

-----

## API Reference

### `load_env(file_path)`

Parses a `.env` file and loads all key-value pairs into `os.environ`. Exits with an error message if the file is missing or empty.

```python
load_env(".env")
```

-----

### `read_and_parse(file_path)`

Parses a `.env` file and returns a `(data, comments)` tuple without modifying `os.environ`.

- `data` — dict of parsed key-value pairs with automatic type conversion
- `comments` — dict of full-line and inline comments keyed by line number

```python
data, comments = read_and_parse(".env")
print(data["PORT"])     # 5432 (int)
print(data["DEBUG"])    # False (bool)
```

Returns `None` if the file does not exist.

-----

### `get(key, default=None, masked=False)`

Retrieves a value from `os.environ`.

- Returns `default` if the key is not set
- Automatically masks values whose key names contain sensitive substrings
- Set `masked=True` to force masking on any key

```python
get("PORT")                    # "5432"
get("API_KEY")                 # "abcd******"  (auto-masked)
get("HOST", default="localhost")
get("INTERNAL_URL", masked=True)
```

-----

### `require(key_list)`

Validates that every key in `key_list` is present in `os.environ`. Prints all missing keys at once, then calls `sys.exit(1)`.

```python
require(["DATABASE_URL", "SECRET_KEY", "API_KEY"])
# Prints all missing keys before exiting — no hunt-and-fix loop
```

-----

### `write_env(file_path, data, overwrite=False)`

Writes a dictionary of key-value pairs to a `.env`-formatted file.

- Returns `True` on success
- Returns `None` (without raising) if the file exists and `overwrite=False`

```python
data = {"PORT": 5432, "DEBUG": False}
write_env(".env.backup", data)             # safe default
write_env(".env.backup", data, overwrite=True)  # force overwrite
```

-----

### `expand(data)`

Resolves `${VAR}` references within a parsed data dictionary. Handles deep nesting and detects circular references without looping forever.

```python
data = {
    "HOST": "localhost",
    "PORT": "8080",
    "URL": "http://${HOST}:${PORT}/api"
}
expand(data)
# data["URL"] → "http://localhost:8080/api"
```

- Unresolvable references are left as-is: `${MISSING}` stays `${MISSING}`
- Circular references print a warning and stop expanding that key

-----

## Secret Masking

Keys whose names contain any of the following substrings (split on `_`) are automatically masked:

```
password  secret  key  token  api
```

The first 4 characters of the value are shown; the rest are replaced with `*`. Values 4 characters or shorter are fully masked.

```python
get("API_KEY")       # "abcd******"
get("SECRET")        # "****"
get("DATABASE_URL")  # "postgres://localhost/db"  (not masked)
```

The check splits on `_` to avoid false positives — for example, `MONKEY` is not flagged because `monkey` split on `_` does not equal `key`.

-----

## Exporting Environment Data

Convert any dictionary back to `.env` format:

```python
from main import write_env

data = {"HOST": "localhost", "PORT": 5432, "DEBUG": False}
result = write_env(".env.export", data)

if result is None:
    print("File already exists. Pass overwrite=True to replace it.")
```

Output file:

```env
HOST=localhost
PORT=5432
DEBUG=False
```

-----

## Testing

Run the full test suite:

```bash
pytest
```

Run a specific file:

```bash
pytest test_parser.py
```

### Test coverage

|Area     |What’s tested                                                                   |
|---------|--------------------------------------------------------------------------------|
|Parsing  |Normal values, empty values, multiple `=` signs                                 |
|Comments |Inline stripping, quoted `#` preservation                                       |
|Types    |`bool`, `int`, `float`, `str` conversion                                        |
|Masking  |Short values, long values, key sensitivity detection                            |
|Writing  |Successful write, correct content, overwrite protection                         |
|Expansion|Single reference, deep nesting, multiple references, missing vars, circular refs|

-----

## Security

The codebase is periodically scanned with [Bandit](https://bandit.readthedocs.io/), a static security analysis tool for Python.

```bash
bandit -r .
```

Current status: **✅ Clean** — no issues detected in the current codebase.

-----

## How It Works

### Processing pipeline

```
.env file → read_and_parse → expand → load → os.environ
                                              ↓
                                           get / require
```

### Comment parsing

Inline comments are handled with a single-pass character scanner that tracks whether the cursor is currently inside a quoted string. This ensures:

```env
NAME="John # Smith"   →  value: John # Smith  (# not treated as comment)
API_KEY=secret123 # note  →  value: secret123, comment: note
```

### Type conversion order

Values are converted in this priority order:

1. Empty string → `""`
1. `"true"` / `"false"` (case-insensitive) → `bool`
1. Quoted string (`"..."` or `'...'`) → inner `str` with quotes stripped
1. Valid integer → `int`
1. Valid float → `float`
1. Anything else → `str`

### Variable expansion

The `expand()` function resolves `${VAR}` references iteratively per key. It tracks previously seen states to detect circular references and break out safely, so `A → ${B} → ${A}` will not loop.

### Overwrite protection

`write_env()` checks for file existence before writing. If the file exists and `overwrite=False`, it returns `None` silently instead of raising an exception — making it safe to call unconditionally in scripts.