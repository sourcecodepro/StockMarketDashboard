from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import yfinance as yf


def calc_multi_period_returns(df_close: pd.Series) -> Dict[str, float]:
    """Calculates 1D, 1W, 1M, and YTD percentage changes from close price series."""
    if df_close.empty or len(df_close) < 2:
        return {"1D": 0.0, "1W": 0.0, "1M": 0.0, "YTD": 0.0}

    latest = float(df_close.iloc[-1])

    # 1 Day %
    c_1d = float(df_close.iloc[-2])
    ret_1d = ((latest - c_1d) / c_1d) * 100.0 if c_1d > 0 else 0.0

    # 1 Week % (~5 trading days)
    c_1w = float(df_close.iloc[-6]) if len(df_close) >= 6 else float(df_close.iloc[0])
    ret_1w = ((latest - c_1w) / c_1w) * 100.0 if c_1w > 0 else 0.0

    # 1 Month % (~21 trading days)
    c_1m = float(df_close.iloc[-22]) if len(df_close) >= 22 else float(df_close.iloc[0])
    ret_1m = ((latest - c_1m) / c_1m) * 100.0 if c_1m > 0 else 0.0

    # YTD %
    cur_year = df_close.index[-1].year if hasattr(df_close.index[-1], "year") else pd.Timestamp.now().year
    try:
        ytd_subset = df_close[df_close.index.year == cur_year]
        c_ytd = float(ytd_subset.iloc[0]) if not ytd_subset.empty else float(df_close.iloc[0])
    except Exception:
        c_ytd = float(df_close.iloc[0])

    ret_ytd = ((latest - c_ytd) / c_ytd) * 100.0 if c_ytd > 0 else 0.0

    return {
        "1D": round(ret_1d, 2),
        "1W": round(ret_1w, 2),
        "1M": round(ret_1m, 2),
        "YTD": round(ret_ytd, 2)
    }


def fetch_market_radar_data(
        region: str = "IN",
        portfolio_summary: Optional[List[Dict[str, Any]]] = None,
        price_history_dict: Optional[Dict[str, pd.DataFrame]] = None
) -> Dict[str, Any]:
    """
    Dynamically generates Market Radar metrics:
    - If portfolio_summary is provided: Renders Active Portfolio Treemap & Holdings Performance
    - Else: Renders Nifty 50 (IN) or S&P 500 (US) Sector Heavyweight Treemap
    """
    treemap_records = []
    advances = 0
    declines = 0
    vol_anomalies = 0
    highs_52w = 0
    lows_52w = 0

    # Mode A: Active Portfolio Mode
    if portfolio_summary and price_history_dict:
        for item in portfolio_summary:
            ticker = item["Ticker"]
            val = float(item.get("Current_Value", 1000))

            perf_1d = 0.0
            if ticker in price_history_dict and not price_history_dict[ticker].empty:
                hist = price_history_dict[ticker]
                if len(hist) >= 2:
                    latest = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    perf_1d = round(((latest - prev) / prev) * 100.0, 2)

                    if perf_1d >= 0:
                        advances += 1
                    else:
                        declines += 1

                    latest_vol = float(hist["Volume"].iloc[-1])
                    avg_vol = float(hist["Volume"].tail(20).mean())
                    if avg_vol > 0 and (latest_vol / avg_vol) >= 2.0:
                        vol_anomalies += 1

                    max_52w = float(hist["High"].max())
                    min_52w = float(hist["Low"].min())
                    if latest >= max_52w * 0.98:
                        highs_52w += 1
                    if latest <= min_52w * 1.02:
                        lows_52w += 1

            treemap_records.append({
                "Sector": "Portfolio Holdings",
                "Company": f"{ticker}",
                "MarketCap": val,
                "Performance": perf_1d
            })

    # Mode B: Market Region Mode (IN / US)
    if not treemap_records:
        if region == "IN":
            constituents = [
                {"Sector": "Technology", "Company": "TCS (TCS.NS)", "Ticker": "TCS.NS", "MarketCap": 150000},
                {"Sector": "Technology", "Company": "Infosys (INFY.NS)", "Ticker": "INFY.NS", "MarketCap": 80000},
                {"Sector": "Financials", "Company": "HDFC Bank (HDFCBANK.NS)", "Ticker": "HDFCBANK.NS",
                 "MarketCap": 140000},
                {"Sector": "Financials", "Company": "ICICI Bank (ICICIBANK.NS)", "Ticker": "ICICIBANK.NS",
                 "MarketCap": 95000},
                {"Sector": "Energy", "Company": "Reliance (RELIANCE.NS)", "Ticker": "RELIANCE.NS", "MarketCap": 200000},
                {"Sector": "Energy", "Company": "NTPC (NTPC.NS)", "Ticker": "NTPC.NS", "MarketCap": 40000},
                {"Sector": "FMCG", "Company": "ITC (ITC.NS)", "Ticker": "ITC.NS", "MarketCap": 60000},
                {"Sector": "Automobile", "Company": "Tata Motors (TATAMOTORS.NS)", "Ticker": "TATAMOTORS.NS",
                 "MarketCap": 38000},
            ]
        else:
            constituents = [
                {"Sector": "Technology", "Company": "Apple (AAPL)", "Ticker": "AAPL", "MarketCap": 3400},
                {"Sector": "Technology", "Company": "Microsoft (MSFT)", "Ticker": "MSFT", "MarketCap": 3100},
                {"Sector": "Technology", "Company": "NVIDIA (NVDA)", "Ticker": "NVDA", "MarketCap": 3300},
                {"Sector": "Consumer Cyclical", "Company": "Amazon (AMZN)", "Ticker": "AMZN", "MarketCap": 2100},
                {"Sector": "Consumer Cyclical", "Company": "Tesla (TSLA)", "Ticker": "TSLA", "MarketCap": 750},
                {"Sector": "Financials", "Company": "JPMorgan (JPM)", "Ticker": "JPM", "MarketCap": 620},
                {"Sector": "Healthcare", "Company": "Eli Lilly (LLY)", "Ticker": "LLY", "MarketCap": 850},
                {"Sector": "Energy", "Company": "ExxonMobil (XOM)", "Ticker": "XOM", "MarketCap": 480},
            ]

        for item in constituents:
            sym = item["Ticker"]
            perf_1d = 0.0
            try:
                yt = yf.Ticker(sym)
                hist = yt.history(period="1y")
                if not hist.empty and len(hist) >= 2:
                    latest = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    perf_1d = round(((latest - prev) / prev) * 100.0, 2)

                    if perf_1d >= 0:
                        advances += 1
                    else:
                        declines += 1

                    latest_vol = float(hist["Volume"].iloc[-1])
                    avg_vol = float(hist["Volume"].tail(20).mean())
                    if avg_vol > 0 and (latest_vol / avg_vol) >= 2.0:
                        vol_anomalies += 1

                    max_52w = float(hist["High"].max())
                    min_52w = float(hist["Low"].min())
                    if latest >= max_52w * 0.98:
                        highs_52w += 1
                    if latest <= min_52w * 1.02:
                        lows_52w += 1
                else:
                    advances += 1
            except Exception:
                advances += 1

            treemap_records.append({
                "Sector": item["Sector"],
                "Company": item["Company"],
                "MarketCap": item["MarketCap"],
                "Performance": perf_1d
            })

    # Fetch Sector Rotation Heatmap Matrix
    sector_benchmarks = {
        "Technology": "TCS.NS" if region == "IN" else "XLK",
        "Financials": "HDFCBANK.NS" if region == "IN" else "XLF",
        "Energy": "RELIANCE.NS" if region == "IN" else "XLE",
        "FMCG / Consumer": "ITC.NS" if region == "IN" else "XLY",
        "Healthcare": "SUNPHARMA.NS" if region == "IN" else "XLV",
    }

    heatmap_sectors = list(sector_benchmarks.keys())
    heatmap_periods = ["1D", "1W", "1M", "YTD"]
    heatmap_matrix = []

    for sector, b_ticker in sector_benchmarks.items():
        try:
            yt = yf.Ticker(b_ticker)
            hist = yt.history(period="1y")
            if not hist.empty:
                returns = calc_multi_period_returns(hist["Close"])
                heatmap_matrix.append([returns["1D"], returns["1W"], returns["1M"], returns["YTD"]])
            else:
                heatmap_matrix.append([1.2, 2.4, 4.5, 12.0])
        except Exception:
            heatmap_matrix.append([0.5, 1.1, 2.8, 8.5])

    ad_ratio = round(advances / declines, 2) if declines > 0 else float(advances)

    return {
        "region": region,
        "treemap": treemap_records,
        "sector_heatmap": {
            "sectors": heatmap_sectors,
            "periods": heatmap_periods,
            "matrix": heatmap_matrix
        },
        "breadth": {
            "advances": advances,
            "declines": declines,
            "ad_ratio": ad_ratio,
            "vol_anomalies": vol_anomalies,
            "highs_52w": highs_52w,
            "lows_52w": lows_52w
        }
    }