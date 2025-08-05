import os
import base64
import requests

from requests.auth import HTTPBasicAuth
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

class Mpesa:
    consumer_key = None
    consumer_secret = None
    business_short_code = "174379"
    timestamp = None

    def __init__(self):
        self.consumer_key = os.environ.get('CONSUMER_KEY')
        self.consumer_secret = os.environ.get('CONSUMER_SECRET')
        self.timestamp =datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_access_token(self):
        res = requests.get(
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
        )
        data = res.json()
        return data["access_token"]
    
    def generate_password(self, timestamp):
        password_str = self.business_short_code + os.environ.get("SAF_PASS_KEY") + timestamp
        encoded_password = base64.b64encode(password_str.encode()).decode("utf-8")

        return encoded_password
    
    def make_stk_push(self, data):
        amount = data["amount"]
        phone = data["phone"]
        desc = data["description"]

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        encoded_password = self.generate_password(timestamp)

        body = {  
            "BusinessShortCode": self.business_short_code,    
            "Password": encoded_password,    
            "Timestamp": timestamp,    
            "TransactionType": "CustomerPayBillOnline",    
            "Amount": amount,    
            "PartyA":phone,    
            "PartyB":self.business_short_code,    
            "PhoneNumber":phone,    
            "CallBackURL": "https://ticksy-backend.onrender.com/payments/callback",    
            "AccountReference":"Ticksy",    
            "TransactionDesc":desc
        }

        token = self.get_access_token()

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        return response.json()
    
    def check_transaction(self, checkout_request_id):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = self.generate_password(timestamp)

        data = {    
            "BusinessShortCode":self.business_short_code,    
            "Password": password,    
            "Timestamp": timestamp,    
            "CheckoutRequestID": checkout_request_id,    
        }

        token = self.get_access_token()

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query",
            json=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        return response.json()