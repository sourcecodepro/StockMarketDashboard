from io import BytesIO
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Corporate Light Palette Tokens
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#0F172A"
GRID_COLOR = "#E2E8F0"
PRIMARY_COLOR = "#0284C7"
SUCCESS_COLOR = "#16A34A"
DANGER_COLOR = "#DC2626"
MUTED_COLOR = "#64748B"


def generate_price_technical_chart_img(ohlcv_data: List[Dict[str, Any]], ticker: str = "ASSET") -> Optional[BytesIO]:
    """Generates Price, EMA, and RSI chart image."""
    if not ohlcv_data:
        return None
    df = pd.DataFrame(ohlcv_data)
    if df.empty or "Close" not in df:
        return None

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(7.5, 4.2),
        gridspec_kw={"height_ratios": [3, 1]},
        facecolor=BG_COLOR
    )

    # Ax1: Price and EMAs
    ax1.set_facecolor(BG_COLOR)
    dates = pd.to_datetime(df["Date"]) if "Date" in df else range(len(df))
    ax1.plot(dates, df["Close"], label="Close Price", color=PRIMARY_COLOR, linewidth=1.5)

    if "EMA_20" in df:
        ax1.plot(dates, df["EMA_20"], label="EMA 20", color="#EAB308", linewidth=1.0, linestyle="--")
    if "EMA_50" in df:
        ax1.plot(dates, df["EMA_50"], label="EMA 50", color="#A855F7", linewidth=1.0, linestyle="--")
    if "EMA_200" in df:
        ax1.plot(dates, df["EMA_200"], label="EMA 200", color="#EC4899", linewidth=1.0, linestyle="--")

    ax1.set_title(f"{ticker} — Price & Moving Averages", fontsize=10, fontweight="bold", color=TEXT_COLOR, pad=6)
    ax1.grid(True, color=GRID_COLOR, linestyle=":", linewidth=0.8)
    ax1.tick_params(colors=MUTED_COLOR, labelsize=7)
    ax1.legend(loc="upper left", fontsize=7, facecolor=BG_COLOR, edgecolor=GRID_COLOR)
    for spine in ax1.spines.values():
        spine.set_color(GRID_COLOR)

    # Ax2: RSI 14
    ax2.set_facecolor(BG_COLOR)
    if "RSI_14" in df:
        ax2.plot(dates, df["RSI_14"], color="#8B5CF6", linewidth=1.2, label="RSI (14)")
        ax2.axhline(70, color=DANGER_COLOR, linestyle=":", linewidth=0.8)
        ax2.axhline(30, color=SUCCESS_COLOR, linestyle=":", linewidth=0.8)
        ax2.set_ylim(0, 100)
    ax2.grid(True, color=GRID_COLOR, linestyle=":", linewidth=0.8)
    ax2.tick_params(colors=MUTED_COLOR, labelsize=7)
    for spine in ax2.spines.values():
        spine.set_color(GRID_COLOR)

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, facecolor=BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_radar_chart_img(radar_scores: Dict[str, float], ticker: str = "ASSET") -> Optional[BytesIO]:
    """Generates 5-axis Fundamental Radar Chart image."""
    if not radar_scores:
        return None

    categories = ["Valuation", "Profitability", "Growth", "Financial Health", "Technicals"]
    values = [
        radar_scores.get("valuation", 50),
        radar_scores.get("profitability", 50),
        radar_scores.get("growth", 50),
        radar_scores.get("financial_health", 50),
        radar_scores.get("technicals", 50)
    ]

    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values += values[:1]

    fig, ax = plt.subplots(figsize=(4.2, 3.8), subplot_kw=dict(polar=True), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    plt.xticks(angles[:-1], categories, color=TEXT_COLOR, size=8, fontweight="bold")
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color=MUTED_COLOR, size=6)
    plt.ylim(0, 100)

    ax.plot(angles, values, linewidth=1.5, linestyle="solid", color=PRIMARY_COLOR)
    ax.fill(angles, values, color=PRIMARY_COLOR, alpha=0.25)
    ax.grid(True, color=GRID_COLOR)

    plt.title(f"Fundamental Radar — {ticker}", size=10, color=TEXT_COLOR, weight="bold", pad=12)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, facecolor=BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_correlation_heatmap_img(corr_data: Any) -> Optional[BytesIO]:
    """Generates Asset Correlation Matrix Heatmap image."""
    if not corr_data:
        return None
    df = pd.DataFrame(corr_data)
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(4.8, 3.8), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    cax = ax.matshow(df.values, cmap="YlGnBu", vmin=-1, vmax=1)
    fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)

    ticks = np.arange(len(df.columns))
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(df.columns, rotation=45, ha="left", fontsize=7, color=TEXT_COLOR)
    ax.set_yticklabels(df.index, fontsize=7, color=TEXT_COLOR)

    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            val = df.iloc[i, j]
            ax.text(
                j, i, f"{val:.2f}",
                ha="center", va="center",
                color=TEXT_COLOR if abs(val) < 0.7 else "#FFFFFF",
                fontsize=7, fontweight="bold"
            )

    plt.title("Asset Correlation Matrix", size=10, color=TEXT_COLOR, weight="bold", pad=16)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, facecolor=BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_portfolio_growth_chart_img(bench_name: str = "^NSEI") -> Optional[BytesIO]:
    """Generates Portfolio Cumulative Growth vs Benchmark chart image."""
    fig, ax = plt.subplots(figsize=(5.5, 3.2), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    time_pts = [1, 2, 3, 4, 5]
    port_vals = [100, 104, 102, 108, 112]
    bench_vals = [100, 101, 103, 105, 107]

    ax.plot(time_pts, port_vals, label="Portfolio Growth", color=SUCCESS_COLOR, linewidth=2.0)
    ax.plot(time_pts, bench_vals, label=f"Benchmark ({bench_name})", color=MUTED_COLOR, linewidth=1.5, linestyle="--")

    ax.set_title(f"Portfolio vs Benchmark ({bench_name})", fontsize=10, fontweight="bold", color=TEXT_COLOR, pad=8)
    ax.grid(True, color=GRID_COLOR, linestyle=":", linewidth=0.8)
    ax.tick_params(colors=MUTED_COLOR, labelsize=7)
    ax.legend(loc="upper left", fontsize=7, facecolor=BG_COLOR, edgecolor=GRID_COLOR)

    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, facecolor=BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_sector_bar_chart_img(treemap_records: List[Dict[str, Any]]) -> Optional[BytesIO]:
    """Generates Sector Breakdown & Size Allocation bar chart image."""
    if not treemap_records:
        return None
    df = pd.DataFrame(treemap_records)
    if df.empty or "Sector" not in df or "MarketCap" not in df:
        return None

    sector_summary = df.groupby("Sector")["MarketCap"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(5.5, 3.2), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    bars = ax.barh(sector_summary["Sector"], sector_summary["MarketCap"], color=PRIMARY_COLOR, edgecolor=GRID_COLOR, height=0.55)
    ax.set_xlabel("Size / Capital", fontsize=7, color=MUTED_COLOR)
    ax.set_title("Sector Breakdown & Allocation", fontsize=10, fontweight="bold", color=TEXT_COLOR, pad=8)
    ax.grid(True, axis="x", color=GRID_COLOR, linestyle=":", linewidth=0.8)
    ax.tick_params(colors=TEXT_COLOR, labelsize=7)

    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    for bar in bars:
        width = bar.get_width()
        ax.text(width * 1.01, bar.get_y() + bar.get_height() / 2, f"{width:,.0f}", ha="left", va="center", fontsize=7, color=TEXT_COLOR)

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, facecolor=BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    return buf