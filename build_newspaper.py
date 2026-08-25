import feedparser
import yfinance as yf
from datetime import datetime
import urllib.parse

# 1. Fetch Market Data & Foreign Indices
tickers = {
    "Reliance": "RELIANCE.NS",
    "Blue Clouds": "BLUECLOUDS.NS", 
    "Gold BeES": "GOLDBEES.NS",
    "Nifty BeES": "NIFTYBEES.NS",
    "Patel Eng": "PATELENG.NS",
    "RBA": "RBA.NS",
    "REC Ltd": "RECLTD.NS",
    "Junior BeES": "JUNIORBEES.NS",
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "FTSE 100": "^FTSE",
    "Nikkei 225": "^N225"
}

market_rows = ""
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
            
            market_rows += f"""
            <tr>
                <td class='ticker-name'>{name}</td>
                <td class='price'>{curr:.2f}</td>
                <td class='change' style='color:{color}'>{sign}{pct:.2f}%</td>
            </tr>
            """
    except Exception:
        market_rows += f"<tr><td class='ticker-name'>{name}</td><td colspan='2' class='price'>N/A</td></tr>"

# 2. Helper function to fetch news as a list
def get_news_data(query, max_items=6):
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:max_items]:
        pub_date = entry.published.replace("GMT", "")
        publisher = getattr(entry, 'source', {}).get('title', 'Financial News')
        clean_title = entry.title.rsplit(" - ", 1)[0]
        articles.append({
            "title": clean_title,
            "publisher": publisher,
            "date": pub_date,
            "link": entry.link
        })
    return articles

def render_articles(articles):
    html = ""
    for art in articles:
        html += f"""
        <div class='article'>
            <h3><a href='{art["link"]}' target='_blank'>{art["title"]}</a></h3>
            <p class='meta'><strong>{art["publisher"]}</strong> | {art["date"]}</p>
        </div>
        """
    return html

# 3. Create a filter for your preferred publishers
publishers = "(site:livemint.com OR site:moneycontrol.com OR site:bloomberg.com OR site:timesofindia.indiatimes.com OR site:zerodha.com)"

invest_query = f"(Reliance Industries OR Blue Cloud Softech OR Gold BeES OR Nifty OR Patel Engineering OR Restaurant Brands Asia OR REC Ltd OR HDFC Nifty) AND {publishers}"
ai_query = f'("Artificial Intelligence" OR AI OR OpenAI) AND {publishers}'
ma_query = f'("Mergers and Acquisitions" OR M&A OR "Private Equity") AND {publishers}'
cfa_iim_query = f"(CFA OR 'Chartered Financial Analyst' OR IIM OR 'Indian Institute of Management') AND {publishers}"

# Fetch Data
invest_data = get_news_data(invest_query, 5)
ma_data = get_news_data(ma_query, 4)
ai_data = get_news_data(ai_query, 4)
edu_data = get_news_data(cfa_iim_query, 4)

# Separate the first article to act as the massive "Lead Story"
lead_story = invest_data[0] if invest_data else {"title": "No Lead Story Found", "publisher": "", "date": "", "link": "#"}
sub_invest_data = invest_data[1:] if len(invest_data) > 1 else []

# Render HTML for sub-grids
html_invest = render_articles(sub_invest_data)
html_ma = render_articles(ma_data)
html_ai = render_articles(ai_data)
html_edu = render_articles(edu_data)

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
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');
        
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Lora', serif; 
            background-color: #fcfcfc; 
            color: #111; 
            margin: 0; 
            padding: 20px; 
        }}
        .newspaper-container {{ 
            max-width: 1200px; 
            margin: auto; 
            background: #fff; 
            padding: 40px; 
        }}
        .masthead {{
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
            margin-bottom: 5px;
        }}
        .masthead h1 {{ 
            font-family: 'Playfair Display', serif; 
            font-size: 5em; 
            font-weight: 900;
            text-transform: uppercase; 
            margin: 0; 
            letter-spacing: 2px; 
        }}
        .date-bar {{ 
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #000; 
            padding: 5px 0; 
            margin-bottom: 10px; 
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .nav-bar {{
            text-align: center;
            border-bottom: 4px solid #000;
            padding-bottom: 10px;
            margin-bottom: 30px;
            font-size: 0.9em;
            font-weight: bold;
            word-spacing: 15px;
        }}
        
        .layout-wrapper {{
            display: flex;
            gap: 40px;
        }}
        .main-content {{
            flex: 7; /* 70% width for news */
        }}
        .sidebar {{
            flex: 3; /* 30% width for market data */
            border-left: 1px solid #ddd;
            padding-left: 30px;
        }}
        
        /* Lead Story */
        .lead-story {{
            border-bottom: 2px solid #000;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .lead-story h2 a {{
            font-family: 'Playfair Display', serif;
            font-size: 2.8em;
            font-weight: 900;
            line-height: 1.1;
            margin: 0 0 10px 0;
            color: #000;
            text-decoration: none;
        }}
        .lead-story h2 a:hover {{ text-decoration: underline; }}
        
        /* Article Grids */
        h4.section-title {{
            font-family: 'Playfair Display', serif;
            text-transform: uppercase;
            border-bottom: 1px solid #000;
            padding-bottom: 5px;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
        }}
        .article h3 {{ 
            font-family: 'Playfair Display', serif;
            margin: 0 0 8px 0; 
            font-size: 1.2em; 
            line-height: 1.3; 
        }}
        .article h3 a {{ color: #111; text-decoration: none; }}
        .article h3 a:hover {{ text-decoration: underline; }}
        
        .meta {{ 
            margin: 0; 
            font-size: 0.8em; 
            color: #555; 
            text-transform: uppercase;
        }}
        .meta strong {{ color: #000; }}
        
        /* Sidebar Market Watch */
        .market-header {{
            font-family: 'Playfair Display', serif;
            font-size: 1.3em;
            font-weight: 900;
            text-transform: uppercase;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .market-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .market-table th, .market-table td {{
            padding: 10px 0;
            border-bottom: 1px solid #eee;
            font-size: 0.95em;
        }}
        .market-table th {{
            text-align: left;
            text-transform: uppercase;
            color: #777;
            font-size: 0.8em;
        }}
        .market-table .price, .market-table .change {{ text-align: right; }}
        .ticker-name {{ font-weight: 600; }}
        
        @media (max-width: 900px) {{
            .layout-wrapper {{ flex-direction: column; }}
            .sidebar {{ border-left: none; padding-left: 0; border-top: 2px solid #000; padding-top: 30px; }}
            .articles-grid {{ grid-template-columns: 1fr; }}
            .masthead h1 {{ font-size: 3.5em; }}
        }}
    </style>
</head>
<body>
    <div class="newspaper-container">
        
        <!-- Header Section -->
        <div class="masthead">
            <h1>The Daily Briefing</h1>
        </div>
        <div class="date-bar">
            <span>Vol. 1 — Automated Edition</span>
            <span>{today}</span>
        </div>
        <div class="nav-bar">
            PORTFOLIO &nbsp; • &nbsp; MARKETS &nbsp; • &nbsp; M&A &nbsp; • &nbsp; ARTIFICIAL INTELLIGENCE &nbsp; • &nbsp; CFA & IIM
        </div>
        
        <!-- Main Content & Sidebar -->
        <div class="layout-wrapper">
            
            <!-- Left Side: News -->
            <div class="main-content">
                
                <div class="lead-story">
                    <p class="meta"><strong>{lead_story["publisher"]}</strong> | {lead_story["date"]}</p>
                    <h2><a href="{lead_story["link"]}" target="_blank">{lead_story["title"]}</a></h2>
                </div>
                
                <div class="articles-grid">
                    {html_invest}
                </div>
                
                <h4 class="section-title">Mergers & Acquisitions</h4>
                <div class="articles-grid">
                    {html_ma}
                </div>
                
                <h4 class="section-title">AI & Innovation</h4>
                <div class="articles-grid">
                    {html_ai}
                </div>
                
                <h4 class="section-title">CFA & IIM Updates</h4>
                <div class="articles-grid">
                    {html_edu}
                </div>
                
            </div>
            
            <!-- Right Side: Market Watch Table -->
            <div class="sidebar">
                <div class="market-header">Market Watch</div>
                <table class="market-table">
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th class="price">Price</th>
                            <th class="change">Change</th>
                        </tr>
                    </thead>
                    <tbody>
                        {market_rows}
                    </tbody>
                </table>
            </div>
            
        </div>
    </div>
</body>
</html>
"""

# 5. Save the HTML file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
