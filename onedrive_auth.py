# onedrive_auth.py
import os
import json
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID")
CLIENT_SECRET = os.getenv("ONEDRIVE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ONEDRIVE_REDIRECT_URI")
TOKEN_FILE = "onedrive_token.json"

AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"


def get_authorization_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": "offline_access Files.ReadWrite.All",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def fetch_tokens(auth_code):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(TOKEN_URL, data=data)
    tokens = response.json()
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)
    return tokens


def refresh_access_token():
    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(TOKEN_URL, data=data)
    new_tokens = response.json()
    with open(TOKEN_FILE, "w") as f:
        json.dump(new_tokens, f)
    return new_tokens


def get_access_token():
    try:
        with open(TOKEN_FILE, "r") as f:
            tokens = json.load(f)
        return tokens["access_token"]
    except Exception:
        return None


def upload_file_to_onedrive(file_path, onedrive_path):
    access_token = get_access_token()
    if not access_token:
        raise Exception("Access token not found")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
    }
    with open(file_path, "rb") as f:
        content = f.read()

    url = f"{GRAPH_API_BASE}/me/drive/root:/{onedrive_path}:/content"
    response = requests.put(url, headers=headers, data=content)
    return response.status_code, response.json()
