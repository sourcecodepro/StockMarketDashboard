import time
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import yfinance as yf

from core.schemas import FundamentalDataSchema, MarketDataSchema
from core.sanitization import sanitize_ohlcv, sanitize_fundamentals
from core.telemetry import calculate_dhs, log_telemetry

CURRENCY_MAP = {
    "USD": "$",
    "INR": "₹",
    "EUR": "€",
    "GBP": "£",
    "CAD": "C$",
    "AUD": "A$",
    "JPY": "¥"
}


def resolve_global_ticker(ticker: str) -> Tuple[str, str]:
    """
    Normalizes ticker symbols and resolves exchange origins.
    Auto-appends '.NS' for standard Indian tickers if no exchange extension is provided.
    """
    clean_ticker = ticker.strip().upper()

    # Auto-detect benchmark index based on exchange suffix
    if clean_ticker.endswith(".NS") or clean_ticker.endswith(".BO"):
        return clean_ticker, "^NSEI"  # Nifty 50 Index for NSE/BSE

    # Common Indian stock tickers without suffix support
    indian_bluechips = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "TATAMOTORS", "SBIN", "BHARTIARTL"]
    if clean_ticker in indian_bluechips:
        return f"{clean_ticker}.NS", "^NSEI"

    return clean_ticker, "SPY"  # Standard S&P 500 ETF for US/Global


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.is_tripped = False

    def record_success(self):
        self.failure_count = 0
        self.is_tripped = False

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.is_tripped = True


circuit_breaker = CircuitBreaker()


def generate_fallback_dataset(ticker: str) -> pd.DataFrame:
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq="B")
    base_price = 1500.0 if ".NS" in ticker else 150.0
    data = {
        "Open": [base_price + (i * 0.5) for i in range(100)],
        "High": [base_price + (i * 0.5) + 5.0 for i in range(100)],
        "Low": [base_price + (i * 0.5) - 4.0 for i in range(100)],
        "Close": [base_price + (i * 0.5) + 1.0 for i in range(100)],
        "Volume": [2000000 + (i * 10000) for i in range(100)],
    }
    df = pd.DataFrame(data, index=dates)
    fallback_path = Path("data/fallback_cache.parquet")
    fallback_path.parent.mkdir(exist_ok=True)
    df.to_parquet(fallback_path)
    return df


def load_fallback_data(ticker: str) -> pd.DataFrame:
    fallback_path = Path("data/fallback_cache.parquet")
    if fallback_path.exists():
        return pd.read_parquet(fallback_path)
    return generate_fallback_dataset(ticker)


def fetch_market_and_fundamental_data(raw_ticker: str) -> Dict[str, Any]:
    ticker, default_benchmark = resolve_global_ticker(raw_ticker)
    imputed_log = []
    total_fields_tracked = 12
    source_used = "yfinance_live"

    if circuit_breaker.is_tripped:
        source_used = "offline_fallback_cache"
        df_ohlcv = load_fallback_data(ticker)
        raw_info = {"sector": "Technology", "shortName": f"{ticker} (Offline)",
                    "currency": "INR" if ".NS" in ticker else "USD"}
    else:
        try:
            yt = yf.Ticker(ticker)
            df_ohlcv = yt.history(period="1y", interval="1d")

            if df_ohlcv.empty:
                raise ValueError(f"No price history returned for {ticker}")

            raw_info = yt.info or {}
            circuit_breaker.record_success()

        except Exception:
            circuit_breaker.record_failure()
            source_used = "offline_fallback_cache"
            df_ohlcv = load_fallback_data(ticker)
            raw_info = {"sector": "Technology", "shortName": f"{ticker} (Cached)",
                        "currency": "INR" if ".NS" in ticker else "USD"}

    # Timezone normalization
    if isinstance(df_ohlcv.index, pd.DatetimeIndex) and df_ohlcv.index.tz is not None:
        df_ohlcv.index = df_ohlcv.index.tz_convert("UTC").tz_localize(None)

    clean_df, ohlcv_imputations = sanitize_ohlcv(df_ohlcv)
    imputed_log.extend(ohlcv_imputations)

    try:
        MarketDataSchema.validate_df(clean_df)
    except Exception as e:
        imputed_log.append(f"Market Schema Error: {str(e)}")

    sector = raw_info.get("sector", "Default")
    currency_code = raw_info.get("currency", "INR" if ".NS" in ticker or ".BO" in ticker else "USD")
    currency_symbol = CURRENCY_MAP.get(currency_code, "$")

    raw_fundamentals = {
        "ticker": ticker,
        "sector": sector,
        "pe_ratio": raw_info.get("trailingPE"),
        "ps_ratio": raw_info.get("priceToSalesTrailing12Months"),
        "ev_ebitda": raw_info.get("enterpriseToEbitda"),
        "debt_to_equity": raw_info.get("debtToEquity"),
        "operating_margin": raw_info.get("operatingMargins"),
        "roe": raw_info.get("returnOnEquity"),
        "dividend_yield": raw_info.get("dividendYield"),
        "revenue_growth": raw_info.get("revenueGrowth"),
        "net_income_growth": raw_info.get("earningsGrowth"),
    }

    clean_fundamentals, fund_imputations = sanitize_fundamentals(raw_fundamentals, sector)
    imputed_log.extend(fund_imputations)

    try:
        validated_fundamentals = FundamentalDataSchema(**clean_fundamentals).model_dump()
    except Exception as e:
        imputed_log.append(f"Schema Validation Fallback: {str(e)}")
        validated_fundamentals = clean_fundamentals

    dhs_info = calculate_dhs(total_fields_tracked, len(imputed_log))
    log_telemetry(ticker, dhs_info, imputed_log, source=source_used)

    return {
        "ticker": ticker,
        "company_name": raw_info.get("shortName", ticker),
        "currency_code": currency_code,
        "currency_symbol": currency_symbol,
        "benchmark_symbol": default_benchmark,
        "source": source_used,
        "ohlcv": clean_df.reset_index().to_dict(orient="records"),
        "fundamentals": validated_fundamentals,
        "dhs": dhs_info,
        "imputed_log": imputed_log
    }