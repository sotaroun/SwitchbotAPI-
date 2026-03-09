"""
SwitchBot API v1.1 接続テスト
デバイス一覧と温湿度データを取得して表示する
"""

import hashlib
import hmac
import base64
import time
import uuid
import json
import urllib.request
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

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


def post(path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers=make_headers(),
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))


def toggle_curtain(device_id):
    """カーテンの状態を確認してトグル（開←→閉）する"""
    status = get(f"/devices/{device_id}/status")
    body = status.get("body", {})
    slide_position = body.get("slidePosition", 0)

    print(f"  現在のslidePosition: {slide_position}")

    # slidePosition: 0=全開, 100=全閉 (実機に合わせて逆に設定)
    if slide_position <= 50:
        parameter = "0,ff,100"  # 全閉 (position=100)
        action = "全閉"
    else:
        parameter = "0,ff,0"    # 全開 (position=0)
        action = "全開"

    result = post(f"/devices/{device_id}/commands", {
        "command": "setPosition",
        "parameter": parameter,
        "commandType": "command",
    })
    status_code = result.get("statusCode")
    return action, status_code


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
    else:
        for meter in meters:
            status = get(f"/devices/{meter['deviceId']}/status")
            body = status.get("body", {})
            print(f"  {meter['deviceName']}: 温度 {body.get('temperature')}℃ / 湿度 {body.get('humidity')}%")

    # カーテンをトグル
    print("\n[ カーテン トグル ]")
    action, status_code = toggle_curtain("E2E0085AFD7E")
    if status_code == 100:
        print(f"  成功: カーテンを{action}にしました")
    else:
        print(f"  失敗 (code: {status_code})")


if __name__ == "__main__":
    main()