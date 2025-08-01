# StockScraper.py
import yfinance as yf
from datetime import datetime
import pytz

class StocksScraper:
    def __init__(self, timezone="US/Eastern"):
        self.tz = pytz.timezone(timezone)
        self.tickers = {
            "S&P 500 Futures (ES)": "ES=F",
            "NASDAQ Futures (NQ)": "NQ=F",
            "Micro S&P 500 (MES)": "MES=F",
            "Micro NASDAQ (MNQ)": "MNQ=F"
        }

    def get_realtime_data(self):
        """Fetch latest snapshot prices."""
        symbols = list(self.tickers.values())
        results = []
        try:
            data = yf.download(symbols, period="1d", interval="1m", progress=False, group_by="ticker")
            for name, symbol in self.tickers.items():
                try:
                    df = data[symbol] if symbol in data else None
                    if df is not None and not df.empty:
                        last_price = df["Close"].dropna().iloc[-1]
                        prev_close = df["Close"].dropna().iloc[0]
                        change_pct = ((last_price - prev_close) / prev_close) * 100
                        results.append({
                            "symbol": symbol,
                            "name": name,
                            "last_price": round(last_price, 2),
                            "change_pct": round(change_pct, 2),
                            "timestamp": datetime.now(self.tz).isoformat()
                        })
                    else:
                        results.append({"symbol": symbol, "name": name, "error": "No data"})
                except Exception as e:
                    results.append({"symbol": symbol, "name": name, "error": str(e)})
        except Exception as e:
            return {"error": str(e)}
        return results

    def get_history(self, period="1mo", interval="1d"):
        """
        Fetch historical data with custom timeframe.
        Example: period="1y", interval="1wk" → Weekly chart for 1 year.
        """
        history = {}
        for name, symbol in self.tickers.items():
            try:
                df = yf.download(symbol, period=period, interval=interval, progress=False)
                if df.empty:
                    history[name] = {"error": "No data"}
                    continue
                if df.index.tz is None:
                    df.index = df.index.tz_localize("UTC").tz_convert(self.tz)
                else:
                    df.index = df.index.tz_convert(self.tz)
                history[name] = df.reset_index().to_dict(orient="records")
            except Exception as e:
                history[name] = {"error": str(e)}
        return history

    def run(self, period="1mo", interval="1d"):
        return {
            "realtime": self.get_realtime_data(),
            "history": self.get_history(period=period, interval=interval)
        }
