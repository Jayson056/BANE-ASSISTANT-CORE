import requests
import json
import os

# Load token from secrets
_sf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "secrets.env")
if os.path.exists(_sf):
    with open(_sf) as _f:
        for _l in _f:
            if _l.strip() and not _l.startswith('#') and '=' in _l:
                _k, _v = _l.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"'))

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

response = requests.get(API_URL)
print(json.dumps(response.json(), indent=2))
