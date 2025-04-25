import random
import string
from datetime import datetime, timezone

# ———————————————————————————————
# Dynamic mobile/app fingerprint helpers
# ———————————————————————————————

# A small pool of genuine ZipRecruiter mobile-app UAs
MOBILE_UAS = [
    "Job Search/91.0 (iPhone; CPU iOS 16_6_1 like Mac OS X)",
    "Job Search/90.0 (iPhone; CPU iOS 16_5 like Mac OS X)",
    "Job Search/92.0 (Android; Android 13; Pixel 7)",
    "Job Search/93.0 (Android; Android 14; Galaxy S23)"
]

def get_random_mobile_ua() -> str:
    """Pick a realistic ZipRecruiter mobile-app User-Agent."""
    return random.choice(MOBILE_UAS)

def generate_device_id(length: int = 32) -> str:
    """Produce a 32-char uppercase/digit string for x-deviceid or vid."""
    pool = string.ascii_uppercase + string.digits
    return "".join(random.choices(pool, k=length))

# ———————————————————————————————
# Static + dynamic headers template
# ———————————————————————————————

# Static values that remain constant across sessions
STATIC_HEADERS = {
    "Host": "api.ziprecruiter.com",
    "accept": "*/*",
    "x-pushnotificationid": "0ff4983d38d7fc5b3370297f2bcffcf4b3321c418f5c22dd152a0264707602a0",
    "authorization": "Basic YTBlZjMyZDYtN2I0Yy00MWVkLWEyODMtYTI1NDAzMzI0YTcyOg==",
    "accept-language": "en-US,en;q=0.9",
}

def make_headers() -> dict[str, str]:
    """
    Combine static headers with fresh dynamic values.
    Call this per instance to get a new fingerprint.
    """
    return {
        **STATIC_HEADERS,
        "x-zr-zva-override": f"100000000;vid:{generate_device_id()}",
        "x-deviceid": generate_device_id(),
        "user-agent": get_random_mobile_ua(),
    }

# ———————————————————————————————
# Cookie data for the session event
# ———————————————————————————————

get_cookie_data = [
    ("event_type", "session"),
    ("logged_in", "false"),
    ("number_of_retry", "1"),
    ("property", "model:iPhone"),
    ("property", "os:iOS"),
    ("property", "locale:en_us"),
    ("property", "app_build_number:4734"),
    ("property", "app_version:91.0"),
    ("property", "manufacturer:Apple"),
    ("property", f"timestamp:{datetime.now(timezone.utc).isoformat()}"),
    ("property", "screen_height:852"),
    ("property", "os_version:16.6.1"),
    ("property", "source:install"),
    ("property", "screen_width:393"),
    ("property", "device_model:iPhone 14 Pro"),
    ("property", "brand:Apple"),
]
