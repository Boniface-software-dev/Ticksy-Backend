# resources/mpesaConfig.py
import requests
from base64 import b64encode
from datetime import datetime
import os

# Set these as environment variables ideally
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "your_passkey_here")
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "your_consumer_key")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "your_consumer_secret")
MPESA_BASE_URL = "https://sandbox.safaricom.co.ke"

def get_access_token():
    url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return response.json().get("access_token")

def initiate_stk_push(phone_number, amount, order_id):
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://ticksy-frontend.vercel.app/api/v1/mpesa/callback",
        "AccountReference": order_id,
        "TransactionDesc": "Ticket Order Payment"
    }

    res = requests.post(f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
    return res.json()


