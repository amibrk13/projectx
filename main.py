from fastapi import FastAPI
from utils import get_full_analysis

app = FastAPI()

@app.get("/analyze/{symbol}")
async def analyze(symbol: str):
    symbol = symbol.upper()
    if symbol not in ["BONKUSDT", "BTCUSDT"]:
        return {"error": "Only BONKUSDT and BTCUSDT supported"}
    return await get_full_analysis(symbol)
