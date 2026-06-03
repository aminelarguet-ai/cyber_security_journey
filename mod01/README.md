# env-parser

A lightweight `.env` file parser with secret management, built in pure Python (no dependencies).

## Features

- Parses `.env` files into typed Python dictionaries
- Automatic type casting (bool, int, float, str)
- Handles quoted string values
- Strips inline comments from values
- Tracks full-line and inline comments with line numbers
- Loads variables into os.environ
- Required key validation with automatic pipeline failure
- No third-party libraries required

## Usage

from env_parser import load_env, get, require

load_env(".env")

require(["DATABASE_URL", "API_KEY", "SECRET_KEY"])

print(get("DATABASE_URL"))
print(get("MISSING_KEY", "default"))

## .env format supported

# full line comment
DEBUG=False
PORT=5432
API_KEY=sk-abc123       # inline comment — stripped automatically
NAME="John # Smith"     # quoted # signs are not treated as comments
EMPTY=                  # empty values are handled gracefully

## Implementation notes

### inside_comment()

Detecting inline comments was the most challenging part of Phase 1.

The naive approach — str.find("#") — returns the first # in the string,
which breaks on values like NAME="John # Smith" where the # is inside quotes
and should not be treated as a comment.

A first attempt used str.find() in a loop to collect all # positions,
then compared each position against the quote boundaries to find the real one.
This worked but introduced complexity: a position list, a j counter,
and bounds checking to avoid index errors.

The final version is simpler — a single loop over each character that tracks
whether we are currently inside quotes via an in_quote flag. When a # is
found outside quotes, we record its position and break immediately.

Key lessons:
- str.find() alone is not enough when context matters
- A boolean flag is simpler than tracking position ranges
- idx = None is a cleaner sentinel than idx = 0 since 0 is a valid position

### load_env(), get(), require()

Phase 2 introduced three functions that turn the parser into a usable tool.

load_env() parses the .env file and injects every key into os.environ
so the entire process and its subprocesses can access the values.

get() wraps os.environ.get() as a single point of control — masking,
casting, and logging can be added later without touching calling code.

require() collects all missing required keys before calling sys.exit(1),
so the pipeline fails with a complete error report rather than one key at a time.

## Roadmap

- [x] Parse .env into typed Python dictionary
- [x] Automatic type casting
- [x] Inline comment handling
- [x] Load parsed data into os.environ
- [x] Required key validation with sys.exit(1)
- [ ] Secret masking in output
- [ ] Write/update .env file
- [ ] Nested variable expansion e.g. BASE_URL=${HOST}:${PORT}