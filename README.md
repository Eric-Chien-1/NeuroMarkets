# 📰 NeuroMarket
**Turning Headlines into Market Predictions**

---

## 📌 Overview
**NeuroMarket** is a Python-based tool that collects **historical financial news** and **correlates** it with **S&P 500** and **Nasdaq futures** price action.  
The goal is to uncover patterns between **media sentiment** and **market movement** to help traders make more informed decisions.

This is **Step 1** of a larger project to build an **AI-powered automated trading system**.

---

## 🎯 Core Idea
1. **Scrape** financial headlines from multiple sources (CNBC, Bloomberg, Yahoo Finance, MarketWatch, etc.).
2. **Store** news data in a structured format for analysis.
3. **Align** news timestamps with historical futures market data.
4. **Analyze** the correlation between sentiment and intraday price movement.

---

## 🚀 Features
- Pulls **headline**, **timestamp**, **source**
- Filters **pre-market news** (6:00 AM – 8:30 AM ET)
- Stores daily results in **CSV** format
- Ready for **sentiment analysis** integration
- Designed for **multi-year historical backtesting**

---

## 📂 Example Output
```csv
date,time,headline,sentiment,source
2025-07-31,06:05,"Fed minutes point to rate cut in September",,CNBC
2025-07-31,07:12,"CPI data shows slower inflation in July",,Bloomberg
2025-07-31,08:15,"Futures point to higher open as PPI cools",,Yahoo Finance
