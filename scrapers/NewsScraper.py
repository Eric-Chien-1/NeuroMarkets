import os
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logger (same as in main.py)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self, api_key, query="stock market"):
        self.api_key = api_key
        self.query = query
        self.base_url = "https://newsapi.org/v2/everything"

    def scrape_news(self, days=30):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        params = {
            "q": self.query,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": self.api_key,
            "pageSize": 100
        }

        log.info(f"Fetching news from {start_date.date()} to {end_date.date()}...")
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            log.error(f"Failed to fetch news: {response.status_code} - {response.text}")
            raise Exception(f"Failed to fetch news: {response.status_code} - {response.text}")

        articles = response.json().get("articles", [])
        if not articles:
            log.warning("No news articles found for the given range.")
            return pd.DataFrame(columns=["datetime", "title"])  # Return empty DataFrame

        titles, datetimes = [], []
        for article in articles:
            title = article.get("title")
            published_at = article.get("publishedAt")
            if title and published_at:
                titles.append(title)
                datetimes.append(pd.to_datetime(published_at))

        df = pd.DataFrame({
            "datetime": datetimes,
            "title": titles
        })

        log.info(f"Fetched {len(df)} news articles.")
        return df.sort_values("datetime").reset_index(drop=True)
