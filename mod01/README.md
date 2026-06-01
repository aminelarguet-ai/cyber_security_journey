# env-parser

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
