from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


def compute_technical_indicators(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Calculates 20, 50, and 200 EMA, 14-period RSI, and MACD (12, 26, 9).
    Generates actionable signal alerts (Golden/Death Cross, Overbought/Oversold).
    """
    clean_df = df.copy()

    # Ensure sorting by index or Date with robust mixed-timezone handling
    if "Date" in clean_df.columns:
        clean_df["Date"] = pd.to_datetime(clean_df["Date"], utc=True, format="mixed").dt.tz_localize(None)
        clean_df = clean_df.sort_values("Date").reset_index(drop=True)
    elif "index" in clean_df.columns:
        clean_df.rename(columns={"index": "Date"}, inplace=True)
        clean_df["Date"] = pd.to_datetime(clean_df["Date"], utc=True, format="mixed").dt.tz_localize(None)
        clean_df = clean_df.sort_values("Date").reset_index(drop=True)

    # 1. Exponential Moving Averages (EMA 20, 50, 200)
    clean_df["EMA_20"] = clean_df["Close"].ewm(span=20, adjust=False).mean()
    clean_df["EMA_50"] = clean_df["Close"].ewm(span=50, adjust=False).mean()
    clean_df["EMA_200"] = clean_df["Close"].ewm(span=200, adjust=False).mean()

    # 2. Relative Strength Index (RSI 14)
    delta = clean_df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).ewm(span=14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=14, adjust=False).mean()

    rs = gain / np.where(loss == 0, 1e-9, loss)
    clean_df["RSI_14"] = 100 - (100 / (1 + rs))

    # 3. MACD Line & Signal Line (12, 26, 9)
    ema_12 = clean_df["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = clean_df["Close"].ewm(span=26, adjust=False).mean()
    clean_df["MACD"] = ema_12 - ema_26
    clean_df["MACD_Signal"] = clean_df["MACD"].ewm(span=9, adjust=False).mean()
    clean_df["MACD_Hist"] = clean_df["MACD"] - clean_df["MACD_Signal"]

    # 4. Signal Synthesis & Cross Events
    latest = clean_df.iloc[-1]
    prev = clean_df.iloc[-2] if len(clean_df) > 1 else latest

    ema_cross = "Neutral"
    if prev["EMA_50"] <= prev["EMA_200"] and latest["EMA_50"] > latest["EMA_200"]:
        ema_cross = "Golden Cross (Bullish)"
    elif prev["EMA_50"] >= prev["EMA_200"] and latest["EMA_50"] < latest["EMA_200"]:
        ema_cross = "Death Cross (Bearish)"
    elif latest["EMA_50"] > latest["EMA_200"]:
        ema_cross = "Bullish Alignment (EMA 50 > 200)"
    else:
        ema_cross = "Bearish Alignment (EMA 50 < 200)"

    rsi_status = "Neutral"
    if latest["RSI_14"] >= 70:
        rsi_status = "Overbought (> 70)"
    elif latest["RSI_14"] <= 30:
        rsi_status = "Oversold (< 30)"

    macd_cross = "Neutral"
    if prev["MACD"] <= prev["MACD_Signal"] and latest["MACD"] > latest["MACD_Signal"]:
        macd_cross = "Bullish MACD Crossover"
    elif prev["MACD"] >= prev["MACD_Signal"] and latest["MACD"] < latest["MACD_Signal"]:
        macd_cross = "Bearish MACD Crossover"

    signals_summary = {
        "current_price": round(float(latest["Close"]), 2),
        "ema_20": round(float(latest["EMA_20"]), 2),
        "ema_50": round(float(latest["EMA_50"]), 2),
        "ema_200": round(float(latest["EMA_200"]), 2),
        "rsi_14": round(float(latest["RSI_14"]), 2),
        "macd": round(float(latest["MACD"]), 4),
        "macd_signal": round(float(latest["MACD_Signal"]), 4),
        "macd_hist": round(float(latest["MACD_Hist"]), 4),
        "ema_cross": ema_cross,
        "rsi_status": rsi_status,
        "macd_cross": macd_cross
    }

    return clean_df, signals_summary