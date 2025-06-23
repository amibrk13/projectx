from fastapi import FastAPI
from ws_listener import latest_klines, run_ws

app = FastAPI()

@app.on_event("startup")
def start_ws():
    import threading
    threading.Thread(target=run_ws, daemon=True).start()

@app.get("/live/{symbol}")
def get_live_data(symbol: str):
    symbol = symbol.upper()
    result = {}
    for key, value in latest_klines.items():
        if key.startswith(symbol):
            result[key] = value
    return result
