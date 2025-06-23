
import websocket
import threading
import json
import time
import os
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

SYMBOLS = ["BONKUSDT", "BTCUSDT"]
INTERVALS = {
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240"
}

latest_klines = {}

def generate_auth_payload():
    expires = int(time.time() * 1000) + 10000
    signature_payload = f"{API_KEY}{expires}"
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        signature_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return {
        "op": "auth",
        "args": [API_KEY, expires, signature]
    }

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "topic" in data and "data" in data:
            topic = data["topic"]  # например: "kline.5.BONKUSDT"
            parts = topic.split(".")
            if len(parts) == 3:
                tf = parts[1]
                symbol = parts[2]
                kline_data = data["data"]

                latest_klines[f"{symbol}_{tf}m"] = {
                    "open": kline_data["o"],
                    "high": kline_data["h"],
                    "low": kline_data["l"],
                    "close": kline_data["c"],
                    "volume": kline_data["v"],
                    "turnover": kline_data["t"],
                    "timestamp": kline_data["start"]
                }

                print(f"✅ Updated: {symbol}_{tf}m → close: {kline_data['c']}")
    except Exception as e:
        print("❌ Error in on_message:", e)

def on_open(ws):
    print("✅ WebSocket connected")
    ws.send(json.dumps(generate_auth_payload()))

    time.sleep(1)  # подождём авторизацию
    args = []
    for symbol in SYMBOLS:
        for tf in INTERVALS.values():
            args.append(f"kline.{tf}.{symbol}")
    ws.send(json.dumps({
        "op": "subscribe",
        "args": args
    }))

def run_ws():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://stream.bybit.com/v5/public/spot",
                on_open=on_open,
                on_message=on_message
            )
            ws.run_forever()
        except Exception as e:
            print("🔁 WebSocket reconnecting after error:", e)
            time.sleep(5)

# Thread запускается, если импортировать этот файл
if __name__ == "__main__":
    t = threading.Thread(target=run_ws)
    t.start()
