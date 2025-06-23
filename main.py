from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ws_listener import latest_klines, start_ws_thread

app = FastAPI()

# CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    start_ws_thread()

@app.get("/live/{symbol}")
def get_latest_kline(symbol: str):
    filtered = {k: v for k, v in latest_klines.items() if k.lower().startswith(symbol.lower())}
    return filtered
