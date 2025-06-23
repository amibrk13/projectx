from fastapi import FastAPI
from utils import get_full_analysis

app = FastAPI()

@app.get("/analyze/{symbol}")
async def analyze(symbol: str):
    symbol = symbol.upper()
    if symbol not in ["BONKUSDT", "BTCUSDT"]:
        return {"error": "Only BONKUSDT and BTCUSDT supported"}
    return await get_full_analysis(symbol)

import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # по умолчанию 8000 — для локального запуска
    uvicorn.run("main:app", host="0.0.0.0", port=port)
