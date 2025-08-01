import requests
import pandas as pd
from datetime import datetime, timedelta

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

        print(f"[INFO] Fetching news from {start_date.date()} to {end_date.date()}...")
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch news: {response.status_code} - {response.text}")

        articles = response.json().get("articles", [])
        if not articles:
            raise Exception("No news articles found for the given range.")

        titles, datetimes = [], []
        for article in articles:
            title = article.get("title")
            published_at = article.get("publishedAt")
            if title and published_at:
                titles.append(title)
                datetimes.append(pd.to_datetime(published_at))

        # Always return 'title'
        df = pd.DataFrame({
            "datetime": datetimes,
            "title": titles
        })

        return df.sort_values("datetime").reset_index(drop=True)
