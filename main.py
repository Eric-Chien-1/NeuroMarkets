import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

from scrapers.NewsScraper import NewsScraper
from scrapers.PriceScrapers import PriceScraper
from analysis.Sentiment import analyze_sentiment
from analysis.Correlation import correlate_sentiment_with_price


def main():
    API_KEY = "815b8274e8f94a5db950c060865bb3db"  # Replace with your NewsAPI key
    DAYS = 30
    CORR_HISTORY_FILE = "data/historical_correlations.csv"

    # 1️⃣ Fetch historical news
    print(f"[INFO] Fetching last {DAYS} days of news...")
    ns = NewsScraper(api_key=API_KEY, query="stock market")
    news_df = ns.scrape_news(days=DAYS)

    if news_df.empty:
        print("[WARN] No news found.")
        return

    print(f"[INFO] {len(news_df)} headlines found.")
    print("[INFO] Analyzing sentiment...")
    news_df = analyze_sentiment(news_df)

    # 2️⃣ Fetch historical prices
    print("[INFO] Fetching historical market price data...")
    ps = PriceScraper(ticker="ES=F")  # S&P 500 futures
    price_df = ps.get_historical_data(days=DAYS)

    if price_df.empty:
        print("[WARN] No price data found.")
        return

    # 3️⃣ Calculate correlation
    print("[INFO] Calculating correlation...")
    corr, merged_df = correlate_sentiment_with_price(news_df, price_df)
    print(f"[RESULT] Sentiment-Price Correlation: {corr}")

    # 4️⃣ Save merged daily results
    os.makedirs("data", exist_ok=True)
    merged_df.to_csv("data/correlation_results.csv", index=False)
    print("[INFO] Full correlation dataset saved to data/correlation_results.csv")

    # 5️⃣ Append correlation history (store as datetime64)
    today = pd.Timestamp.now().normalize()  # keeps datetime64 format
    corr_entry = pd.DataFrame([{"date": today, "correlation": corr}])

    if os.path.exists(CORR_HISTORY_FILE):
        hist_df = pd.read_csv(CORR_HISTORY_FILE, parse_dates=["date"])
        hist_df = pd.concat([hist_df, corr_entry], ignore_index=True)
    else:
        hist_df = corr_entry

    hist_df.drop_duplicates(subset=["date"], keep="last", inplace=True)
    hist_df.to_csv(CORR_HISTORY_FILE, index=False)
    print("[INFO] Correlation history updated.")

    # 6️⃣ Plot price vs sentiment
    plot_price_sentiment(merged_df)

    # 7️⃣ Plot correlation history trend
    plot_correlation_history(hist_df)


def plot_price_sentiment(merged_df):
    if "sentiment_score" not in merged_df.columns:
        if "sentiment" in merged_df.columns:
            merged_df["sentiment_score"] = merged_df["sentiment"]
        else:
            raise ValueError("No sentiment column available for plotting.")

    plt.figure(figsize=(10, 5))
    plt.plot(merged_df["datetime"], merged_df["close"], label="Price (Close)", color="blue")
    plt.plot(merged_df["datetime"], merged_df["sentiment_score"], label="Sentiment Score", color="orange")
    plt.legend()
    plt.show()


def plot_correlation_history(hist_df):
    """
    Plots the historical correlation trend over time.
    """
    # Ensure proper datetime type
    hist_df["date"] = pd.to_datetime(hist_df["date"], errors="coerce")

    plt.figure(figsize=(10, 5))
    plt.plot(hist_df["date"], hist_df["correlation"], marker="o", linestyle="-", color="purple")
    plt.axhline(0, color="gray", linestyle="--", linewidth=1)
    plt.title("Sentiment-Price Correlation Over Time")
    plt.xlabel("Date")
    plt.ylabel("Correlation")
    plt.grid(True)
    plt.tight_layout()

    os.makedirs("charts", exist_ok=True)
    chart_path = "charts/correlation_history.png"
    plt.savefig(chart_path)
    print(f"[INFO] Correlation history chart saved to {chart_path}")
    plt.close()


if __name__ == "__main__":
    main()
