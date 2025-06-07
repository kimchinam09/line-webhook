import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage
from datetime import datetime
from utils.excel_handler import append_to_excel
from onedrive_auth import OneDriveClient

app = Flask(__name__)

# Line credentials
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OneDrive client
onedrive_client = OneDriveClient("onedrive_token.json")

# Temporary image storage
TEMP_IMG_PATH = "tmp_image.jpg"
EXCEL_FILE_PATH = "data.xlsx"

@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    if "-" in text:
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)
        sender_name = profile.display_name

        parts = text.split("-", 1)
        department = parts[0].strip()
        machine = parts[1].strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Save basic info
        append_to_excel(EXCEL_FILE_PATH, sender_name, department, machine, timestamp, image_path=None)
        onedrive_client.upload_file(EXCEL_FILE_PATH,"CIL bot data/data.xlsx")

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_id = event.message.id
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    sender_name = profile.display_name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    image_content = line_bot_api.get_message_content(message_id)
    with open(TEMP_IMG_PATH, "wb") as f:
        for chunk in image_content.iter_content():
            f.write(chunk)
 # Ghi dữ liệu vào file Excel
    append_to_excel(EXCEL_FILE_PATH, sender_name, None, None, timestamp, image_path=TEMP_IMG_PATH)

 # Upload ảnh và Excel lên OneDrive
    image_filename = f"CIL bot data/uploaded_images/{user_id}_{timestamp}.jpg"
    onedrive_client.upload_file(TEMP_IMG_PATH, image_filename)
    onedrive_client.upload_file(EXCEL_FILE_PATH, "CIL bot data/data.xlsx")

    

if __name__ == "__main__":
    app.run(port=8000)
