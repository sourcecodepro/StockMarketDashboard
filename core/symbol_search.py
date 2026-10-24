import json
import urllib.parse
import urllib.request
from typing import Dict, List, Any

# Offline fallback symbol database for offline/resilient search
LOCAL_SYMBOL_CACHE: List[Dict[str, str]] = [
    # Indian Bluechips (NSE)
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd", "exchange": "NSE"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services Ltd", "exchange": "NSE"},
    {"symbol": "INFY.NS", "name": "Infosys Ltd", "exchange": "NSE"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Ltd", "exchange": "NSE"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Ltd", "exchange": "NSE"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd", "exchange": "NSE"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors Ltd", "exchange": "NSE"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel Ltd", "exchange": "NSE"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE"},
    {"symbol": "ITC.NS", "name": "ITC Ltd", "exchange": "NSE"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd", "exchange": "NSE"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro Ltd", "exchange": "NSE"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries Ltd", "exchange": "NSE"},
    {"symbol": "NTPC.NS", "name": "NTPC Ltd", "exchange": "NSE"},
    {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corporation Ltd", "exchange": "NSE"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Ltd", "exchange": "NSE"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Ltd", "exchange": "NSE"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank Ltd", "exchange": "NSE"},
    {"symbol": "TITAN.NS", "name": "Titan Company Ltd", "exchange": "NSE"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises Ltd", "exchange": "NSE"},

    # US & Global Leaders
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
    {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
    {"symbol": "BRK-B", "name": "Berkshire Hathaway Inc.", "exchange": "NYSE"},
    {"symbol": "LLY", "name": "Eli Lilly and Company", "exchange": "NYSE"},
    {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "exchange": "NYSE"},
    {"symbol": "XOM", "name": "Exxon Mobil Corporation", "exchange": "NYSE"},
]


def search_global_symbols(query: str) -> List[Dict[str, str]]:
    """
    Dynamically fetches matching stock symbols from live search API endpoint.
    Falls back to local cache if network is unavailable or rate-limited.
    """
    clean_query = query.strip()
    if not clean_query:
        return filter_local_symbols("RELIANCE")

    encoded_query = urllib.parse.quote(clean_query)
    search_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={encoded_query}&quotesCount=12&newsCount=0"

    req = urllib.request.Request(
        search_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )

    results: List[Dict[str, str]] = []

    try:
        with urllib.request.urlopen(req, timeout=2.5) as response:
            data = json.loads(response.read().decode("utf-8"))
            quotes = data.get("quotes", [])
            for q in quotes:
                symbol = q.get("symbol")
                if not symbol:
                    continue

                short_name = q.get("shortname") or q.get("longname") or symbol
                exchange = q.get("exchDisp") or q.get("exchange") or "GLOBAL"
                quote_type = q.get("quoteType", "")

                if quote_type in ["EQUITY", "ETF", "INDEX", "MUTUALFUND"]:
                    results.append({
                        "label": f"{symbol} - {short_name} ({exchange})",
                        "value": symbol
                    })
    except Exception:
        results = filter_local_symbols(clean_query)

    # If API yielded no results, fall back to local matching
    if not results:
        results = filter_local_symbols(clean_query)

    # Guarantee user input option is present
    raw_val = clean_query.upper()
    existing_vals = {r["value"] for r in results}
    if raw_val not in existing_vals:
        results.insert(0, {"label": f"{raw_val} (Query Symbol)", "value": raw_val})

    return results


def filter_local_symbols(query: str) -> List[Dict[str, str]]:
    """Filters offline symbol database by symbol or company name."""
    q = query.strip().upper()
    matched = []
    for item in LOCAL_SYMBOL_CACHE:
        if q in item["symbol"].upper() or q in item["name"].upper():
            matched.append({
                "label": f"{item['symbol']} - {item['name']} ({item['exchange']})",
                "value": item["symbol"]
            })
    return matched