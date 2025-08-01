import pandas as pd
from textblob import TextBlob
from logger import log  # <-- import shared logger

POSITIVE_KEYWORDS = [
    "earnings beat", "ipo", "record profit", "upgrade", "rate cut", "expands", "surge"
]
NEGATIVE_KEYWORDS = [
    "layoffs", "job losses", "tariff", "underperform", "downgrade", "recession",
    "missed estimates", "slump"
]
ECONOMIC_EVENT_KEYWORDS = [
    "ppi", "producer price index",
    "cpi", "consumer price index",
    "inflation report", "inflation data",
    "fomc", "federal reserve", "fed meeting", "fed statement",
    "interest rate hike", "interest rate cut", "monetary policy"
]

def analyze_sentiment(news_df: pd.DataFrame) -> pd.DataFrame:
    if "title" not in news_df.columns:
        raise ValueError("News DataFrame must have a 'title' column for sentiment analysis.")

    # Calculate sentiment scores
    scores = []
    for text in news_df["title"].fillna(""):
        score = TextBlob(str(text)).sentiment.polarity
        scores.append(score)

    news_df["sentiment"] = scores
    news_df["sentiment_score"] = scores

    # Round for cleaner display
    news_df["sentiment"] = news_df["sentiment"].round(3)
    news_df["sentiment_score"] = news_df["sentiment_score"].round(3)

    # Ensure datetime format
    if "datetime" in news_df.columns:
        news_df["datetime"] = pd.to_datetime(news_df["datetime"], errors="coerce")

    def matches_keywords(text, keywords):
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

    def classify_row(row):
        title = row["title"]
        sentiment = row["sentiment_score"]

        if matches_keywords(title, ECONOMIC_EVENT_KEYWORDS):
            return "MACRO_EVENT"
        elif sentiment >= 0.5 or matches_keywords(title, POSITIVE_KEYWORDS):
            return "BULLISH"
        elif sentiment <= -0.5 or matches_keywords(title, NEGATIVE_KEYWORDS):
            return "BEARISH"
        return None

    news_df["category"] = news_df.apply(classify_row, axis=1)

    filtered_df = news_df[news_df["category"].notnull()].copy()

    log.info(f"Total headlines: {len(news_df)}")
    log.info(f"Market-moving headlines kept: {len(filtered_df)}")

    with pd.option_context("display.max_rows", None,
                           "display.max_columns", None,
                           "display.width", 120,
                           "display.colheader_justify", "center"):
        log.info("\nFiltered Market-Moving News:")
        log.info(filtered_df[["datetime", "category", "sentiment_score", "title"]].to_string(index=False))

    return filtered_df
