import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go


def create_placeholder_figure(text="Select an asset to display analysis"):
    """Creates a pre-themed empty figure with accurate status text to prevent white flashes."""
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": text,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 13, "color": "#94A3B8"}
            }
        ],
        margin=dict(l=10, r=10, t=10, b=10),
        height=380
    )
    return fig


def create_stock_tab():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3(id="stock-title-header", className="fw-bold mb-1"),
                            html.P(id="stock-subtitle-header", className="text-muted mb-3"),
                        ],
                        width=12
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Price & Technical Alignment (EMA 20/50/200, RSI 14)", className="card-title fw-bold mb-3"),
                                    dcc.Graph(
                                        id="price-technicals-chart",
                                        figure=create_placeholder_figure("Select an asset to view Price & Technical Analysis"),
                                        config={"displayModeBar": False}
                                    )
                                ]
                            ),
                            className="executive-card mb-3"
                        ),
                        width=8
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Fundamental Radar (5-Axis)", className="card-title fw-bold mb-3"),
                                    dcc.Graph(
                                        id="radar-chart",
                                        figure=create_placeholder_figure("Select an asset to view Fundamental Radar"),
                                        config={"displayModeBar": False}
                                    )
                                ]
                            ),
                            className="executive-card mb-3"
                        ),
                        width=4
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Peer Comparative Multiples Matrix", className="card-title fw-bold mb-3"),
                                    html.Div(id="peer-table-container")
                                ]
                            ),
                            className="executive-card mb-3"
                        ),
                        width=8
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Automated Decision Support Takeaways", className="card-title fw-bold mb-3"),
                                    html.Div(id="executive-insights-container")
                                ]
                            ),
                            className="executive-card mb-3"
                        ),
                        width=4
                    ),
                ]
            )
        ]
    )


def apply_theme_layout(fig: go.Figure, theme_key: str = "FORMAL_DARK"):
    if theme_key == "LIGHT_CORPORATE":
        bg_color = "#FFFFFF"
        paper_color = "#FFFFFF"
        font_color = "#0F172A"
        grid_color = "#E2E8F0"
    elif theme_key == "CYBORG_TERMINAL":
        bg_color = "#060606"
        paper_color = "#121212"
        font_color = "#00E676"
        grid_color = "rgba(0, 230, 118, 0.2)"
    else:  # FORMAL_DARK
        bg_color = "#1E293B"
        paper_color = "#1E293B"
        font_color = "#F8FAFC"
        grid_color = "#334155"

    fig.update_layout(
        paper_bgcolor=paper_color,
        plot_bgcolor=bg_color,
        font=dict(color=font_color, family="Segoe UI, sans-serif"),
        xaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color),
        yaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color),
    )


def generate_price_technicals_figure(ohlcv_data, technicals, theme_key="FORMAL_DARK"):
    import pandas as pd
    from plotly.subplots import make_subplots

    if not ohlcv_data:
        return create_placeholder_figure("Select an asset to view Price & Technical Analysis")

    df = pd.DataFrame(ohlcv_data)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.75, 0.25]
    )

    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="Price"
    ), row=1, col=1)

    if "EMA_20" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA_20"], name="EMA 20", line=dict(color="#EAB308", width=1.5)), row=1, col=1)
    if "EMA_50" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA_50"], name="EMA 50", line=dict(color="#A855F7", width=1.5)), row=1, col=1)
    if "EMA_200" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA_200"], name="EMA 200", line=dict(color="#EC4899", width=1.5)), row=1, col=1)

    if "RSI_14" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI_14"], name="RSI (14)", line=dict(color="#38BDF8", width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#EF4444", row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#22C55E", row=2, col=1)

    apply_theme_layout(fig, theme_key)
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False,
        height=380,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def generate_radar_figure(radar_scores, theme_key="FORMAL_DARK"):
    categories = ["Valuation", "Profitability", "Growth", "Financial Health", "Technicals"]
    values = [
        radar_scores.get("valuation", 50),
        radar_scores.get("profitability", 50),
        radar_scores.get("growth", 50),
        radar_scores.get("financial_health", 50),
        radar_scores.get("technicals", 50),
    ]

    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(56, 189, 248, 0.25)",
        line=dict(color="#38BDF8", width=2)
    ))

    apply_theme_layout(fig, theme_key)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=30, r=30, t=30, b=30),
        height=380,
        showlegend=False
    )
    return fig