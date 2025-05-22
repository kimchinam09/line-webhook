from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    print(json.dumps(data, indent=2))
    return 'OK', 200

@app.route("/", methods=["POST"])
def webhook():
    print("✅ Nhận được yêu cầu từ LINE")
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
