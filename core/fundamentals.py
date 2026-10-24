from typing import Dict, Any, List
import pandas as pd
from core.sanitization import load_sector_medians


def calculate_radar_scores(fundamentals: Dict[str, Any], rsi_14: float = 50.0) -> Dict[str, float]:
    """
    Normalizes 5 fundamental/technical axes to a [0, 100] scale:
    1. Valuation (P/E relative to sector)[cite: 6]
    2. Growth (Revenue/Net Income Growth)[cite: 6]
    3. Financial Health (Debt to Equity)[cite: 6]
    4. Dividends (Dividend Yield)[cite: 6]
    5. Momentum (14-period RSI)[cite: 6]
    """
    sector = fundamentals.get("sector", "Default")
    sector_db = load_sector_medians()
    sec_defaults = sector_db.get(sector, sector_db.get("Default"))

    # 1. Valuation Score (Lower P/E relative to sector -> higher score)
    pe = fundamentals.get("pe_ratio", sec_defaults.get("pe_ratio", 20.0))
    sec_pe = sec_defaults.get("pe_ratio", 20.0)
    val_score = max(0.0, min(100.0, 100.0 * (1.5 - (pe / (sec_pe * 1.5)))))

    # 2. Growth Score
    rev_growth = fundamentals.get("revenue_growth") or 0.05
    inc_growth = fundamentals.get("net_income_growth") or 0.05
    growth_avg = (rev_growth + inc_growth) / 2.0
    growth_score = max(0.0, min(100.0, 50.0 + (growth_avg * 200.0)))

    # 3. Financial Health Score (Lower D/E -> higher score)
    de = fundamentals.get("debt_to_equity", sec_defaults.get("debt_to_equity", 0.75))
    health_score = max(0.0, min(100.0, 100.0 - (de * 40.0)))

    # 4. Dividend Score
    div_yield = fundamentals.get("dividend_yield") or 0.0
    div_score = max(0.0, min(100.0, div_yield * 2000.0))

    # 5. Momentum Score (RSI Mapping)
    momentum_score = max(0.0, min(100.0, rsi_14))

    return {
        "Valuation": round(val_score, 1),
        "Growth": round(growth_score, 1),
        "Financial Health": round(health_score, 1),
        "Dividends": round(div_score, 1),
        "Momentum": round(momentum_score, 1)
    }


def generate_peer_comparison_matrix(target_ticker: str, target_fund: Dict[str, Any]) -> pd.DataFrame:
    """Creates comparative valuation matrix across target asset and benchmark peers[cite: 1, 3, 6]."""
    sector = target_fund.get("sector", "Default")
    sec_db = load_sector_medians()
    benchmark = sec_db.get(sector, sec_db.get("Default"))

    records = [
        {
            "Ticker": target_ticker,
            "P/E": target_fund.get("pe_ratio"),
            "P/S": target_fund.get("ps_ratio"),
            "EV/EBITDA": target_fund.get("ev_ebitda"),
            "Operating Margin": f"{round((target_fund.get('operating_margin') or 0.0) * 100, 1)}%",
            "ROE": f"{round((target_fund.get('roe') or 0.0) * 100, 1)}%"
        },
        {
            "Ticker": f"Sector Median ({sector})",
            "P/E": benchmark.get("pe_ratio"),
            "P/S": benchmark.get("ps_ratio"),
            "EV/EBITDA": benchmark.get("ev_ebitda"),
            "Operating Margin": f"{round(benchmark.get('operating_margin', 0.15) * 100, 1)}%",
            "ROE": f"{round(benchmark.get('roe', 0.15) * 100, 1)}%"
        }
    ]

    return pd.DataFrame(records)