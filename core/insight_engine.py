from typing import Dict, Any, List


def generate_executive_insights(
        ticker: str,
        fundamentals: Dict[str, Any],
        technicals_summary: Dict[str, Any],
        risk_metrics: Dict[str, Any] = None
) -> List[str]:
    """
    Parses combined technical and fundamental metrics through a decision matrix rule engine:
    Outputs 3 to 5 executive takeaway bullet points.
    """
    insights = []

    # Parse technical signals
    price = technicals_summary.get("current_price", 0.0)
    ema_20 = technicals_summary.get("ema_20", 0.0)
    ema_200 = technicals_summary.get("ema_200", 0.0)
    rsi = technicals_summary.get("rsi_14", 50.0)

    # Parse fundamentals
    pe = fundamentals.get("pe_ratio", 20.0)
    de = fundamentals.get("debt_to_equity", 0.75)
    sector = fundamentals.get("sector", "Sector")

    # Rule 1: Technical Swing Alignment
    if rsi < 30 and price > ema_200:
        insights.append(
            f"**Oversold Pullback ({ticker}):** RSI is oversold ({rsi}) above the 200-day EMA, indicating a potential swing long entry setup.")
    elif rsi > 70 and price < ema_20:
        insights.append(
            f"**Overbought Reversal ({ticker}):** RSI is overbought ({rsi}) below the 20-day EMA, suggesting near-term momentum depletion.")
    elif price > ema_20 > ema_200:
        insights.append(
            f"**Strong Uptrend ({ticker}):** Price trades constructively above both 20-day and 200-day EMAs with neutral RSI ({rsi}).")
    else:
        insights.append(
            f"**Consolidation Pattern ({ticker}):** Technical indicators reflect range-bound price action around EMA levels.")

    # Rule 2: Fundamental Valuation & Balance Sheet Safety
    if pe < 15.0 and de < 0.6:
        insights.append(
            f"**Value & Balance Sheet Quality:** Trades at an attractive P/E multiplier ({pe}) paired with low Debt-to-Equity ({de}).")
    elif pe > 40.0:
        insights.append(
            f"**Premium Multiple Alert:** P/E of {pe} reflects high growth expectations relative to {sector} baseline benchmarks.")
    else:
        insights.append(f"**Fair Valuation:** Valuation multiples align within normal expected {sector} sector bounds.")

    # Rule 3: Portfolio Beta & Concentration Exposure (if provided)
    if risk_metrics:
        p_beta = risk_metrics.get("portfolio_beta", 1.0)
        sharpe = risk_metrics.get("sharpe_ratio", 0.0)

        if p_beta > 1.35:
            insights.append(
                f"**High Systematic Exposure:** Overall portfolio Beta ({p_beta}) indicates high sensitivity to broader market downturns.")
        elif p_beta < 0.85:
            insights.append(
                f"**Defensive Portfolio Bias:** Portfolio Beta ({p_beta}) provides downside mitigation against index volatility.")

        if sharpe > 1.2:
            insights.append(
                f"**Strong Risk-Adjusted Returns:** Annualized Sharpe Ratio stands at {sharpe}, indicating efficient risk-adjusted performance.")
        elif sharpe < 0.5:
            insights.append(
                f"**Sub-optimal Risk Adjustment:** Sharpe Ratio of {sharpe} suggests return compensation is low relative to portfolio volatility.")

    return insights