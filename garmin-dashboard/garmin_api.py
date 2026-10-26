"""Shared helpers for talking to Garmin's Personal API (read-only).

Uses only Python's built-in libraries. The API key is read from .env.local
and is never printed or written anywhere else.
"""
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(HERE, ".env.local")
DATA_DIR = os.path.join(HERE, "data")
TOKEN_FILE = os.path.join(DATA_DIR, "token.json")

API_BASE = "https://personal.connectapi.garmin.com"
TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"
TOKEN_MAX_AGE = 20 * 3600  # tokens last 24h; renew after 20h
PAUSE = 0.4                # seconds between calls
RETRY_CODES = (429, 502, 503)


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def read_key():
    """Return the API key from .env.local, or None if it is not set."""
    if not os.path.exists(ENV_FILE):
        return None
    with open(ENV_FILE, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GARMIN_PERSONAL_API_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                return value or None
    return None


def _ssl_context():
    return ssl.create_default_context()


def _request(method, url, headers):
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60, context=_ssl_context()) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except urllib.error.URLError as e:
        if isinstance(e.reason, ssl.SSLCertVerificationError):
            sys.exit(
                "\nYour Python can't verify secure connections yet.\n"
                "On a Mac: open Finder > Applications > Python 3.x and double-click\n"
                "'Install Certificates.command', then try again."
            )
        raise ApiError(0, f"Could not reach Garmin ({e.reason}). Check your internet connection.")


def _load_saved_token():
    try:
        with open(TOKEN_FILE, encoding="utf-8") as f:
            saved = json.load(f)
        if time.time() - saved["obtained_at"] < TOKEN_MAX_AGE:
            return saved["token"]
    except (OSError, ValueError, KeyError):
        pass
    return None


def get_token(force_new=False):
    """Return a valid access token, exchanging the API key for a new one if needed."""
    if not force_new:
        token = _load_saved_token()
        if token:
            return token
    key = read_key()
    if not key:
        raise ApiError(0, "Your API key is not set in .env.local.")
    status, body = _request("POST", API_BASE + TOKEN_PATH, {"Authorization": "ApiKey " + key})
    if status != 200 or not body.strip():
        raise ApiError(
            status,
            f"Garmin refused the API key (HTTP {status}). It is probably missing, mistyped "
            "or expired. Open .env.local and check it.",
        )
    token = body.decode("utf-8").strip().strip('"')
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump({"token": token, "obtained_at": time.time()}, f)
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except OSError:
        pass
    return token


def get(path, params=None, retries=4):
    """GET a JSON endpoint. Raises ApiError on failure (status 500 = response too big)."""
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    token = get_token()
    renewed = False
    for attempt in range(retries + 1):
        time.sleep(PAUSE)
        status, body = _request("GET", url, {"Authorization": "Bearer " + token,
                                             "Accept": "application/json"})
        if status == 200:
            return json.loads(body) if body.strip() else None
        if status == 204:
            return None
        if status == 401 and not renewed:
            token = get_token(force_new=True)
            renewed = True
            continue
        if status in RETRY_CODES and attempt < retries:
            time.sleep(3 * (attempt + 1))
            continue
        raise ApiError(status, f"HTTP {status} for {path}")
    raise ApiError(0, f"Gave up on {path}")
