import random
import string
import secrets
from datetime import datetime, timezone

# ———————————————————————————————
# Dynamic mobile/app fingerprint helpers
# ———————————————————————————————

# A larger, up-to-date pool of genuine ZipRecruiter mobile-app UAs
MOBILE_UAS = [
    # iOS versions:
    "Job Search/100.0 (iPhone; CPU iOS 17_3 like Mac OS X)",
    "Job Search/101.0 (iPhone; CPU iOS 17_4 like Mac OS X)",
    # Android versions:
    "Job Search/102.0 (Android; Android 14; Pixel 8)",
    "Job Search/103.0 (Android; Android 15; Galaxy S24)",
    "Job Search/98.0 (iPhone; CPU iOS 16_5 like Mac OS X)",
    "Job Search/99.0 (Android; Android 13; Pixel 7)",
]

def get_random_mobile_ua() -> str:
    """Pick a realistic ZipRecruiter mobile-app User-Agent."""
    return random.choice(MOBILE_UAS)

def generate_device_id(length: int = 32) -> str:
    """Produce a 32-char uppercase/digit string for x-deviceid or vid."""
    pool = string.ascii_uppercase + string.digits
    return "".join(random.choices(pool, k=length))

def generate_pushnotification_id(length: int = 64) -> str:
    """
    Produce a cryptographically secure hex string to simulate a real pushnotification token.
    Real mobile apps register a unique APNs/FCM token per install.
    """
    return secrets.token_hex(length // 2)  # 64 hex chars → 32 bytes

# ———————————————————————————————
# Static values that remain constant across sessions
# ———————————————————————————————

_STATIC_BASE_AUTH = "Basic YTBlZjMyZDYtN2I0Yy00MWVkLWEyODMtYTI1NDAzMzI0YTcyOg=="  # <– same JobSpy mobile token

STATIC_HEADERS = {
    "Host": "api.ziprecruiter.com",
    "accept": "*/*",
    "authorization": _STATIC_BASE_AUTH,
    "accept-language": "en-US,en;q=0.9",
}

def make_headers() -> dict[str, str]:
    """
    Combine static headers with fresh dynamic values. Call this per session to get a new fingerprint.
    """
    return {
        **STATIC_HEADERS,
        # Rotate pushnotification ID on every session, instead of using a static one:
        "x-pushnotificationid": generate_pushnotification_id(64),
        # Rotate “zva” fingerprint:
        "x-zr-zva-override": f"100000000;vid:{generate_device_id()}",
        # Rotate device ID:
        "x-deviceid": generate_device_id(),
        # Rotate through a larger, updated UA pool:
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
    ("property", "app_build_number:1010"),  # bump for newer app version
    ("property", "app_version:101.0"),
    ("property", "manufacturer:Apple"),
    ("property", f"timestamp:{datetime.now(timezone.utc).isoformat()}"),
    ("property", "screen_height:852"),
    ("property", "os_version:17.3"),
    ("property", "source:install"),
    ("property", "screen_width:393"),
    ("property", "device_model:iPhone 16 Pro"),
    ("property", "brand:Apple"),
]
