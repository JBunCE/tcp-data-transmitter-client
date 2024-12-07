import requests
import json

BASE_URL = "https://api.sci-all.icu/api/v1"


def publish(payload):
    url = f"{BASE_URL}/social/publications"

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return {
            "status": "success",
            "data": response.json()
        }
    else:
        return {
            "status": "error",
            "data": response.json()
        }


def login(phone_number, password):
    url = f"{BASE_URL}/auth/user/login"

    payload = json.dumps({
        "phoneNumber": phone_number,
        "password": password
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        return {
            "status": "success",
            "data": response.json()
        }
    else:
        return {
            "status": "error",
            "data": response.json()
        }
