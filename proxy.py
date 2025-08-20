from flask import Flask, request
import requests

app = Flask(__name__)

# 전달할 Webhook URL
TARGET_WEBHOOK = "https://59.23.119.207:5959/webhook"
VERIFY_TOKEN = "shangusdnswl"

@app.route("/webhook", methods=["POST"])
def proxy():
    data = request.get_json(force=True, silent=True) or {}
    try:
        # 받은 JSON을 그대로 TARGET_WEBHOOK로 전달
        resp = requests.post(TARGET_WEBHOOK, json=data)
        return "ok", 200
    except Exception as e:
        return f"Error: {e}", 500
    
@app.get("/webhook")
def verify():
    if (request.args.get("hub.mode") == "subscribe"
        and request.args.get("hub.verify_token") == VERIFY_TOKEN):
        return request.args.get("hub.challenge"), 200
    return "fail", 403

@app.route("/ping")
def ping():
    return "pong", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
