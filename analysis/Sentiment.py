import pandas as pd
from textblob import TextBlob

def analyze_sentiment(news_df: pd.DataFrame) -> pd.DataFrame:
    if "title" not in news_df.columns:
        raise ValueError("News DataFrame must have a 'title' column for sentiment analysis.")

    scores = []
    for text in news_df["title"].fillna(""):
        score = TextBlob(str(text)).sentiment.polarity
        scores.append(score)

    news_df["sentiment"] = scores  # for correlation
    news_df["sentiment_score"] = scores  # for plotting

    return news_df
