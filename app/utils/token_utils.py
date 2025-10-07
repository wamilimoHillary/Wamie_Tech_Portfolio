# app/utils/token_utils.py
import secrets
from datetime import datetime, timedelta

def generate_reset_token():
    # Generate a url-safe token ~43 chars
    return secrets.token_urlsafe(32)

def get_reset_expiry(hours=1):
    # Expire in `hours` from now (UTC)
    return datetime.utcnow() + timedelta(hours=hours)
