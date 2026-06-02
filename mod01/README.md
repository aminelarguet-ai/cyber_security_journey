# env-parser

A lightweight `.env` file parser with secret management, built in pure Python (no dependencies).

## Features

- Parses `.env` files into typed Python dictionaries
- Automatic type casting (bool, int, float, str)
- Handles quoted string values
- Strips inline comments from values
- Tracks full-line and inline comments with line numbers
- No third-party libraries required

## Usage

from env_parser import read_and_parse

data, comments = read_and_parse(".env")
print(data["PORT"])    # 5432 (int)
print(data["DEBUG"])   # True (bool)

## .env format supported

# full line comment
DEBUG=False
PORT=5432
API_KEY=sk-abc123       # inline comment — stripped automatically
NAME="John # Smith"     # quoted # signs are not treated as comments

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

Key lessons from this implementation:
- str.find() alone is not enough when context matters
- A boolean flag is simpler than tracking position ranges
- idx = None is a cleaner sentinel than idx = 0 since 0 is a valid position
- for/else in Python runs the else block only when no break occurred

## Roadmap

- [ ] Load parsed data into os.environ
- [ ] Required key validation with sys.exit(1)
- [ ] Secret masking in output
- [ ] Write/update .env file# env-parser

A lightweight `.env` file parser with secret management, built in pure Python (no dependencies).

## Features
- Parses `.env` files into typed Python dictionaries
- Automatic type casting (bool, int, float, str)
- Handles quoted string values
- Tracks comments with line numbers
- No third-party libraries required

## Usage
```python
from env_parser import read_and_parse

data, comments = read_and_parse(".env")
print(data["PORT"])    # 5432 (int)
print(data["DEBUG"])   # True (bool)
```

## .env format supported
