import json
from pathlib import Path
from typing import Dict, Any, Tuple, List
import pandas as pd


def load_sector_medians() -> Dict[str, Dict[str, float]]:
    path = Path("data/sector_medians.json")
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {"Default": {"pe_ratio": 20.0, "ps_ratio": 2.5, "ev_ebitda": 14.0, "debt_to_equity": 0.75, "operating_margin": 0.15, "roe": 0.15}}


def sanitize_ohlcv(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Sanitizes price time-series using forward-fill, backward-fill, and volume zeroing."""
    repaired_fields: List[str] = []
    clean_df = df.copy()

    # 1. Fill missing volume channels with zero
    if clean_df["Volume"].isnull().any():
        clean_df["Volume"] = clean_df["Volume"].fillna(0)
        repaired_fields.append("Volume (Zero Filled)")

    # 2. Forward-fill then Backward-fill missing OHLC price gaps
    price_cols = [c for c in ["Open", "High", "Low", "Close", "Adj Close"] if c in clean_df.columns]
    for col in price_cols:
        if clean_df[col].isnull().any():
            clean_df[col] = clean_df[col].ffill().bfill()
            repaired_fields.append(f"{col} Time-Series (ffill/bfill)")

    return clean_df, repaired_fields


def sanitize_fundamentals(raw_metrics: Dict[str, Any], sector: str = "Default") -> Tuple[Dict[str, Any], List[str]]:
    """Imputes missing valuation ratios using derived financial relationships and sector medians."""
    imputed_fields: List[str] = []
    sanitized = raw_metrics.copy()
    medians_db = load_sector_medians()
    sector_defaults = medians_db.get(sector, medians_db.get("Default"))

    # Strategy 1: Dynamic Balance Sheet Ratio Derivation
    if sanitized.get("debt_to_equity") is None:
        tot_liab = raw_metrics.get("total_liabilities")
        tot_eq = raw_metrics.get("total_equity")
        if tot_liab and tot_eq and tot_eq != 0:
            sanitized["debt_to_equity"] = round(tot_liab / tot_eq, 2)
            imputed_fields.append("debt_to_equity (Derived from Liabilities/Equity)")

    # Strategy 2: Sector Median Imputation
    target_ratios = ["pe_ratio", "ps_ratio", "ev_ebitda", "debt_to_equity", "operating_margin", "roe"]
    for key in target_ratios:
        if sanitized.get(key) is None or pd.isna(sanitized.get(key)):
            median_val = sector_defaults.get(key, 0.0)
            sanitized[key] = median_val
            imputed_fields.append(f"{key} (Sector Median: {sector})")

    return sanitized, imputed_fields