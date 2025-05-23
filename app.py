from flask import Flask, request, abort
import json
import requests
import os

app = Flask(__name__)

# Token bí mật từ LINE
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")  # Đảm bảo biến môi trường được set

def reply_message(reply_token, text):
    if not CHANNEL_ACCESS_TOKEN:
        print("❌ Lỗi: CHANNEL_ACCESS_TOKEN chưa được cấu hình")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }

    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }

    response = requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=headers,
        data=json.dumps(data)
    )

    print("📨 LINE API Response:")
    print("Status:", response.status_code)
    print("Body:", response.text)

    if response.status_code != 200:
        print("❌ Gửi tin nhắn thất bại. Kiểm tra reply_token, message format hoặc access token.")


@app.route("/", methods=["POST"])
def webhook():
    try:
        body = request.get_data(as_text=True)
        data = json.loads(body)

        print("📥 Nhận sự kiện:")
        print(json.dumps(data, indent=4))

        if "events" not in data:
            return "No events", 200

        for event in data["events"]:
            event_type = event.get("type", "")
            reply_token = event.get("replyToken", "")
            print("🧾 Event type:", event_type)
            print("🔁 replyToken:", reply_token)

            if not reply_token:
                print("❌ Không có replyToken. Không thể gửi tin nhắn.")
                continue  # Nếu không có replyToken, bỏ qua sự kiện này

            if event_type == "join":
                print("🤖 Bot vừa được thêm vào nhóm, đang gửi lời chào...")
                reply_message(reply_token, "Xin chào! Tôi đã tham gia nhóm và sẵn sàng hỗ trợ.")

        return "OK", 200

    except Exception as e:
        print("❌ Lỗi xử lý webhook:", str(e))
        return "ERROR", 500

if __name__ == "__main__":
    app.run()
