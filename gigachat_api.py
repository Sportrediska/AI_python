import json
import uuid
from enum import verify

import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

from utils import get_file_id

CLIENT_ID = st.secrets["CLIENT_ID"]
SECRET = st.secrets["SECRET"]

# curl -L -X POST 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth' \
# -H 'Content-Type: application/x-www-form-urlencoded' \
# -H 'Accept: application/json' \
# -H 'RqUID: 31c6b453-b8d4-481b-8903-dce923125feb' \
# -H 'Authorization: Basic <Authorization key>' \
# --data-urlencode 'scope=GIGACHAT_API_PERS'

def get_access_token() -> str:
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
    }
    payload = {"scope": "GIGACHAT_API_PERS"}
    res = requests.post(
            url=url,
            headers=headers,
            auth=HTTPBasicAuth(CLIENT_ID, SECRET),
            data=payload,
            verify = False
    )
    access_token = res.json()["access_token"]
    return access_token


def get_image(file_id: str, access_token: str):

    url = f"https://gigachat.devices.sberbank.ru/api/v1/files/{file_id}/content"

    payload = {}
    headers = {
        'Accept': 'image/jpg',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers, data=payload, verify = False)

    return response.content

def send_prompt(msg: str, access_token: str):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    payload = json.dumps({
        "model": "GigaChat-Pro",
        "messages": [
            {
                "role": "user",
                "content": msg
            }
        ],
        "stream": False,
        "update_interval": 0,
        "function_call": "auto"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(url, headers=headers, data=payload, verify = False)
    return response.json()["choices"][0]["message"]["content"]


def send_prompt_and_get_response(msg: str, access_token: str):
    res = send_prompt(msg, access_token)
    data, is_image = get_file_id(res)
    if is_image:
        data = get_image(file_id=data, access_token=access_token)
    return data, is_image