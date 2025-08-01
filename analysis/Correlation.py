import pandas as pd

def correlate_sentiment_with_price(news_df, price_df):
    # Reset index if needed
    if isinstance(news_df.index, (pd.MultiIndex, pd.DatetimeIndex)):
        news_df = news_df.reset_index()
    if isinstance(price_df.index, (pd.MultiIndex, pd.DatetimeIndex)):
        price_df = price_df.reset_index()

    # Normalize column names
    for df in [news_df, price_df]:
        if "Datetime" in df.columns:
            df.rename(columns={"Datetime": "datetime"}, inplace=True)
        if "Date" in df.columns:
            df.rename(columns={"Date": "datetime"}, inplace=True)

    # Convert datetime and remove timezone if present
    def to_naive_datetime(series):
        dt = pd.to_datetime(series, errors="coerce")
        if hasattr(dt.dt, "tz_localize"):
            try:
                dt = dt.dt.tz_convert(None)  # Remove timezone if it exists
            except TypeError:
                pass
        return dt

    news_df["datetime"] = to_naive_datetime(news_df["datetime"])
    price_df["datetime"] = to_naive_datetime(price_df["datetime"])

    # Keep only relevant columns
    news_df = news_df[["datetime", "sentiment"]]
    price_df = price_df[["datetime", "close"]]

    # Drop rows with missing datetime
    news_df.dropna(subset=["datetime"], inplace=True)
    price_df.dropna(subset=["datetime"], inplace=True)

    # Sort by datetime
    news_df = news_df.sort_values("datetime")
    price_df = price_df.sort_values("datetime")

    # Merge on datetime (within 30 min)
    merged = pd.merge_asof(
        news_df,
        price_df,
        on="datetime",
        tolerance=pd.Timedelta("30m"),
        direction="backward"
    )

    # Round numbers for clean display
    merged["sentiment"] = merged["sentiment"].round(3)
    merged["close"] = merged["close"].round(2)

    # Format datetime for neat printing
    merged["datetime"] = merged["datetime"].dt.strftime("%Y-%m-%d %H:%M")

    # Calculate correlation
    if merged["sentiment"].notna().sum() > 1 and merged["close"].notna().sum() > 1:
        corr = merged["sentiment"].corr(merged["close"])
    else:
        corr = None

    # Nicely print with spacing
    with pd.option_context(
        "display.max_rows", None,
        "display.max_columns", None,
        "display.width", 120,
        "display.colheader_justify", "center"
    ):
        print(merged.to_string(index=False))

    return corr, merged
