"""
SwitchBot API v1.1 接続テスト
デバイス一覧と温湿度データを取得して表示する
"""

import hashlib
import hmac
import base64
import time
import uuid
import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("SWITCHBOT_TOKEN")
SECRET = os.getenv("SWITCHBOT_SECRET")
BASE_URL = "https://api.switch-bot.com/v1.1"


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


def get(path):
    req = urllib.request.Request(
        BASE_URL + path,
        headers=make_headers(),
        method="GET",
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))


def main():
    print("=== SwitchBot API 接続テスト ===\n")

    # デバイス一覧を取得
    print("[ デバイス一覧 ]")
    data = get("/devices")
    devices = data.get("body", {}).get("deviceList", [])
    if not devices:
        print("デバイスが見つかりませんでした")
        return

    for d in devices:
        print(f"  - {d['deviceName']} ({d['deviceType']}) / ID: {d['deviceId']}")

    # Meter（温湿度計）のデータを取得
    print("\n[ 温湿度データ ]")
    meters = [d for d in devices if "Meter" in d.get("deviceType", "")]
    if not meters:
        print("Meterが見つかりませんでした")
        return

    for meter in meters:
        status = get(f"/devices/{meter['deviceId']}/status")
        body = status.get("body", {})
        print(f"  {meter['deviceName']}: 温度 {body.get('temperature')}℃ / 湿度 {body.get('humidity')}%")


if __name__ == "__main__":
    main()