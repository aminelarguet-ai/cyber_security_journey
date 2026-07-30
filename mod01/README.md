env-parser 🐍
A lightweight .env file parser written in pure Python — no extra packages needed!
I built this as a learning project to understand how configuration management works, how to handle secrets safely, and what “production-grade” logging actually means. If you’re learning too, hopefully this helps!
 
What’s inside?
File
What it does
Best for
main.py
Simple functions: load, get, save
Quick scripts, beginners
env_parser.py
Classes: Parser, EnvStore, EnvFile
Bigger projects, OOP practice
secure_logging.py
JSON logs that auto-hide secrets
Production / learning logging
logger.py
Basic file logging
Seeing the “before” version
Why two versions? I wanted to see how the same idea looks as plain functions vs. classes. Both work! Pick whichever makes more sense to you.
 
Quick Start
The simple way (functions in main.py)
from main import load_env, get, require
from secure_logging import get_secure_logger

# 1. Load your .env file into the environment
load_env(".env")

# 2. Make sure the important stuff is there
require(["DATABASE_URL", "API_KEY", "SECRET_KEY"])

# 3. Grab values when you need them
print(get("DATABASE_URL"))                    # normal value
print(get("API_KEY"))                          # auto-masked (shows abcd****)
print(get("PORT", default="8080"))            # fallback if not set

# 4. Log stuff safely — secrets get hidden automatically!
logger = get_secure_logger(__name__)
logger.info("Database connected", extra={"extra_data": {
   "host": get("DATABASE_URL"),
   "api_key": get("API_KEY")  # shows as REDACTED in logs
}})

The object-oriented way (env_parser.py)
from env_parser import Parser, EnvFile, EnvStore
from secure_logging import get_secure_logger

logger = get_secure_logger(__name__)

# 1. Read the file (strips out blank lines and comments)
file = EnvFile(".env")
cleaned_lines = file.read()

# 2. Parse into a dictionary
parser = Parser()
parser.parse(cleaned_lines)

# 3. Load into the store
store = EnvStore()
store.load(parser.data)

# 4. Use it!
print(store.get("API_KEY"))  # auto-masked
logger.info("Config loaded", extra={"extra_data": {"keys": len(parser.data)}})

 
What syntax does it support?
# This is a full-line comment — it's saved separately

DEBUG=False
PORT=5432
DATABASE_URL=postgres://localhost/db

# Only the FIRST = is the delimiter — the rest are part of the value
TOKEN=abc=123=xyz

# Inline comments get stripped from the value
API_KEY=secret123  # production key

# But # inside quotes is kept as-is!
NAME="John # Smith"

# Empty values are allowed
EMPTY=

# You can reference other variables with ${VAR}
BASE_URL=https://example.com
API_URL=${BASE_URL}/api/v1

 
API Cheatsheet
main.py — Functions
Function
What it does
load_env(path)
Reads .env and loads everything into os.environ
read_and_parse(path)
Reads .env and returns (data_dict, comments_dict) without touching os.environ
get(key, default=None, masked=False)
Gets a value. Auto-masks secrets by key name.
require(["KEY1", "KEY2"])
Checks keys exist. If any are missing, prints what’s missing and exits.
write_env(path, data, overwrite=False)
Saves a dict back to .env format. Won’t overwrite unless you say so!
expand(data)
Replaces ${VAR} with actual values. Detects circular references so it won’t loop forever.
env_parser.py — Classes
Class
What it does
Parser()
Turns lines of text into a clean dictionary
EnvStore()
Holds the data and gives you get() / require()
EnvFile(path)
Reads/writes the actual file on disk
secure_logging.py — Safe Logging
from secure_logging import get_secure_logger

logger = get_secure_logger("myapp")

# Simple message
logger.info("Server started")

# Message with extra info
logger.warning("Slow query", extra={"extra_data": {
   "query_time_ms": 1234,
   "table": "users"
}})

# If something breaks, include the traceback
logger.error("Auth failed", exc_info=True)

What the log looks like:
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

 
Secret Masking — How it works
When you get() a value
If the key name contains any of these words, the value gets masked automatically:
password, secret, key, token, api

Values longer than 4 chars: shows first 4, then * (e.g. abcd******)
Values 4 chars or less: fully masked (e.g. ****)
get("API_KEY")       # "abcd******"
get("SECRET")        # "****"
get("DATABASE_URL")  # "postgres://localhost/db"  (not masked — safe to show)

When you log something
The logger scans every field name in your extra_data. If it matches a sensitive name, the value becomes "REDACTED" — even if it’s nested deep inside a dictionary or inside a list.
Sensitive names it looks for:
password, passwd, pwd,
token, access_token, refresh_token,
secret, api_key, apikey,
authorization, auth,
ssn, social_security_number,
credit_card, card_number, cvv,
private_key

Example:
logger.info("Auth attempt", extra={"extra_data": {
   "user": "alice",
   "credentials": {
       "password": "hunter2",
       "api_key": "sk-1234567890"
   }
}})

Output:
{
 "extra": {
   "user": "alice",
   "credentials": {
     "password": "REDACTED",
     "api_key": "REDACTED"
   }
 }
}

💡 The point: You don’t have to remember to hide secrets. The code does it for you. That’s way safer than hoping you don’t accidentally log a password!
 
Exporting back to .env
Got a dictionary and want to save it as a .env file? Easy:
from main import write_env

data = {"HOST": "localhost", "PORT": 5432, "DEBUG": False}
write_env(".env.backup", data)

Result:
HOST=localhost
PORT=5432
DEBUG=False

By default, it won’t overwrite an existing file. Pass overwrite=True if you mean it.
 
How the parsing actually works
Type conversion order
When the parser sees a value, it tries to convert it in this order:
Empty string → ""
"true" / "false" (any case) → bool
"quoted" or 'quoted' → str (quotes stripped)
Looks like a number? → int
Looks like a decimal? → float
Everything else → str
Comments
The parser uses a simple character scanner. It keeps track of whether you’re inside quotes. If you are, # is just a character. If you’re not, # starts a comment.
NAME="John # Smith"   → value is: John # Smith
API_KEY=secret # ok   → value is: secret, comment is: ok

Variable expansion
${VAR} gets replaced with the actual value. If A depends on B and B depends on A, the parser catches that and stops instead of looping forever.
 
Testing
You’ll need pytest:
pip install pytest

Run everything:
pytest

Run specific files:
pytest test_parser.py     # parsing, masking, expansion, file I/O
pytest test_logging.py    # JSON logs, redaction, nested data

What’s tested?
Area
Covered?
Normal values, empty values, multiple = signs
✅
Inline comments, quoted #, full-line comments
✅
bool, int, float, str conversion
✅
Masking short/long values, key name detection
✅
Writing files, overwrite protection
✅
Expansion: single, nested, missing vars, circular refs
✅
JSON format, nested redaction, case-insensitive matching
✅
 
Security
Static analysis
The code is scanned with Bandit:
pip install bandit
bandit -r .

Current status: ✅ Clean — no issues found.
What makes this “secure by default”?
🔒 No secrets in source code — designed to keep them in .env files
🔒 Auto-masking — secrets get hidden without you doing anything
🔒 Circular reference protection — expansion can’t infinite-loop
🔒 Overwrite protection — won’t accidentally wipe your .env
🔒 Deep redaction — sensitive fields hidden at any nesting depth in logs
🔒 Pre-commit hooks — Gitleaks scans for secrets before you commit
🔒 CI pipeline — automated tests + security scans on every push
CI/CD (GitHub Actions)
Every push and PR runs: 1. Unit tests — pytest makes sure nothing is broken 2. SAST scan — Bandit checks for security bugs 3. Dependency audit — pip-audit checks for known vulnerabilities 4. Secrets scan — Gitleaks catches accidentally committed credentials
 
Learning Path
This repo is basically my learning diary. Here’s how it grew:
Phase
File
What I learned
1
main.py
How to parse text, convert types, and load into os.environ
2
env_parser.py
How to refactor into classes (Parser, EnvStore, EnvFile)
3
logger.py
Basic file logging — the “naive” version
4
secure_logging.py
JSON logging, recursive redaction, production patterns
Each phase still exists so you can compare them. If you’re learning too, try reading them in order — you’ll see the progression from “just make it work” to “make it safe and maintainable.”
 
Installation
git clone <repo-url>
cd mod01

Optional but recommended:
pip install pytest      # for testing
pip install bandit      # for security scanning

 
Why I built this
I wanted to understand: - How .env files actually get parsed (it’s not as simple as it looks!) - What “secure logging” means in practice - Why people use classes instead of just functions - How to catch my own mistakes before they become problems
If any of that sounds interesting, dig around the code. It’s commented and (I hope) readable. Questions welcome! 🙌

Finally this is a test i did run locally and its result 
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
