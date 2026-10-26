"""Says whether the API key in .env.local is set. Never prints the key."""
import os
import sys

from garmin_api import ENV_FILE, read_key

if not os.path.exists(ENV_FILE):
    sys.exit(f"NOT SET: {ENV_FILE} doesn't exist. Run the setup step again.")
key = read_key()
if not key:
    sys.exit("NOT SET: .env.local has no key after the = sign. Paste it there and save.")
if any(c.isspace() for c in key):
    sys.exit("PROBLEM: the key contains a space or line break. Re-copy it from Garmin.")
print(f"SET: your key is in .env.local ({len(key)} characters).")
