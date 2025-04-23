# Updated headers with multiple user-agent options for rotation
headers = {
    "Host": "api.ziprecruiter.com",
    "accept": "*/*",
    "x-zr-zva-override": "100000000;vid:ZT1huzm_EQlDTVEc",
    "x-pushnotificationid": "0ff4983d38d7fc5b3370297f2bcffcf4b3321c418f5c22dd152a0264707602a0",
    "x-deviceid": "D77B3A92-E589-46A4-8A39-6EF6F1D86006",
    "authorization": "Basic YTBlZjMyZDYtN2I0Yy00MWVkLWEyODMtYTI1NDAzMzI0YTcyOg==",
    "accept-language": "en-US,en;q=0.9",
}

# List of user agents for rotation
user_agents = [
    "Job Search/87.0 (iPhone; CPU iOS 16_6_1 like Mac OS X)",
    "Job Search/91.0 (iPhone; CPU iOS 16_7 like Mac OS X)",
    "Job Search/85.0 (iPhone; CPU iOS 15_5 like Mac OS X)",
    "Job Search/88.0 (iPhone; CPU iOS 16_6_1 like Mac OS X)",
    "Job Search/90.0 (iPhone; CPU iOS 15_3 like Mac OS X)",
]

# Get cookie data remains unchanged, but we might want to ensure it gets updated when the user-agent changes
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
    ("property", "timestamp:2025-01-12T12:04:42-06:00"),
    ("property", "screen_height:852"),
    ("property", "os_version:16.6.1"),
    ("property", "source:install"),
    ("property", "screen_width:393"),
    ("property", "device_model:iPhone 14 Pro"),
    ("property", "brand:Apple"),
]

