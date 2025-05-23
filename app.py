from flask import Flask, request, abort
import json
import requests
import os

app = Flask(__name__)

# Token bí mật từ LINE
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")  # hoặc bạn có thể dán trực tiếp để test

def reply_message(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {"type": "text", "text": text}
        ]
    }
    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, data=json.dumps(data))
    print("📨 Trả lời:", response.status_code, response.text)

@app.route("/", methods=["POST"])
def webhook():
    try:
        body = request.get_data(as_text=True)
        data = json.loads(body)
        print(json.dumps(data, indent=4))

        if "events" not in data:
            return "No events", 200

        for event in data["events"]:
            event_type = event.get("type", "")
            reply_token = event.get("replyToken", "")

            if event_type == "join":
                print("🤖 Bot vào nhóm, gửi lời chào...")
                reply_message(reply_token, "Xin chào! Tôi đã tham gia nhóm và sẵn sàng hỗ trợ.")
        
        return "OK", 200

    except Exception as e:
        print("❌ Lỗi xử lý webhook:", str(e))
        return "ERROR", 500

if __name__ == "__main__":
    app.run()
