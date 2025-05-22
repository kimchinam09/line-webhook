from flask import Flask, request, abort
import json

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    try:
        body = request.get_data(as_text=True)
        data = json.loads(body)

        print("✅ Dữ liệu nhận từ LINE:")
        print(json.dumps(data, indent=4))

        if "events" not in data:
            return "No events", 200

        for event in data["events"]:
            event_type = event.get("type", "")
            print(f"📌 Nhận event: {event_type}")

            # Xử lý khi bot được mời vào nhóm
            if event_type == "join":
                print("🤖 Bot đã được thêm vào nhóm.")
                # Không cần phản hồi gì thêm, chỉ cần không lỗi là LINE giữ bot lại

            # Xử lý khi có tin nhắn gửi đến
            elif event_type == "message":
                msg_type = event["message"]["type"]
                print(f"✉️ Tin nhắn loại: {msg_type}")
                if msg_type == "text":
                    text = event["message"]["text"]
                    print(f"📄 Nội dung: {text}")

        return "OK", 200

    except Exception as e:
        print("❌ Lỗi xử lý webhook:", str(e))
        return "ERROR", 500

if __name__ == "__main__":
    app.run()
