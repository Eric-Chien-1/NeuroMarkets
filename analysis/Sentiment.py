import pandas as pd
from textblob import TextBlob
from logger import log  # <-- shared logger

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
    scores = [TextBlob(str(t)).sentiment.polarity for t in news_df["title"].fillna("")]
    news_df["sentiment"] = pd.Series(scores).round(3)
    news_df["sentiment_score"] = news_df["sentiment"]

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

    # Summary logging
    log.info(f"Total headlines: {len(news_df)}")
    log.info(f"Market-moving headlines kept: {len(filtered_df)}")

    # Format datetime for clean display
    filtered_df["datetime"] = filtered_df["datetime"].dt.strftime("%Y-%m-%d %H:%M")

    # Auto-adjust spacing
    col_widths = {
        "datetime": max(filtered_df["datetime"].str.len().max(), len("datetime")),
        "category": max(filtered_df["category"].str.len().max(), len("category")),
        "sentiment_score": max(filtered_df["sentiment_score"].astype(str).str.len().max(), len("sentiment_score")),
    }

    # Build aligned string
    lines = []
    header = f"{'datetime'.ljust(col_widths['datetime'])}  " \
             f"{'category'.ljust(col_widths['category'])}  " \
             f"{'sentiment_score'.ljust(col_widths['sentiment_score'])}  title"
    lines.append(header)

    for _, row in filtered_df.iterrows():
        lines.append(
            f"{str(row['datetime']).ljust(col_widths['datetime'])}  "
            f"{str(row['category']).ljust(col_widths['category'])}  "
            f"{str(row['sentiment_score']).ljust(col_widths['sentiment_score'])}  "
            f"{row['title']}"
        )

    # Log the table
    log.info("\nFiltered Market-Moving News:\n%s", "\n".join(lines))

    return filtered_df
