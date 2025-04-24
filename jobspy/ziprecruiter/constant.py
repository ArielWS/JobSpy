# constant.py

from datetime import datetime

# 1.1 Base API headers (no User-Agent here—will inject later)
API_HEADERS = {
    "Host":           "api.ziprecruiter.com",
    "Accept":         "*/*",
    "Authorization":  "Basic YTBlZjMyZDYt…",       # your existing token
    "Accept-Language":"en-US,en;q=0.9",
    # (leave out User-Agent; we’ll add it dynamically)
}

# 1.2 Base cookie payload, minus timestamp & UA
BASE_COOKIE_PAYLOAD = [
    ("event_type",    "session"),
    ("logged_in",     "false"),
    ("number_of_retry","1"),
    # … all your other ("property", "...") lines up to brand
]

# 1.3 Function to build a fresh payload each time
def build_cookie_payload(ua: str) -> list[tuple[str,str]]:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S-00:00")
    return [
        *BASE_COOKIE_PAYLOAD,
        ("property", f"timestamp:{now}"),
        ("property", f"user_agent:{ua}")
    ]

# 1.4 Real-browser User-Agents pool
USER_AGENTS = [
  # your existing five UA strings…
]

# 1.5 Optional: browser-style headers for HTML pages
HTML_HEADERS = {
  "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.9",
  # Referer will be injected in init before each HTML request
}
