import json
import time
import threading
from fastapi import FastAPI
from websocket import WebSocketApp

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

def on_message(ws, message):
    data = json.loads(message)
    if "topic" in data and "data" in data:
        topic = data["topic"]
        parts = topic.split(".")
        tf = parts[1]
        symbol = parts[2]
        kline_data = data["data"]
        latest_klines.setdefault(symbol, {})[tf] = {
            "open": kline_data["o"],
            "high": kline_data["h"],
            "low": kline_data["l"],
            "close": kline_data["c"],
            "volume": kline_data["v"],
            "turnover": kline_data["t"],
            "timestamp": kline_data["start"]
        }

def on_open(ws):
    print("✅ WebSocket connected (public)")
    args = []
    for symbol in SYMBOLS:
        for tf in INTERVALS.values():
            args.append(f"kline.{tf}.{symbol}")
    ws.send(json.dumps({
        "op": "subscribe",
        "args": args
    }))

def run_ws():
    def _run():
        while True:
            try:
                ws = WebSocketApp(
                    "wss://stream.bybit.com/v5/public/spot",
                    on_open=on_open,
                    on_message=on_message
                )
                ws.run_forever()
            except Exception as e:
                print("🔁 WebSocket reconnecting after error:", e)
                time.sleep(5)
    threading.Thread(target=_run, daemon=True).start()

# Start WebSocket
run_ws()

# FastAPI
app = FastAPI()

@app.get("/live/{symbol}")
def get_latest_klines(symbol: str):
    symbol = symbol.upper()
    return latest_klines.get(symbol, {})
