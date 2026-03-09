"""
SwitchBot カーテン操作サーバー
MacroDroidからHTTPリクエストを受け取りSwitchBot APIを叩く
"""

import hashlib
import hmac
import base64
import time
import uuid
import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TOKEN = os.getenv("SWITCHBOT_TOKEN")
SECRET = os.getenv("SWITCHBOT_SECRET")
BASE_URL = "https://api.switch-bot.com/v1.1"
CURTAIN_ID = "E2E0085AFD7E"
PORT = 8080


def make_headers():
    t = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())
    sign = base64.b64encode(
        hmac.new(
            SECRET.encode("utf-8"),
            (TOKEN + t + nonce).encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")
    return {
        "Authorization": TOKEN,
        "sign": sign,
        "nonce": nonce,
        "t": t,
        "Content-Type": "application/json",
    }


def send_curtain_command(command):
    data = json.dumps({
        "command": command,
        "parameter": "default",
        "co"
        "mmandType": "command",
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/devices/{CURTAIN_ID}/commands",
        data=data,
        headers=make_headers(),
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/open":
            result = send_curtain_command("turnOn")
        elif self.path == "/close":
            result = send_curtain_command("turnOff")
        else:
            self.send_response(404)
            self.end_headers()
            return

        status_code = result.get("statusCode")
        self.send_response(200)
        self.end_headers()
        msg = "success" if status_code == 100 else f"failed: {status_code}"
        self.wfile.write(msg.encode("utf-8"))
        print(f"{self.path} → {msg}")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    print(f"サーバー起動中: http://localhost:{PORT}")
    print("停止するには Ctrl+C")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
