import pandas as pd

def correlate_sentiment_with_price(news_df, price_df):
    if isinstance(news_df.index, (pd.MultiIndex, pd.DatetimeIndex)):
        news_df = news_df.reset_index()
    if isinstance(price_df.index, (pd.MultiIndex, pd.DatetimeIndex)):
        price_df = price_df.reset_index()

    for df in [news_df, price_df]:
        if "Datetime" in df.columns:
            df.rename(columns={"Datetime": "datetime"}, inplace=True)
        if "Date" in df.columns:
            df.rename(columns={"Date": "datetime"}, inplace=True)

    news_df["datetime"] = pd.to_datetime(news_df["datetime"], errors="coerce")
    price_df["datetime"] = pd.to_datetime(price_df["datetime"], errors="coerce")

    news_df = news_df[["datetime", "sentiment"]]
    price_df = price_df[["datetime", "close"]]

    news_df.dropna(subset=["datetime"], inplace=True)
    price_df.dropna(subset=["datetime"], inplace=True)

    news_df = news_df.sort_values("datetime")
    price_df = price_df.sort_values("datetime")

    merged = pd.merge_asof(
        news_df,
        price_df,
        on="datetime",
        tolerance=pd.Timedelta("30m"),
        direction="backward"
    )

    if merged["sentiment"].notna().sum() > 1 and merged["close"].notna().sum() > 1:
        corr = merged["sentiment"].corr(merged["close"])
    else:
        corr = None

    return corr, merged
