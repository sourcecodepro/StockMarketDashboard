from typing import Dict, Any, List
import numpy as np
import pandas as pd


def compute_portfolio_risk_metrics(
    portfolio_df: pd.DataFrame,
    price_history_dict: Dict[str, pd.DataFrame],
    benchmark_symbol: str = "SPY",
    rf_rate: float = 0.042
) -> Dict[str, Any]:
    if portfolio_df.empty or not price_history_dict:
        return {
            "portfolio_beta": 1.0,
            "sharpe_ratio": 0.0,
            "total_invested": 0.0,
            "current_value": 0.0,
            "total_pnl": 0.0,
            "pnl_pct": 0.0,
            "benchmark_used": benchmark_symbol,
            "summary_table": [],
            "correlation_matrix": pd.DataFrame().to_dict()
        }

    summary_rows = []
    daily_returns_dict = {}

    for _, row in portfolio_df.iterrows():
        ticker = row["Ticker"]
        qty = float(row["Quantity"])
        buy_price = float(row["Buy_Price"])

        if ticker in price_history_dict and not price_history_dict[ticker].empty:
            hist_df = price_history_dict[ticker]
            curr_price = float(hist_df["Close"].iloc[-1])
            returns = hist_df["Close"].pct_change().dropna()
            daily_returns_dict[ticker] = returns
        else:
            curr_price = buy_price
            daily_returns_dict[ticker] = pd.Series([0.0])

        invested = qty * buy_price
        current_val = qty * curr_price
        pnl = current_val - invested

        summary_rows.append({
            "Ticker": ticker,
            "Quantity": qty,
            "Buy_Price": buy_price,
            "Current_Price": curr_price,
            "Invested": invested,
            "Current_Value": current_val,
            "PnL": pnl,
            "PnL_Pct": (pnl / invested) * 100.0 if invested > 0 else 0.0
        })

    summary_df = pd.DataFrame(summary_rows)
    total_invested = float(summary_df["Invested"].sum())
    total_value = float(summary_df["Current_Value"].sum())
    total_pnl = total_value - total_invested
    pnl_pct = (total_pnl / total_invested) * 100.0 if total_invested > 0 else 0.0

    summary_df["Weight"] = summary_df["Current_Value"] / total_value if total_value > 0 else 0.0

    returns_df = pd.DataFrame(daily_returns_dict).dropna()
    if not returns_df.empty and len(returns_df.columns) > 1:
        corr_matrix = returns_df.corr(method="pearson").round(2)
    else:
        corr_matrix = pd.DataFrame(1.0, index=summary_df["Ticker"], columns=summary_df["Ticker"])

    # Benchmark Risk Alignment (Nifty 50 for Indian assets, S&P 500 for US/Global)
    if benchmark_symbol in price_history_dict and not price_history_dict[benchmark_symbol].empty:
        bench_returns = price_history_dict[benchmark_symbol]["Close"].pct_change().dropna()
    else:
        bench_returns = returns_df.mean(axis=1) if not returns_df.empty else pd.Series([0.01] * len(returns_df))

    aligned_data = returns_df.join(bench_returns.rename("Benchmark"), how="inner").dropna()

    if not aligned_data.empty and len(aligned_data) > 5:
        bench_var = float(aligned_data["Benchmark"].var())
        weights = summary_df.set_index("Ticker")["Weight"].to_dict()

        asset_betas = {}
        for col in returns_df.columns:
            if bench_var > 0:
                cov = float(aligned_data[col].cov(aligned_data["Benchmark"]))
                asset_betas[col] = cov / bench_var
            else:
                asset_betas[col] = 1.0

        portfolio_beta = float(sum(weights.get(t, 0.0) * asset_betas.get(t, 1.0) for t in weights))

        port_daily_ret = sum(aligned_data[t] * weights.get(t, 0.0) for t in returns_df.columns)
        mean_ret = float(port_daily_ret.mean()) * 252
        volatility = float(port_daily_ret.std()) * np.sqrt(252)

        sharpe_ratio = float((mean_ret - rf_rate) / volatility) if volatility > 0 else 0.0
    else:
        portfolio_beta = 1.0
        sharpe_ratio = 0.0

    return {
        "total_invested": round(total_invested, 2),
        "current_value": round(total_value, 2),
        "total_pnl": round(total_pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "portfolio_beta": round(portfolio_beta, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "benchmark_used": benchmark_symbol,
        "summary_table": summary_df.to_dict(orient="records"),
        "correlation_matrix": corr_matrix.to_dict()
    }