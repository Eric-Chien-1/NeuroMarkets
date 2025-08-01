from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from StocksScraper import StocksScraper
from NewsScraper import NewsScraper
from EconomicNewsScraper import EconomicNewsScraper
import traceback
import yfinance as yf

app = FastAPI(title="Market News & Analysis API", version="1.0")

ns = NewsScraper()
es = EconomicNewsScraper()
ss = StocksScraper()

@app.get("/")
def home():
    return {"message": "Welcome to the Market News & Analysis API"}

@app.get("/news")
def getNews():
    return ns.run()

@app.get("/economic-events")
def getEconomicEvents():
    return es.run()

@app.get("/stocks/history")
def get_stocks_history(
    symbol: str = Query(...),
    period: str = Query("1mo"),
    interval: str = Query("1d")
):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            return {"error": f"No data found for {symbol}"}

        return df.reset_index().to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}


@app.get("/merged")
def getMerged():
    """Merge news + economic events sorted by datetime."""
    return sorted(
        ns.run() + es.run(),
        key=lambda x: x["datetime"]
    )
