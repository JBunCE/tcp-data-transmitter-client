import requests
import json

BASE_URL = "http://localhost:8080/api/v1"


def login(phone_number, password):
    url = f"{BASE_URL}/application/access"
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


def create_stream(stream_title, stream_description, user):
    url = f"{BASE_URL}/stream"
    payload = json.dumps({
        "title": stream_title,
        "description": stream_description,
        "WRTCUrl": "http://WBRTC-URL",
        "startDate": "2024-06-29",
        "endDate": "2024-06-29",
        "startTime": "10:00",
        "endTime": "11:00",
        "authorId": user
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)
    return response.json()
