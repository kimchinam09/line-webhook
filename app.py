from flask import Flask, request, abort
import json
import requests
import os

app = Flask(__name__)

# Token bí mật từ LINE
CHANNEL_ACCESS_TOKEN = "8K79Qi64N+UDt2e5L1T+Q4NgvnmEeQP4y7mfkwrxv+F0CVW4Qk7RXJxj1qDaTURYFCBFQHHn3aaj6x64xTCsDMbFM/EZ78l85mfLKavAJ9laclwvjK4AYe6KtNJwtrULsFN4SOMoWUkIhwGKYyaANwdB04t89/1O/w1cDnyilFU="  # Đảm bảo biến môi trường được set
print("🔐 CHANNEL_ACCESS_TOKEN:", CHANNEL_ACCESS_TOKEN)  # In ra để kiểm tra (xóa dòng này khi deploy thực tế)

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

    print("📤 Payload gửi LINE:")
    print(json.dumps(data, indent=2))

    response = requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=headers,
        data=json.dumps(data)
    )

    print("📨 Phản hồi từ LINE:")
    print("➡ Status:", response.status_code)
    print("➡ Body:", response.text)

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

            if event_type == "join":
                print("🤖 Bot vừa được thêm vào nhóm, đang gửi lời chào...")
                reply_message(reply_token, "Xin chào! Tôi đã tham gia nhóm và sẵn sàng hỗ trợ.")

        return "OK", 200

    except Exception as e:
        print("❌ Lỗi xử lý webhook:", str(e))
        return "ERROR", 500

if __name__ == "__main__":
    app.run()
