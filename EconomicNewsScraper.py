# EconomicNewsScraper.py
import requests
from datetime import datetime
import pytz

class EconomicNewsScraper:
    def __init__(self, timezone="US/Eastern"):
        self.tz = pytz.timezone(timezone)

    def fetch_tradingeconomics(self):
        url = "https://api.tradingeconomics.com/calendar?c=guest:guest&f=json"

        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[ERROR] Failed to fetch economic events: {e}")
            return []

        events = []
        for e in data:
            if e.get("Country") == "United States":
                try:
                    # Try parsing date (with or without milliseconds)
                    try:
                        dt = datetime.strptime(e["Date"], "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        dt = datetime.strptime(e["Date"], "%Y-%m-%dT%H:%M:%S.%f")

                    dt = pytz.utc.localize(dt).astimezone(self.tz)
                except Exception:
                    continue

                events.append({
                    "datetime": dt.isoformat(),
                    "type": "economic_event",
                    "title": e.get("Event", ""),
                    "actual": e.get("Actual"),
                    "forecast": e.get("Forecast"),
                    "previous": e.get("Previous"),
                    "importance": e.get("Importance", ""),
                    "source": "TradingEconomics"
                })
        return events

    def run(self):
        return self.fetch_tradingeconomics()
