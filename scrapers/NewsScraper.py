# NewsScraper.py
from gnews import GNews
from datetime import datetime
import pytz

class NewsScraper:
    def __init__(self, timezone="US/Eastern", period="1d"):
        self.tz = pytz.timezone(timezone)
        self.google_news = GNews(language='en', country='US', period=period, max_results=50)

    def fetch_market_news(self):
        try:
            news_list = self.google_news.get_news('stock market OR S&P 500 OR Nasdaq OR Dow Jones OR CPI OR PPI OR FOMC')
        except Exception as e:
            print(f"[ERROR] Failed to fetch market news: {e}")
            return []

        articles = []
        for item in news_list:
            try:
                # Convert datetime to US/Eastern timezone
                dt = item.get("published date")
                if isinstance(dt, datetime):
                    dt = dt.astimezone(self.tz)
                else:
                    dt = datetime.now(self.tz)  # fallback

                articles.append({
                    "datetime": dt.isoformat(),
                    "type": "market_news",
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "link": item.get("url", ""),
                    "source": item.get("publisher", {}).get("title", "Google News")
                })
            except Exception:
                continue
        return articles

    def run(self):
        return self.fetch_market_news()
