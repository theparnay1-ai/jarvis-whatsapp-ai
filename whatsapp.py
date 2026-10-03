import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


def send_whatsapp_message(to, message, phone_number_id=None):

    phone_number_id = phone_number_id or os.getenv("PHONE_NUMBER_ID")

    url = f"https://graph.facebook.com/v25.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(url, headers=headers, json=data)

    print("Status:", response.status_code)
    print("Response:", response.text)

    return response