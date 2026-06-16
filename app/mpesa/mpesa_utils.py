"""
app/mpesa/mpesa_utils.py
M-Pesa Daraja API helpers — STK Push (sandbox)
"""
import base64
import requests
from datetime import datetime
import os


# ─────────────────────────────────────────────
#  READ CREDENTIALS FROM ENV
# ─────────────────────────────────────────────
CONSUMER_KEY    = os.getenv("MPESA_CONSUMER_KEY", "")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
SHORTCODE       = os.getenv("MPESA_SHORTCODE", "174379")       # sandbox default
PASSKEY         = os.getenv("MPESA_PASSKEY", "")
CALLBACK_URL    = os.getenv("MPESA_CALLBACK_URL", "")         # your ngrok / public URL

# Sandbox base URL
BASE_URL = "https://sandbox.safaricom.co.ke"


# ─────────────────────────────────────────────
#  1. GET ACCESS TOKEN
# ─────────────────────────────────────────────
def get_access_token() -> str:
    """Return a fresh OAuth access token from Daraja sandbox."""
    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode("utf-8")

    response = requests.get(
        url,
        headers={"Authorization": f"Basic {encoded}"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


# ─────────────────────────────────────────────
#  2. GENERATE PASSWORD
# ─────────────────────────────────────────────
def generate_password() -> tuple[str, str]:
    """
    Returns (password, timestamp).
    password = base64(Shortcode + Passkey + Timestamp)
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw = f"{SHORTCODE}{PASSKEY}{timestamp}"
    password = base64.b64encode(raw.encode()).decode("utf-8")
    return password, timestamp


# ─────────────────────────────────────────────
#  3. INITIATE STK PUSH
# ─────────────────────────────────────────────
def stk_push(phone: str, amount: int, account_ref: str = "WamieTech", description: str = "Payment") -> dict:
    """
    Trigger a Lipa Na M-Pesa Online (STK Push) request.

    Args:
        phone:        Customer phone in format 2547XXXXXXXX
        amount:       Amount in KES (integer)
        account_ref:  Account reference string shown on customer's phone
        description:  Transaction description

    Returns:
        Daraja API JSON response dict
    """
    # Normalise phone: strip leading 0 or + and ensure 254 prefix
    phone = str(phone).strip()
    if phone.startswith("+"):
        phone = phone[1:]
    if phone.startswith("0"):
        phone = "254" + phone[1:]

    access_token = get_access_token()
    password, timestamp = generate_password()

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password":          password,
        "Timestamp":         timestamp,
        "TransactionType":   "CustomerPayBillOnline",
        "Amount":            int(amount),
        "PartyA":            phone,
        "PartyB":            SHORTCODE,
        "PhoneNumber":       phone,
        "CallBackURL":       CALLBACK_URL,
        "AccountReference":  account_ref,
        "TransactionDesc":   description,
    }

    response = requests.post(
        f"{BASE_URL}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────────────────
#  4. STK PUSH QUERY (check status)
# ─────────────────────────────────────────────
def stk_query(checkout_request_id: str) -> dict:
    """Query the status of a pending STK push."""
    access_token = get_access_token()
    password, timestamp = generate_password()

    payload = {
        "BusinessShortCode":    SHORTCODE,
        "Password":             password,
        "Timestamp":            timestamp,
        "CheckoutRequestID":    checkout_request_id,
    }

    response = requests.post(
        f"{BASE_URL}/mpesa/stkpushquery/v1/query",
        json=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
