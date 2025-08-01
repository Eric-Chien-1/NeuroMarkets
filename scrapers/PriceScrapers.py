import yfinance as yf
import pandas as pd

class PriceScraper:
    def __init__(self, ticker="ES=F"):
        self.ticker = ticker

    def get_historical_data(self, days=30):
        """
        Automatically picks the right Yahoo Finance interval
        and fetches intraday or daily historical data.
        """
        if days <= 30:
            # Intraday
            interval = "30m"
            period = f"{days}d"
        elif days <= 60:
            # Hourly
            interval = "1h"
            period = f"{days}d"
        else:
            # Daily
            interval = "1d"
            # Yahoo only accepts specific period strings for >60 days
            period = f"{max(days, 60)}d"

        return self.get_intraday_data(period=period, interval=interval)

    def get_intraday_data(self, period="30d", interval="30m"):
        """
        Fetches historical price data and ensures a proper datetime column.
        """
        print(f"[INFO] Fetching price data for {self.ticker} ({period}, {interval})...")

        # Download data
        df = yf.download(self.ticker, period=period, interval=interval)

        if df.empty:
            raise Exception(f"No price data found for {self.ticker}.")

        # Reset index so datetime is a column
        df = df.reset_index()

        # Handle MultiIndex column names from yfinance (tuple issue fix)
        if isinstance(df.columns[0], tuple):
            df.columns = [col[0].lower() if isinstance(col, tuple) else str(col).lower()
                          for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]

        # Ensure datetime column exists
        if "datetime" not in df.columns:
            if "date" in df.columns:
                df.rename(columns={"date": "datetime"}, inplace=True)
            elif "index" in df.columns:
                df.rename(columns={"index": "datetime"}, inplace=True)
            else:
                raise Exception("No datetime column found in downloaded data.")

        # Keep only relevant columns
        keep_cols = ["datetime", "open", "high", "low", "close", "volume"]
        df = df[[c for c in keep_cols if c in df.columns]]

        # Ensure datetime type
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

        # Sort chronologically
        df = df.sort_values("datetime").reset_index(drop=True)

        return df
