"""Gets an access token and shows your 5 latest activities."""
import sys

from garmin_api import ApiError, get, get_token

try:
    get_token()
    print("Connected to Garmin: access token received.\n")
    acts = get("/activitylist-service/activities/search/activities",
               {"start": 0, "limit": 5}) or []
except ApiError as e:
    sys.exit(f"\nNot working yet: {e}")

if not acts:
    print("Connection works, but Garmin returned no activities.")
for a in acts:
    meters = a.get("distance") or 0
    date = (a.get("startTimeLocal") or "")[:16]
    kind = (a.get("activityType") or {}).get("typeKey", "?").replace("_", " ")
    print(f"{date}  {kind:<20} {meters / 1000:7.2f} km  /  {meters / 1609.344:6.2f} mi")
