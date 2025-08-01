# 🧠 SentimentMarketAnalysis — News & Price Action Correlation

SentimentMarketAnalysis is a Python-based research tool that correlates **financial news sentiment** with **market price action** (e.g., S&P 500 futures) in near real-time.

It:
- Scrapes the latest stock market news
- Analyzes sentiment (positive, neutral, negative)
- Fetches intraday price data for a chosen ticker
- Correlates sentiment scores with price movements
- Saves all results for research & strategy development

---

## 📌 Features

- **News Scraping** — Pulls real-time headlines from Yahoo Finance.
- **Sentiment Analysis** — Uses NLP to determine positive, neutral, or negative sentiment.
- **Market Data** — Fetches intraday market price data from Yahoo Finance via `yfinance`.
- **Correlation Analysis** — Merges and calculates correlation between sentiment and price movement.
- **Debug Data Saving** — Saves raw and processed datasets for transparency.

---

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/NeuroMarkets.git
cd NeuroMarkets
2️⃣ Install dependencies
Make sure you’re using Python 3.8+.

bash
Copy
Edit
pip install -r requirements.txt
Typical dependencies:

text
Copy
Edit
pandas
numpy
yfinance
beautifulsoup4
requests
textblob
3️⃣ Run the script
bash
Copy
Edit
python main.py
📂 Project Structure
bash
Copy
Edit
NeuroMarkets/
│
├── main.py                        # Main entry point
├── scrapers/
│   ├── NewsScraper.py             # Yahoo Finance news scraper
│   ├── PriceScrapers.py           # Yahoo Finance price scraper
│
├── analysis/
│   ├── Sentiment.py               # Sentiment analysis functions
│   ├── Correlation.py             # Correlation calculation
│
├── data/                          # Output data files
│   ├── news_raw.csv
│   ├── news_with_sentiment.csv
│   ├── price_raw.csv
│   ├── correlation_results.csv
│
├── requirements.txt
└── README.md
📊 Output Files
After running main.py, the following files will be created in the data/ folder:

File	Description
news_raw.csv	Raw scraped headlines + timestamps
news_with_sentiment.csv	Headlines + timestamps + sentiment score
price_raw.csv	Intraday market data for chosen ticker
correlation_results.csv	Merged dataset with sentiment + price movement + calculated correlation

⚙️ How It Works
Scrape News
Pulls latest market news from Yahoo Finance.

Analyze Sentiment
Classifies each headline as positive, negative, or neutral.

Fetch Price Data
Downloads intraday OHLCV data from Yahoo Finance.

Merge & Correlate
Matches news to price data within a 30-minute window, then calculates correlation.

📈 Example Output
text
Copy
Edit
[INFO] Fetching news...
[INFO] Retrieved 35 news articles.
[INFO] Analyzing sentiment...
[INFO] Fetching market price data...
[INFO] Retrieved 78 price records.
[INFO] Calculating correlation...
[RESULT] Sentiment-Price Correlation: 0.3421
[INFO] Results saved to data/correlation_results.csv
🔮 Future Enhancements
Add multiple news sources (Bloomberg, Reuters, etc.)

Expand sentiment model using transformer-based NLP (e.g., BERT)

Backtest strategies using historical data

Real-time dashboard visualization
