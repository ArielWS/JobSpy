import random
import string
from datetime import datetime, timezone

# —————————————————————————————————————————————————————————————————————
# Helpers to randomize your mobile/app fingerprint values each session
# —————————————————————————————————————————————————————————————————————

# A small pool of genuine ZipRecruiter mobile-app UAs—rotate each session
MOBILE_UAS = [
    "Job Search/91.0 (iPhone; CPU iOS 16_6_1 like Mac OS X)",
    "Job Search/90.0 (iPhone; CPU iOS 16_5 like Mac OS X)",
    "Job Search/92.0 (Android; Android 13; Pixel 7)",
    "Job Search/93.0 (Android; Android 14; Galaxy S23)"
]
def get_random_mobile_ua() -> str:
    return random.choice(MOBILE_UAS)

# Generate a 32-char uppercase/digit device ID
def generate_device_id(length: int = 32) -> str:
    pool = string.ascii_uppercase + string.digits
    return "".join(random.choices(pool, k=length))

# —————————————————————————————————————————————————————————————————————
# Update the headers to use randomized mobile/app values
# —————————————————————————————————————————————————————————————————————

headers = {
    "Host": "api.ziprecruiter.com",
    "accept": "*/*",
    # Dynamic override token—keeps the same format but new vid per run
    "x-zr-zva-override": f"100000000;vid:{generate_device_id()}",
    # Static push-notification ID can stay (it’s less likely to be fingerprinted)
    "x-pushnotificationid": "0ff4983d38d7fc5b3370297f2bcffcf4b3321c418f5c22dd152a0264707602a0",
    # Rotate the “device” each run
    "x-deviceid": generate_device_id(),
    # Mobile/app User-Agent—must stay in Job Search/<ver> (iPhone/Android) format
    "user-agent": get_random_mobile_ua(),
    # Keep your own Base64 auth token here
    "authorization": "Basic YTBlZjMyZDYtN2I0Yy00MWVkLWEyODMtYTI1NDAzMzI0YTcyOg==",
    "accept-language": "en-US,en;q=0.9",
}

# —————————————————————————————————————————————————————————————————————
# Cookie data for the “session event” call—timestamp updated each run
# —————————————————————————————————————————————————————————————————————

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
    # Use current UTC timestamp to avoid stale fingerprinting
    ("property", f"timestamp:{datetime.now(timezone.utc).isoformat()}"),
    ("property", "screen_height:852"),
    ("property", "os_version:16.6.1"),
    ("property", "source:install"),
    ("property", "screen_width:393"),
    ("property", "device_model:iPhone 14 Pro"),
    ("property", "brand:Apple"),
]
