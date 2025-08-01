import os
import pandas as pd
import matplotlib.pyplot as plt
import logging
from scrapers.NewsScraper import NewsScraper
from scrapers.PriceScrapers import PriceScraper
from analysis.Sentiment import analyze_sentiment
from analysis.Correlation import correlate_sentiment_with_price

# Configure logger
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# Tickers for major index futures
INDEX_TICKERS = {
    "S&P 500": "ES=F",
    "NASDAQ 100": "NQ=F",
    "Dow Jones": "YM=F",
    "Russell 2000": "RTY=F"
}

def main():
    API_KEY = " "  # Replace with your NewsAPI key
    DAYS = 30
    CORR_HISTORY_DIR = "data/historical_correlations"
    CHARTS_DIR = "charts"

    os.makedirs("data", exist_ok=True)
    os.makedirs(CORR_HISTORY_DIR, exist_ok=True)
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # 1 Fetch and analyze news sentiment
    log.info(f"Fetching last {DAYS} days of news...")
    ns = NewsScraper(api_key=API_KEY, query="stock market")
    news_df = ns.scrape_news(days=DAYS)

    if news_df.empty:
        log.warning("No news found.")
        return

    log.info(f"{len(news_df)} headlines found.")
    log.info("Analyzing sentiment...")
    news_df = analyze_sentiment(news_df)

    # 2️ Fetch price data for all tickers
    ps = PriceScraper(list(INDEX_TICKERS.values()))
    price_data = ps.get_historical_data(days=DAYS)

    # 3️ Process each index separately
    for index_name, ticker in INDEX_TICKERS.items():
        if ticker not in price_data:
            log.warning(f"No price data for {index_name} ({ticker}), skipping.")
            continue

        log.info(f"Analyzing correlation for {index_name} ({ticker})...")
        price_df = price_data[ticker]

        # Merge and correlate
        corr, merged_df = correlate_sentiment_with_price(news_df, price_df)
        log.info(f"{index_name} Sentiment-Price Correlation: {corr}")

        # Save merged dataset
        merged_file = f"data/correlation_results_{ticker.replace('=','')}.csv"
        merged_df.to_csv(merged_file, index=False)
        log.info(f"Full correlation dataset saved to {merged_file}")

        # Append correlation history
        today = pd.Timestamp.now().normalize()
        hist_file = os.path.join(CORR_HISTORY_DIR, f"{ticker.replace('=','')}_history.csv")

        corr_entry = pd.DataFrame([{"date": today, "correlation": corr}])
        if os.path.exists(hist_file):
            hist_df = pd.read_csv(hist_file, parse_dates=["date"])
            hist_df = pd.concat([hist_df, corr_entry], ignore_index=True)
        else:
            hist_df = corr_entry

        hist_df.drop_duplicates(subset=["date"], keep="last", inplace=True)
        hist_df.to_csv(hist_file, index=False)
        log.info(f"Correlation history updated for {index_name}.")

        # Plot sentiment vs price for this index
        plot_price_sentiment(merged_df, index_name, ticker, CHARTS_DIR)

        # Plot correlation history for this index
        plot_correlation_history(hist_df, index_name, ticker, CHARTS_DIR)


def plot_price_sentiment(merged_df, index_name, ticker, charts_dir):
    """
    Plots sentiment score vs market price over time for a given index.
    """
    if "sentiment_score" not in merged_df.columns:
        if "sentiment" in merged_df.columns:
            merged_df["sentiment_score"] = merged_df["sentiment"]
        else:
            raise ValueError("No sentiment column available for plotting.")

    plt.figure(figsize=(10, 5))
    plt.plot(merged_df["datetime"], merged_df["close"], label="Price (Close)", color="blue")
    plt.plot(merged_df["datetime"], merged_df["sentiment_score"], label="Sentiment Score", color="orange")
    plt.title(f"{index_name} - Sentiment vs Price")
    plt.xlabel("Date/Time")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    chart_path = os.path.join(charts_dir, f"sentiment_price_{ticker.replace('=','')}.png")
    plt.savefig(chart_path)
    plt.close()
    log.info(f"Sentiment vs Price chart saved to {chart_path}")


def plot_correlation_history(hist_df, index_name, ticker, charts_dir):
    hist_df["date"] = pd.to_datetime(hist_df["date"], errors="coerce")

    plt.figure(figsize=(10, 5))
    plt.plot(hist_df["date"], hist_df["correlation"], marker="o", markersize=8, color="purple", linestyle="-")
    plt.axhline(0, color="gray", linestyle="--", linewidth=1)

    # Label last point
    if not hist_df.empty:
        last_row = hist_df.iloc[-1]
        plt.text(last_row["date"], last_row["correlation"], f"{last_row['correlation']:.3f}",
                 fontsize=10, color="purple", weight="bold", ha="left", va="bottom")

    plt.title(f"{index_name} - Sentiment-Price Correlation Over Time")
    plt.xlabel("Date")
    plt.ylabel("Correlation")
    plt.grid(True)

    # Limit x-axis range
    plt.xlim(hist_df["date"].min() - pd.Timedelta(days=5),
             hist_df["date"].max() + pd.Timedelta(days=5))

    plt.tight_layout()

    os.makedirs(charts_dir, exist_ok=True)
    chart_path = os.path.join(charts_dir, f"correlation_history_{ticker.replace('=','')}.png")
    plt.savefig(chart_path)
    plt.close()
    log.info(f"Correlation history chart saved to {chart_path}")


if __name__ == "__main__":
    main()
