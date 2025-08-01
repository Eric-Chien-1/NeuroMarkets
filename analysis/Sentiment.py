import pandas as pd
from textblob import TextBlob

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

    # Round scores for cleaner display
    news_df["sentiment"] = news_df["sentiment"].round(3)
    news_df["sentiment_score"] = news_df["sentiment_score"].round(3)

    # Format datetime if exists
    if "datetime" in news_df.columns:
        news_df["datetime"] = pd.to_datetime(news_df["datetime"]).dt.strftime("%Y-%m-%d %H:%M")

    # Print nicely with spacing
    with pd.option_context("display.max_rows", None,
                           "display.max_columns", None,
                           "display.width", 120,
                           "display.colheader_justify", "center"):
        print(news_df.to_string(index=False))

    return news_df
