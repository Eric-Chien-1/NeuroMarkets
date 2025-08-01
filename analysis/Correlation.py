import os
import logging
import pandas as pd

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logger (shared config)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

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

    # Format datetime for neat display
    merged["datetime"] = merged["datetime"].dt.strftime("%Y-%m-%d %H:%M")

       # Calculate correlation
    if merged["sentiment"].notna().sum() > 1 and merged["close"].notna().sum() > 1:
        corr = merged["sentiment"].corr(merged["close"])
    else:
        corr = None

    log.info("Merged sentiment & price data preview:\n%s", merged.to_string(index=False))

    if corr is not None:
        # Convert to percentage for non-technical users
        strength_percent = abs(corr) * 100
        direction = "positive" if corr > 0 else "negative"
        log.info("Calculated correlation: %.6f", corr)
        log.info("Correlation strength: %.1f%% (%s)", strength_percent, direction)
    else:
        log.info("Calculated correlation: N/A")


    log.info("Merged sentiment & price data preview:\n%s", merged.to_string(index=False))
    log.info("Calculated correlation: %s", corr if corr is not None else "N/A")

    return corr, merged
