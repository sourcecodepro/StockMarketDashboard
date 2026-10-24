from typing import Dict, Any, Optional
import pandas as pd
from pydantic import BaseModel, Field, field_validator


class FundamentalDataSchema(BaseModel):
    """Pydantic contract enforcing numerical boundaries on financial ratios."""
    ticker: str
    sector: str = "Default"
    pe_ratio: Optional[float] = Field(None, ge=0.0, le=1000.0)
    ps_ratio: Optional[float] = Field(None, ge=0.0)
    ev_ebitda: Optional[float] = Field(None, ge=0.0)
    debt_to_equity: Optional[float] = Field(None, ge=0.0)
    operating_margin: Optional[float] = Field(None)
    roe: Optional[float] = Field(None, ge=-5.0, le=5.0)
    dividend_yield: Optional[float] = Field(None, ge=0.0, le=1.0)
    revenue_growth: Optional[float] = Field(None)
    net_income_growth: Optional[float] = Field(None)

    @field_validator("pe_ratio", mode="before")
    @classmethod
    def sanitize_pe(cls, v: Any) -> Optional[float]:
        if v is None or pd.isna(v):
            return None
        try:
            val = float(v)
            return val if 0.0 <= val <= 1000.0 else None
        except (ValueError, TypeError):
            return None

    @field_validator("dividend_yield", mode="before")
    @classmethod
    def sanitize_div_yield(cls, v: Any) -> Optional[float]:
        if v is None or pd.isna(v):
            return None
        try:
            val = float(v)
            # Convert percentage scale (1.99%) to ratio scale (0.0199)
            if val > 1.0:
                val = val / 100.0
            return val if 0.0 <= val <= 1.0 else None
        except (ValueError, TypeError):
            return None

    @field_validator("roe", mode="before")
    @classmethod
    def sanitize_roe(cls, v: Any) -> Optional[float]:
        if v is None or pd.isna(v):
            return None
        try:
            val = float(v)
            if abs(val) > 100.0:
                val = val / 100.0
            return val if -5.0 <= val <= 5.0 else None
        except (ValueError, TypeError):
            return None


class MarketDataSchema:
    """Validates structure, types, and bounds of historical OHLCV DataFrames."""

    REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

    @classmethod
    def validate_df(cls, df: pd.DataFrame) -> bool:
        if df.empty:
            raise ValueError("Market DataFrame is empty")

        missing_cols = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required price columns: {missing_cols}")

        if (df["Volume"] < 0).any():
            raise ValueError("Negative volume values detected")

        if (df["Close"] <= 0).any():
            raise ValueError("Non-positive close prices detected")

        return True