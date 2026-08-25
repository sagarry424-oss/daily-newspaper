import feedparser
import yfinance as yf
from datetime import datetime
import urllib.parse

# 1. Fetch Market Data & Foreign Indices
tickers = {
    # Your Portfolio
    "Reliance": "RELIANCE.NS",
    "Blue Clouds": "BLUECLOUDS.NS", 
    "Gold BeES": "GOLDBEES.NS",
    "Nifty BeES": "NIFTYBEES.NS",
    "Patel Eng": "PATELENG.NS",
    "RBA": "RBA.NS",
    "REC Ltd": "RECLTD.NS",
    "Junior BeES": "JUNIORBEES.NS",
    # Foreign Markets
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "FTSE 100": "^FTSE",
    "Nikkei 225": "^N225"
}

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
            market_html += f"<div class='market-item'><strong>{name}</strong><br>{curr:.2f} <span style='color:{color}'>({sign}{pct:.2f}%)</span></div>"
    except Exception:
        market_html += f"<div class='market-item'><strong>{name}</strong><br>Data unavailable</div>"

# 2. Helper function to fetch and format news
def get_news_html(query, max_items=6):
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    html = ""
    for entry in feed.entries[:max_items]:
        pub_date = entry.published.replace("GMT", "")
        
        # Extract the publisher name (Google News usually appends it or includes it in the source tag)
        publisher = getattr(entry, 'source', {}).get('title', 'Financial News')
        
        # Clean up the title if Google appended the publisher name to it (e.g. "Headline - Moneycontrol")
        clean_title = entry.title.rsplit(" - ", 1)[0]
        
        html += f"""
        <div class='article'>
            <h3>{clean_title}</h3>
            <p class='meta'><strong>{publisher}</strong> | <em>{pub_date}</em></p>
            <p class='snippet'><a href='{entry.link}' target='_blank'>Read Full Story &raquo;</a></p>
        </div>
        """
    return html

# 3. Create a filter for your preferred publishers
publishers = "(site:livemint.com OR site:moneycontrol.com OR site:bloomberg.com OR site:timesofindia.indiatimes.com OR site:zerodha.com)"

# Attach the publishers filter to your custom queries
invest_query = f"(Reliance Industries OR Blue Cloud Softech OR Gold BeES OR Nifty OR Patel Engineering OR Restaurant Brands Asia OR REC Ltd OR HDFC Nifty) AND {publishers}"
ai_query = f'("Artificial Intelligence" OR AI OR OpenAI) AND {publishers}'
ma_query = f'("Mergers and Acquisitions" OR M&A OR "Private Equity") AND {publishers}'
cfa_iim_query = f"(CFA OR 'Chartered Financial Analyst' OR IIM OR 'Indian Institute of Management') AND {publishers}"

# Fetch News for specific custom sections
html_invest = get_news_html(invest_query, 6)
html_ma = get_news_html(ma_query, 4)
html_ai = get_news_html(ai_query, 4)
html_edu = get_news_html(cfa_iim_query, 4)

# 4. Generate Authentic Newspaper HTML
today = datetime.now().strftime("%A, %B %d, %Y")
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Daily Briefing</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');
        
        body {{ 
            font-family: 'Lora', serif; 
            background-color: #e9e6df; /* Vintage paper color */
            color: #1a1a1a; 
            margin: 0; 
            padding: 20px; 
        }}
        .newspaper-container {{ 
            max-width: 1100px; 
            margin: auto; 
            background: #f4f1ea; 
            padding: 40px; 
            box-shadow: 0 0 20px rgba(0,0,0,0.15); 
        }}
        .masthead {{
            text-align: center;
            border-bottom: 4px solid #111;
            border-top: 4px solid #111;
            padding: 20px 0;
            margin-bottom: 20px;
        }}
        .masthead h1 {{ 
            font-family: 'Playfair Display', serif; 
            font-size: 4.5em; 
            text-transform: uppercase; 
            margin: 0; 
            letter-spacing: 2px; 
        }}
        .date-bar {{ 
            font-style: italic; 
            text-align: center; 
            border-bottom: 2px solid #111; 
            padding-bottom: 10px; 
            margin-bottom: 30px; 
            font-size: 1.1em;
        }}
        h2.section-header {{ 
            font-family: 'Playfair Display', serif;
            text-transform: uppercase; 
            border-bottom: 2px solid #333; 
            border-top: 2px solid #333;
            padding: 5px 0; 
            font-size: 1.5em; 
            text-align: center;
            background-color: #ece8df;
            margin-top: 40px;
        }}
        .market-ticker {{ 
            display: flex; 
            justify-content: center; 
            flex-wrap: wrap; 
            gap: 15px;
            margin-bottom: 30px; 
            font-size: 1.1em; 
            border: 1px solid #ccc;
            padding: 15px;
            background: #fffdf5;
        }}
        .market-item {{
            padding: 5px 15px;
            border-right: 1px solid #ccc;
            text-align: center;
        }}
        .market-item:last-child {{ border-right: none; }}
        
        .columns {{
            column-count: 3;
            column-gap: 30px;
            column-rule: 1px solid #ccc;
        }}
        .columns-2 {{
            column-count: 2;
            column-gap: 30px;
            column-rule: 1px solid #ccc;
        }}
        .article {{ 
            margin-bottom: 25px; 
            break-inside: avoid; /* Prevents text from splitting awkwardly across columns */
        }}
        .article h3 {{ 
            font-family: 'Playfair Display', serif;
            margin: 0 0 8px 0; 
            font-size: 1.3em; 
            line-height: 1.2; 
        }}
        .meta {{ 
            margin: 0 0 8px 0; 
            font-size: 0.85em; 
            color: #555; 
            text-transform: uppercase;
        }}
        .meta strong {{
            color: #b30000; /* Dark red for the publisher name to make it pop */
        }}
        .snippet a {{ 
            color: #111; 
            font-weight: bold;
            text-decoration: none; 
            border-bottom: 1px dotted #111;
        }}
        .snippet a:hover {{ color: #0056b3; border-bottom: 1px solid #0056b3; }}
        
        @media (max-width: 768px) {{
            .columns, .columns-2 {{ column-count: 1; }}
            .masthead h1 {{ font-size: 2.5em; }}
        }}
    </style>
</head>
<body>
    <div class="newspaper-container">
        <div class="masthead">
            <h1>The Daily Briefing</h1>
        </div>
        <div class="date-bar">Published on {today} | Automated Edition</div>
        
        <h2 class="section-header">Global & Portfolio Markets</h2>
        <div class="market-ticker">
            {market_html}
        </div>
        
        <h2 class="section-header">Portfolio & Equity News</h2>
        <div class="columns">
            {html_invest}
        </div>

        <h2 class="section-header">Mergers, Acquisitions & Private Equity</h2>
        <div class="columns-2">
            {html_ma}
        </div>
        
        <h2 class="section-header">Artificial Intelligence & Innovation</h2>
        <div class="columns-2">
            {html_ai}
        </div>
        
        <h2 class="section-header">CFA & IIM Updates</h2>
        <div class="columns-2">
            {html_edu}
        </div>
    </div>
</body>
</html>
"""

# 5. Save the HTML file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
