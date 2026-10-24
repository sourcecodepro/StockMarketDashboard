import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
from components.tab_stock import apply_theme_layout, create_placeholder_figure


def create_market_tab():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Sector Heatmap & Market Treemap", className="card-title fw-bold mb-3"),
                                    dcc.Graph(
                                        id="market-treemap-graph",
                                        figure=create_placeholder_figure("Select region or asset to view Market Treemap"),
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
                                    html.H5("Market Breadth & Liquidity", className="card-title fw-bold mb-3"),
                                    html.Div(id="market-breadth-container")
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
                                    html.H5("Multi-Period Sector Performance Matrix", className="card-title fw-bold mb-3"),
                                    dcc.Graph(
                                        id="sector-rotation-heatmap",
                                        figure=create_placeholder_figure("Select region or asset to view Sector Rotation Matrix"),
                                        config={"displayModeBar": False}
                                    )
                                ]
                            ),
                            className="executive-card mb-3"
                        ),
                        width=12
                    )
                ]
            )
        ]
    )


def generate_market_treemap_figure(radar_payload=None, theme_key="FORMAL_DARK"):
    if not radar_payload or "treemap" not in radar_payload or not radar_payload["treemap"]:
        return create_placeholder_figure("Select region or asset to view Market Treemap")

    records = radar_payload["treemap"]
    labels = []
    parents = []
    values = []
    colors = []

    sectors = sorted(list(set(r["Sector"] for r in records)))
    for sec in sectors:
        labels.append(sec)
        parents.append("")
        values.append(0)
        colors.append(0.0)

    for r in records:
        labels.append(r["Company"])
        parents.append(r["Sector"])
        values.append(r["MarketCap"])
        colors.append(r["Performance"])

    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(
                colors=colors,
                colorscale="RdYlGn",
                cmid=0,
                showscale=True,
                colorbar=dict(title="1D %")
            ),
            textinfo="label+value+percent parent"
        )
    )
    apply_theme_layout(fig, theme_key)
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=380
    )
    return fig


def generate_sector_heatmap_figure(radar_payload=None, theme_key="FORMAL_DARK"):
    if not radar_payload or "sector_heatmap" not in radar_payload:
        return create_placeholder_figure("Select region or asset to view Sector Rotation Matrix")

    sec_data = radar_payload["sector_heatmap"]
    sectors = sec_data.get("sectors", [])
    periods = sec_data.get("periods", ["1D", "1W", "1M", "YTD"])
    z_values = sec_data.get("matrix", [])

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=periods,
            y=sectors,
            colorscale="RdYlGn",
            zmid=0,
            colorbar=dict(title="% Change")
        )
    )
    apply_theme_layout(fig, theme_key)
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=20),
        height=320
    )
    return fig


def generate_market_breadth_ui(radar_payload=None):
    if not radar_payload or "breadth" not in radar_payload:
        adv, dec, ad_ratio, vol_anom, h_52, l_52 = 0, 0, 0.0, 0, 0, 0
    else:
        b = radar_payload["breadth"]
        adv = b.get("advances", 0)
        dec = b.get("declines", 0)
        ad_ratio = b.get("ad_ratio", 1.0)
        vol_anom = b.get("vol_anomalies", 0)
        h_52 = b.get("highs_52w", 0)
        l_52 = b.get("lows_52w", 0)

    ad_status = "Bullish" if ad_ratio >= 1.0 else "Bearish"
    ad_color = "text-success" if ad_ratio >= 1.0 else "text-danger"

    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([html.Small("Advance / Decline", className="text-muted d-block"), html.Strong(f"{adv} / {dec} ({ad_status})", className=ad_color)]), width=6),
            dbc.Col(html.Div([html.Small("Volume Anomalies", className="text-muted d-block"), html.Strong(f"{vol_anom} Stocks (>200%)", className="text-warning")]), width=6),
        ], className="g-2 mb-3"),
        dbc.Row([
            dbc.Col(html.Div([html.Small("52-Wk Highs Near", className="text-muted d-block"), html.Strong(f"{h_52}", className="text-success")]), width=6),
            dbc.Col(html.Div([html.Small("52-Wk Lows Near", className="text-muted d-block"), html.Strong(f"{l_52}", className="text-danger")]), width=6),
        ], className="g-2")
    ])