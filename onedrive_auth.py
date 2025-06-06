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

import json
import os
import requests
from datetime import datetime, timedelta

class OneDriveClient:
    def __init__(self, credentials_path='credentials.json'):
        self.credentials_path = credentials_path
        self.load_tokens()

    def load_tokens(self):
        with open(self.credentials_path, 'r') as f:
            creds = json.load(f)

            self.access_token = creds.get('access_token')
            self.refresh_token = creds.get('refresh_token')
            self.client_id = creds.get('client_id', os.getenv("ONEDRIVE_CLIENT_ID"))
            self.client_secret = creds.get('client_secret', os.getenv("ONEDRIVE_CLIENT_SECRET"))
            self.redirect_uri = creds.get('redirect_uri', os.getenv("ONEDRIVE_REDIRECT_URI"))
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=creds.get("expires_in", 3600))


    def upload_file(self, local_path, remote_filename):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/octet-stream"
        }
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_filename}:/content"
        with open(local_path, 'rb') as f:
            response = requests.put(upload_url, headers=headers, data=f)
        if response.status_code >= 200 and response.status_code < 300:
            print("✅ Tải file lên OneDrive thành công:", remote_filename)
        else:
            print("❌ Upload thất bại:", response.status_code, response.text)

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
if __name__ == "__main__":
    print("📌 Truy cập liên kết sau để cấp quyền cho ứng dụng:")
    print(get_authorization_url())

    auth_code = input("🔐 Dán mã 'code' từ URL sau khi đăng nhập: ").strip()
    if auth_code:
        tokens = fetch_tokens(auth_code)
        print("✅ Access token đã được lưu:", tokens)
    else:
        print("⚠️ Không nhận được mã code.")
