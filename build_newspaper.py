import feedparser
import yfinance as yf
from datetime import datetime

# 1. Fetch Market Data (Nifty 50 & Sensex)
tickers = {"Nifty 50": "^NSEI", "Sensex": "^BSESN"}
market_html = ""
for name, symbol in tickers.items():
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if len(hist) >= 2:
            prev = hist['Close'].iloc[-2]
            curr = hist['Close'].iloc[-1]
            pct = ((curr - prev) / prev) * 100
            color = "#16a34a" if pct >= 0 else "#dc2626"
            sign = "+" if pct >= 0 else ""
            market_html += f"<div class='market-item'><strong>{name}</strong>: {curr:.2f} <span style='color:{color}'>({sign}{pct:.2f}%)</span></div>"
    except Exception:
        market_html += f"<div class='market-item'><strong>{name}</strong>: Data unavailable</div>"

# 2. Fetch Business News (Google News India RSS)
feed_url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en"
feed = feedparser.parse(feed_url)
news_html = ""
for entry in feed.entries[:10]:
    # Clean up the date string slightly
    pub_date = entry.published.replace("GMT", "")
    news_html += f"""
    <div class='article'>
        <h3><a href='{entry.link}' target='_blank'>{entry.title}</a></h3>
        <p class='meta'><em>{pub_date}</em></p>
    </div>
    """

# 3. Generate the HTML Newspaper Template
today = datetime.now().strftime("%A, %B %d, %Y")
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Daily Briefing</title>
    <style>
        body {{ font-family: 'Georgia', serif; background-color: #f4f1ea; color: #333; margin: 0; padding: 20px; }}
        .newspaper {{ max-width: 800px; margin: auto; background: white; padding: 40px; box-shadow: 0 0 15px rgba(0,0,0,0.1); border-top: 6px solid #111; }}
        h1 {{ font-size: 3em; text-align: center; text-transform: uppercase; border-bottom: 2px solid #111; margin-bottom: 10px; padding-bottom: 10px; letter-spacing: 2px; }}
        .date {{ font-style: italic; text-align: center; border-bottom: 1px solid #ccc; padding-bottom: 20px; margin-bottom: 30px; color: #555; }}
        h2 {{ text-transform: uppercase; border-bottom: 1px solid #eee; padding-bottom: 5px; font-size: 1.5em; }}
        .market-section {{ display: flex; justify-content: space-around; flex-wrap: wrap; background: #faf9f6; padding: 15px; border: 1px solid #e5e5e5; margin-bottom: 30px; font-size: 1.2em; }}
        .article {{ margin-bottom: 25px; }}
        .article h3 {{ margin: 0 0 8px 0; font-size: 1.4em; line-height: 1.3; }}
        .article a {{ color: #111; text-decoration: none; }}
        .article a:hover {{ text-decoration: underline; color: #1a0dab; }}
        .meta {{ margin: 0; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="newspaper">
        <h1>The Daily Briefing</h1>
        <div class="date">{today}</div>
        
        <h2>Market Snapshot</h2>
        <div class="market-section">
            {market_html}
        </div>
        
        <h2>Top Headlines</h2>
        <div class="news-section">
            {news_html}
        </div>
    </div>
</body>
</html>
"""

# 4. Save the HTML file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
