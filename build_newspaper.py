import os
import feedparser
import requests
import yfinance as yf
from datetime import datetime
import urllib.parse

# Loads a local .env file if present (for testing on your own machine).
# In GitHub Actions there is no .env file, so this line just does nothing there —
# the key comes from the environment variable set in the workflow instead.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

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

TRUSTED_PUBLISHERS = [
    "livemint.com", "moneycontrol.com", "bloomberg.com",
    "timesofindia.indiatimes.com", "zerodha.com", "economictimes.indiatimes.com",
    "business-standard.com", "reuters.com"
]


def get_google_news(query, max_items=6):
    """Fetch recent articles from Google News RSS. when:2d keeps results fresh."""
    full_query = f"{query} when:2d"
    encoded_query = urllib.parse.quote(full_query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        clean_title = entry.title.rsplit(" - ", 1)[0].strip()
        publisher = getattr(entry, "source", {}).get("title", "Financial News")
        pub_date = getattr(entry, "published", "").replace("GMT", "").strip()
        articles.append({
            "title": clean_title,
            "publisher": publisher,
            "date": pub_date,
            "link": entry.link,
            "is_trusted": any(dom in entry.link for dom in TRUSTED_PUBLISHERS),
        })
    return articles


def get_newsapi_news(query, max_items=6):
    """
    Fetch recent articles from NewsAPI's /v2/everything endpoint.
    Returns an empty list (not an error) if the key is missing or the
    request fails, so the page still builds using Google News alone.
    """
    if not NEWS_API_KEY:
        return []

    try:
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "apiKey": NEWS_API_KEY,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": max_items,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"NewsAPI request failed for query '{query}': {e}")
        return []

    articles = []
    for item in data.get("articles", []):
        title = (item.get("title") or "").rsplit(" - ", 1)[0].strip()
        if not title:
            continue
        link = item.get("url", "#")
        publisher = item.get("source", {}).get("name", "Financial News")
        # NewsAPI dates look like 2026-08-27T05:12:00Z — trim to something readable
        raw_date = item.get("publishedAt", "")
        pub_date = raw_date.replace("T", " ").replace("Z", "") if raw_date else ""
        articles.append({
            "title": title,
            "publisher": publisher,
            "date": pub_date,
            "link": link,
            "is_trusted": any(dom in link for dom in TRUSTED_PUBLISHERS),
        })
    return articles


def get_news_data(query, max_items=6):
    """
    Merge NewsAPI + Google News results for one topic, deduplicate by
    title, prioritize trusted publishers, and cap to max_items.
    """
    combined = get_newsapi_news(query, max_items) + get_google_news(query, max_items)

    seen_titles = set()
    deduped = []
    for art in combined:
        key = art["title"].lower()
        if key in seen_titles or not art["title"]:
            continue
        seen_titles.add(key)
        deduped.append(art)

    deduped.sort(key=lambda a: not a["is_trusted"])
    return deduped[:max_items]


def render_articles(articles):
    if not articles:
        return "<p class='no-articles'>No fresh coverage in the last two days.</p>"

    html = ""
    for art in articles:
        html += f"""
        <div class='article'>
            <h3><a href='{art["link"]}' target='_blank'>{art["title"]}</a></h3>
            <p class='meta'><strong>{art["publisher"]}</strong> | {art["date"]}</p>
        </div>
        """
    return html


# 2. Build each section
invest_query = "Reliance Industries OR Nifty OR Gold BeES OR Patel Engineering OR REC Ltd OR HDFC Nifty"
ma_query = "Mergers and Acquisitions OR Private Equity India"
ai_query = "Artificial Intelligence OR OpenAI OR AI regulation"
cfa_iim_query = "CFA Institute OR IIM Calcutta OR Chartered Financial Analyst"

invest_data = get_news_data(invest_query, 6)
ma_data = get_news_data(ma_query, 4)
ai_data = get_news_data(ai_query, 4)
edu_data = get_news_data(cfa_iim_query, 4)

lead_story = invest_data[0] if invest_data else {
    "title": "No fresh lead story found today — check back after the next update.",
    "publisher": "", "date": "", "link": "#"
}
sub_invest_data = invest_data[1:] if len(invest_data) > 1 else []

html_invest = render_articles(sub_invest_data)
html_ma = render_articles(ma_data)
html_ai = render_articles(ai_data)
html_edu = render_articles(edu_data)

# 3. Generate Authentic Newspaper HTML
today = datetime.now().strftime("%A, %B %d, %Y")
generated_at = datetime.now().strftime("%I:%M %p")

html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Daily Briefing</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Lora:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">

    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Lora', Georgia, serif;
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
            font-family: 'Playfair Display', Georgia, serif;
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
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
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

        .layout-wrapper {{ display: flex; gap: 40px; }}
        .main-content {{ flex: 7; }}
        .sidebar {{ flex: 3; border-left: 1px solid #ddd; padding-left: 30px; }}

        .lead-story {{
            border-bottom: 2px solid #000;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .lead-story h2 a {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 2.8em;
            font-weight: 900;
            line-height: 1.1;
            margin: 0 0 10px 0;
            color: #000;
            text-decoration: none;
        }}
        .lead-story h2 a:hover {{ text-decoration: underline; }}

        h4.section-title {{
            font-family: 'Playfair Display', Georgia, serif;
            text-transform: uppercase;
            border-bottom: 1px solid #000;
            padding-bottom: 5px;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.2em;
            letter-spacing: 0.5px;
        }}
        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
        }}
        .article h3 {{
            font-family: 'Playfair Display', Georgia, serif;
            margin: 0 0 8px 0;
            font-size: 1.2em;
            line-height: 1.3;
        }}
        .article h3 a {{ color: #111; text-decoration: none; }}
        .article h3 a:hover {{ text-decoration: underline; }}
        .no-articles {{ font-style: italic; color: #777; font-size: 0.9em; }}

        .meta {{
            margin: 0;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75em;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        .meta strong {{ color: #000; }}

        .market-header {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.3em;
            font-weight: 900;
            text-transform: uppercase;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .market-table {{ width: 100%; border-collapse: collapse; }}
        .market-table th, .market-table td {{
            padding: 10px 0;
            border-bottom: 1px solid #eee;
            font-size: 0.95em;
        }}
        .market-table th {{
            text-align: left;
            text-transform: uppercase;
            color: #777;
            font-size: 0.75em;
            font-family: 'IBM Plex Mono', monospace;
        }}
        .market-table .price, .market-table .change {{ text-align: right; }}
        .ticker-name {{ font-weight: 600; }}

        .footer-note {{
            margin-top: 40px;
            text-align: center;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7em;
            color: #999;
            letter-spacing: 0.5px;
        }}

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

        <div class="masthead">
            <h1>The Daily Briefing</h1>
        </div>
        <div class="date-bar">
            <span>Vol. 1 — Automated Edition</span>
            <span>{today} · Generated {generated_at} IST</span>
        </div>
        <div class="nav-bar">
            PORTFOLIO &nbsp; • &nbsp; MARKETS &nbsp; • &nbsp; M&amp;A &nbsp; • &nbsp; ARTIFICIAL INTELLIGENCE &nbsp; • &nbsp; CFA &amp; IIM
        </div>

        <div class="layout-wrapper">

            <div class="main-content">

                <div class="lead-story">
                    <p class="meta"><strong>{lead_story["publisher"]}</strong> | {lead_story["date"]}</p>
                    <h2><a href="{lead_story["link"]}" target="_blank">{lead_story["title"]}</a></h2>
                </div>

                <div class="articles-grid">
                    {html_invest}
                </div>

                <h4 class="section-title">Mergers &amp; Acquisitions</h4>
                <div class="articles-grid">
                    {html_ma}
                </div>

                <h4 class="section-title">AI &amp; Innovation</h4>
                <div class="articles-grid">
                    {html_ai}
                </div>

                <h4 class="section-title">CFA &amp; IIM Updates</h4>
                <div class="articles-grid">
                    {html_edu}
                </div>

            </div>

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

        <div class="footer-note">
            Articles limited to the last 48 hours · Trusted publishers shown first · Auto-generated, verify before acting on any figure
        </div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)
