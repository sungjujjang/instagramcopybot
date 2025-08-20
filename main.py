# requirements: pip install flask requests python-dotenv
import os, hmac, hashlib, requests
from flask import Flask, request, abort
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag

load_dotenv()

cl = Client()
cl.login(
    os.getenv("ID"), 
    os.getenv("PW")
)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
APP_SECRET   = os.getenv("APP_SECRET")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
API          = "https://graph.facebook.com/v21.0"

app = Flask(__name__)

@app.get("/webhook")
def verify():
    if (request.args.get("hub.mode") == "subscribe"
        and request.args.get("hub.verify_token") == VERIFY_TOKEN):
        return request.args.get("hub.challenge"), 200
    return "fail", 403

def verify_signature(req):
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not sig.startswith("sha256="):
        return False
    digest = hmac.new(APP_SECRET.encode(), msg=req.get_data(), digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig.split("=",1)[1], digest)

def get_comment(comment_id):
    url = f"{API}/{comment_id}"
    params = {"fields": "id,text,username,timestamp,parent_id", "access_token": ACCESS_TOKEN}
    return requests.get(url, params=params).json()

@app.post("/webhook")
def webhook():
    if not verify_signature(request):
        abort(403)

    payload = request.get_json(force=True, silent=True) or {}
    entries = payload.get("entry", [])

    for e in entries:
        for change in e.get("changes", []):
            field = change.get("field")       # "mentions" or "comments"
            value = change.get("value", {})

            comment_id = value.get("comment_id")
            if comment_id:
                c = get_comment(comment_id)
                print(f"\n[MENTION] @{c.get('username')} said: {c.get('text')}")

                parent_id = c.get("parent_id")
                if parent_id:
                    p = get_comment(parent_id)
                    print(f"   ↳ Original by @{p.get('username')}: {p.get('text')}")
                    user_id = cl.user_id_from_username(c.get('username'))
                    text = f'{p.get('text')}'
                    cl.direct_send(text, user_ids=[user_id])

    return "ok", 200

if __name__ == "__main__":
    app.run(host="1.1.1.1", port=80, debug=True)
