import httpx
import os
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
BASE_URL = "https://api.bybit.com"

TIMEFRAMES = {
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240"
}

def sign(params: dict):
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{k}={v}" for k, v in sorted_params)
    return hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()


async def get_klines(symbol: str, interval: str):
    params = {
        "category": "spot",
        "symbol": symbol,
        "interval": interval,
        "limit": 1
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/v5/market/kline", params=params)
        data = r.json()["result"]["list"][0]
        return {
            "open": data[1],
            "high": data[2],
            "low": data[3],
            "close": data[4],
            "volume": data[5],
            "turnover": data[6]
        }


async def get_ticker(symbol: str):
    params = {"category": "spot", "symbol": symbol}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/v5/market/tickers", params=params)
        d = r.json()["result"]["list"][0]
        return {
            "lastPrice": d["lastPrice"],
            "volume24h": d["volume24h"],
            "turnover24h": d["turnover24h"],
            "priceChangePercent24h": d["price24hPcnt"]
        }


async def get_full_analysis(symbol: str):
    result = {"data": {}, "ticker": {}}
    for label, tf in TIMEFRAMES.items():
        result["data"][label] = await get_klines(symbol, tf)
    result["ticker"] = await get_ticker(symbol)
    return result
