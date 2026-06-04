# env-parser

A lightweight `.env` parser and environment loader built in pure Python with no third-party runtime dependencies.

This project was created as a learning challenge to understand how environment management libraries work internally before adopting production solutions such as python-dotenv.

## Features

* Parse `.env` files into typed Python dictionaries
* Automatic type conversion:

  * `True` / `False` → bool
  * integers → int
  * decimals → float
  * quoted values → str
* Preserve `#` characters inside quoted strings
* Strip inline comments from values
* Track full-line and inline comments
* Load variables into `os.environ`
* Retrieve values through a unified API
* Required key validation with automatic pipeline failure
* Basic secret detection and masking
* Pytest test suite covering common parsing edge cases
* No third-party runtime dependencies

---

## Installation

Clone the repository:

```bash
git clone <repo-url>
cd env-parser
```

Optional testing dependency:

```bash
pip install pytest
```

---

## Usage

```python
from env_parser import load_env, get, require

load_env(".env")

require(["DATABASE_URL", "API_KEY", "SECRET_KEY"])

print(get("DATABASE_URL"))
print(get("MISSING_KEY", "default"))
```

### Secret masking

```python
print(get("API_KEY"))
```

Output:

```text
abcd******
```

Explicit masking:

```python
print(get("API_KEY", masked=True))
```

---

## Supported .env Syntax

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

## Testing

Run the test suite:

```bash
pytest
```

Run a specific file:

```bash
pytest test_parser.py
```

Current test coverage includes:

* Normal values
* Empty values
* Multiple `=` characters
* Inline comment stripping
* Hash signs inside quoted strings
* Secret masking
* Sensitive key detection

---

## Implementation Notes

### inside_comment()

Detecting inline comments was the most challenging part of Phase 1.

A naive implementation using:

```python
string.find("#")
```

fails for values such as:

```env
NAME="John # Smith"
```

because the `#` belongs to the value rather than a comment.

The final implementation performs a character-by-character scan while tracking whether the parser is currently inside quotes.

When a `#` is encountered outside quotes, the parser extracts the value and comment portions immediately.

Lessons learned:

* Context matters more than character matching
* Simple state tracking often beats position bookkeeping
* `idx = None` is a safer sentinel than `idx = 0`

---

### Secret Handling

Sensitive values are identified through common environment variable naming conventions:

```text
PASSWORD
SECRET
TOKEN
API_KEY
SECRET_KEY
```

The parser masks these values when retrieved through `get()`.

Example:

```text
API_KEY=abcdefgh12345
```

becomes:

```text
abcd**********
```

This prevents accidental disclosure during debugging and logging.

---

### Validation

The `require()` function validates required environment variables before application startup.

Instead of failing on the first missing key, it collects all missing variables and reports them together before exiting.

Example:

```python
require([
    "DATABASE_URL",
    "API_KEY",
    "SECRET_KEY"
])
```

---

## Roadmap

### Completed

* [x] Parse `.env` files into dictionaries
* [x] Automatic type casting
* [x] Inline comment handling
* [x] Quoted string support
* [x] Load values into `os.environ`
* [x] Required key validation
* [x] Secret masking
* [x] Sensitive key detection
* [x] Pytest test suite

### Planned

* [ ] Write/update `.env` files
* [ ] Nested variable expansion

```env
BASE_URL=${HOST}:${PORT}
```

* [ ] Optional overwrite mode
* [ ] Export environment variables
* [ ] Improved quote escaping support
* [ ] Enhanced secret management features

---

## Learning Goals

This project is intentionally implemented from scratch as a software engineering and cybersecurity learning exercise.

Objectives:

* Understand configuration management
* Learn parser design
* Practice testing and validation
* Explore environment-based secret handling
* Compare custom implementations against professional libraries
