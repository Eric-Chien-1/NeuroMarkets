import os
import yfinance as yf
import pandas as pd
import logging

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logger (same as main.py and NewsScraper.py)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

class PriceScraper:
    def __init__(self, tickers=None):
        """
        tickers: list of ticker symbols or a single string
        Example: ["ES=F", "NQ=F", "YM=F", "RTY=F"]
        """
        if isinstance(tickers, str):
            tickers = [tickers]
        self.tickers = tickers or ["ES=F"]

    def get_historical_data(self, days=30):
        """
        Fetch historical price data for each ticker.
        Returns: dict {ticker: DataFrame}
        """
        results = {}
        for ticker in self.tickers:
            if days <= 30:
                interval = "30m"
                period = f"{days}d"
            elif days <= 60:
                interval = "1h"
                period = f"{days}d"
            else:
                interval = "1d"
                period = f"{max(days, 60)}d"

            try:
                df = self._get_intraday_data(ticker, period=period, interval=interval)
                results[ticker] = df
            except Exception as e:
                log.error(f"Failed to fetch data for {ticker}: {e}")

        return results

    def _get_intraday_data(self, ticker, period="30d", interval="30m"):
        """
        Fetch historical data for a single ticker and ensure correct datetime formatting.
        """
        log.info(f"Fetching price data for {ticker} ({period}, {interval})...")

        df = yf.download(ticker, period=period, interval=interval)
        if df.empty:
            raise Exception(f"No price data found for {ticker}.")

        df = df.reset_index()

        # Handle multi-index from yfinance
        if isinstance(df.columns[0], tuple):
            df.columns = [col[0].lower() if isinstance(col, tuple) else str(col).lower()
                          for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]

        # Ensure datetime column
        if "datetime" not in df.columns:
            if "date" in df.columns:
                df.rename(columns={"date": "datetime"}, inplace=True)
            elif "index" in df.columns:
                df.rename(columns={"index": "datetime"}, inplace=True)
            else:
                raise Exception("No datetime column found in downloaded data.")

        # Keep relevant columns
        keep_cols = ["datetime", "open", "high", "low", "close", "volume"]
        df = df[[c for c in keep_cols if c in df.columns]]

        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df = df.sort_values("datetime").reset_index(drop=True)

        log.info(f"Retrieved {len(df)} rows for {ticker}.")
        return df
