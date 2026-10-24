import base64
import io
import json
from pathlib import Path
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, dash_table
import pandas as pd
import plotly.graph_objects as go

from components.navbar import create_navbar
from components.sidebar import create_sidebar
from components.tab_market import create_market_tab, generate_market_treemap_figure, generate_sector_heatmap_figure, \
    generate_market_breadth_ui
from components.tab_stock import create_stock_tab, generate_price_technicals_figure, generate_radar_figure, \
    apply_theme_layout
from components.tab_portfolio import create_portfolio_tab, generate_correlation_figure

from core.symbol_search import search_global_symbols
from core.data_engine import fetch_market_and_fundamental_data, resolve_global_ticker
from core.market_engine import fetch_market_radar_data
from core.technicals import compute_technical_indicators
from core.fundamentals import calculate_radar_scores, generate_peer_comparison_matrix
from core.risk_engine import compute_portfolio_risk_metrics
from core.insight_engine import generate_executive_insights
from core.pdf_exporter import generate_pdf_bytes
from core.excel_exporter import generate_excel_bytes

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.SLATE,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
    ],
    suppress_callback_exceptions=True,
    title="The Executive Terminal"
)

app.layout = html.Div(
    [
        html.Link(id="theme-stylesheet", rel="stylesheet", href="/assets/theme_dark.css"),
        dcc.Store(id="session-store", storage_type="memory"),
        dcc.Download(id="download-pdf"),
        dcc.Download(id="download-excel"),
        create_navbar(),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(create_sidebar(), width=3),
                        dbc.Col(
                            dcc.Loading(
                                id="master-fetching-indicator",
                                type="circle",
                                color="#38BDF8",
                                children=[
                                    html.Div(id="fetch-status-target", style={"display": "none"}),
                                    dbc.Tabs(
                                        [
                                            dbc.Tab(create_market_tab(), label="Market Radar", tab_id="tab-market"),
                                            dbc.Tab(create_stock_tab(), label="Stock X-Ray", tab_id="tab-stock"),
                                            dbc.Tab(create_portfolio_tab(), label="Portfolio Terminal",
                                                    tab_id="tab-portfolio"),
                                        ],
                                        id="active-tab-switcher",
                                        active_tab="tab-stock"
                                    )
                                ]
                            ),
                            width=9
                        )
                    ]
                )
            ],
            fluid=True
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Executive Intelligence Briefing")),
                dbc.ModalBody(id="executive-modal-body"),
                dbc.ModalFooter(
                    [
                        dbc.Button([html.I(className="bi bi-file-earmark-pdf me-1"), "Export PDF"], id="btn-export-pdf",
                                   color="danger", size="sm", className="me-2"),
                        dbc.Button([html.I(className="bi bi-file-earmark-excel me-1"), "Export Excel"],
                                   id="btn-export-excel", color="success", size="sm", className="me-2"),
                        dbc.Button("Close", id="close-modal-btn", className="ms-auto", color="secondary", size="sm")
                    ]
                ),
            ],
            id="executive-modal",
            size="lg",
            is_open=False,
        )
    ]
)


def get_datatable_styles(theme_key):
    if theme_key == "LIGHT_CORPORATE":
        return {
            "style_header": {"backgroundColor": "#F1F5F9", "color": "#0F172A", "fontWeight": "bold",
                             "border": "1px solid #E2E8F0"},
            "style_data": {"backgroundColor": "#FFFFFF", "color": "#0F172A", "border": "1px solid #E2E8F0"},
            "style_cell": {"textAlign": "left", "padding": "8px", "fontSize": "0.85rem", "fontFamily": "sans-serif"}
        }
    elif theme_key == "CYBORG_TERMINAL":
        return {
            "style_header": {"backgroundColor": "#1A1A1A", "color": "#00E676", "fontWeight": "bold",
                             "border": "1px solid #00E676"},
            "style_data": {"backgroundColor": "#060606", "color": "#00E676", "border": "1px solid rgba(0,230,118,0.3)"},
            "style_cell": {"textAlign": "left", "padding": "8px", "fontSize": "0.85rem", "fontFamily": "monospace"}
        }
    else:  # FORMAL_DARK
        return {
            "style_header": {"backgroundColor": "#0F172A", "color": "#F8FAFC", "fontWeight": "bold",
                             "border": "1px solid #334155"},
            "style_data": {"backgroundColor": "#1E293B", "color": "#F8FAFC", "border": "1px solid #334155"},
            "style_cell": {"textAlign": "left", "padding": "8px", "fontSize": "0.85rem", "fontFamily": "sans-serif"}
        }


@app.callback(
    Output("ticker-dropdown", "options"),
    Input("ticker-dropdown", "search_value"),
    State("ticker-dropdown", "options")
)
def update_autocomplete_options(search_value, current_options):
    if not search_value or len(search_value.strip()) < 1:
        return current_options or []

    return search_global_symbols(search_value)


@app.callback(
    Output("ticker-dropdown", "value"),
    [
        Input("btn-rel", "n_clicks"),
        Input("btn-tcs", "n_clicks"),
        Input("btn-infy", "n_clicks"),
        Input("btn-aapl", "n_clicks"),
        Input("btn-nvda", "n_clicks"),
        Input("btn-msft", "n_clicks")
    ],
    State("ticker-dropdown", "value")
)
def sync_watchlist_buttons(c1, c2, c3, c4, c5, c6, current_val):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_val or "RELIANCE.NS"

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    mapping = {
        "btn-rel": "RELIANCE.NS",
        "btn-tcs": "TCS.NS",
        "btn-infy": "INFY.NS",
        "btn-aapl": "AAPL",
        "btn-nvda": "NVDA",
        "btn-msft": "MSFT"
    }
    return mapping.get(triggered_id, current_val)


# Master Session Store Update Callback (Triggers Spinner Instantly on Action)
@app.callback(
    [
        Output("session-store", "data"),
        Output("fetch-status-target", "children")
    ],
    [
        Input("ticker-dropdown", "value"),
        Input("upload-portfolio", "contents")
    ],
    State("upload-portfolio", "filename")
)
def update_master_session_store(selected_ticker, upload_contents, upload_filename):
    active_ticker = selected_ticker or "RELIANCE.NS"

    portfolio_df = pd.DataFrame()
    if upload_contents:
        try:
            content_type, content_string = upload_contents.split(",")
            decoded = base64.b64decode(content_string)
            portfolio_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        except Exception:
            portfolio_path = Path("data/portfolio.csv")
            if portfolio_path.exists():
                portfolio_df = pd.read_csv(portfolio_path)
    else:
        portfolio_path = Path("data/portfolio.csv")
        if portfolio_path.exists():
            portfolio_df = pd.read_csv(portfolio_path)

    raw_payload = fetch_market_and_fundamental_data(active_ticker)

    df_ohlcv = pd.DataFrame(raw_payload["ohlcv"])
    clean_ohlcv, technicals_summary = compute_technical_indicators(df_ohlcv)

    radar_scores = calculate_radar_scores(
        raw_payload["fundamentals"],
        rsi_14=technicals_summary.get("rsi_14", 50.0)
    )

    peer_df = generate_peer_comparison_matrix(raw_payload["ticker"], raw_payload["fundamentals"])

    benchmark_symbol = raw_payload["benchmark_symbol"]
    price_history_dict = {raw_payload["ticker"]: clean_ohlcv}

    bench_payload = fetch_market_and_fundamental_data(benchmark_symbol)
    bench_ohlcv, _ = compute_technical_indicators(pd.DataFrame(bench_payload["ohlcv"]))
    price_history_dict[benchmark_symbol] = bench_ohlcv

    if not portfolio_df.empty:
        for p_ticker in portfolio_df["Ticker"].unique():
            p_resolved, _ = resolve_global_ticker(p_ticker)
            if p_resolved not in price_history_dict:
                p_payload = fetch_market_and_fundamental_data(p_resolved)
                p_df, _ = compute_technical_indicators(pd.DataFrame(p_payload["ohlcv"]))
                price_history_dict[p_resolved] = p_df

    risk_metrics = compute_portfolio_risk_metrics(
        portfolio_df,
        price_history_dict,
        benchmark_symbol=benchmark_symbol
    )

    insights = generate_executive_insights(
        raw_payload["ticker"],
        raw_payload["fundamentals"],
        technicals_summary,
        risk_metrics
    )

    region = "IN" if ".NS" in raw_payload["ticker"] or ".BO" in raw_payload["ticker"] else "US"
    market_radar_payload = fetch_market_radar_data(
        region=region,
        portfolio_summary=risk_metrics.get("summary_table"),
        price_history_dict=price_history_dict
    )

    session_payload = {
        "ticker": raw_payload["ticker"],
        "company_name": raw_payload["company_name"],
        "currency_symbol": raw_payload["currency_symbol"],
        "benchmark_symbol": benchmark_symbol,
        "dhs": raw_payload["dhs"],
        "ohlcv": clean_ohlcv.to_dict(orient="records"),
        "technicals": technicals_summary,
        "fundamentals": raw_payload["fundamentals"],
        "radar_scores": radar_scores,
        "peer_matrix": peer_df.to_dict(orient="records"),
        "risk_metrics": risk_metrics,
        "insights": insights,
        "market_radar": market_radar_payload
    }

    return session_payload, "ready"


@app.callback(
    Output("theme-stylesheet", "href"),
    Input("theme-selector", "value")
)
def switch_theme_stylesheet(theme_key):
    if theme_key == "LIGHT_CORPORATE":
        return "/assets/theme_light.css"
    elif theme_key == "CYBORG_TERMINAL":
        return "/assets/theme_cyborg.css"
    return "/assets/theme_dark.css"


@app.callback(
    Output("dhs-badge-container", "children"),
    Input("session-store", "data")
)
def update_dhs_badge(data):
    if not data or "dhs" not in data:
        return html.Div()

    dhs = data["dhs"]
    return dbc.Badge(
        f"Data Health: {dhs.get('dhs_score')}% ({dhs.get('status')})",
        color=dhs.get("badge_color", "info"),
        className="dhs-badge p-2 fw-semibold"
    )


@app.callback(
    [
        Output("stock-title-header", "children"),
        Output("stock-subtitle-header", "children"),
        Output("price-technicals-chart", "figure"),
        Output("radar-chart", "figure"),
        Output("peer-table-container", "children"),
        Output("executive-insights-container", "children"),
        Output("market-treemap-graph", "figure"),
        Output("sector-rotation-heatmap", "figure"),
        Output("market-breadth-container", "children"),
        Output("portfolio-kpi-cards-container", "children"),
        Output("correlation-matrix-graph", "figure"),
        Output("portfolio-growth-chart", "figure"),
        Output("portfolio-table-container", "children")
    ],
    [
        Input("session-store", "data"),
        Input("theme-selector", "value")
    ]
)
def render_dashboard_views(data, theme_key):
    if not data:
        empty_fig = go.Figure()
        apply_theme_layout(empty_fig, theme_key)
        return "", "", empty_fig, empty_fig, html.Div(), html.Div(), empty_fig, empty_fig, html.Div(), [], empty_fig, empty_fig, html.Div()

    ticker = data["ticker"]
    company = data["company_name"]
    curr = data.get("currency_symbol", "₹")
    technicals = data["technicals"]

    title = f"{ticker} - {company}"
    subtitle = f"Price: {curr}{technicals.get('current_price'):,} | RSI: {technicals.get('rsi_14')} | Cross: {technicals.get('ema_cross')}"

    fig_price = generate_price_technicals_figure(data["ohlcv"], technicals, theme_key)
    fig_radar = generate_radar_figure(data["radar_scores"], theme_key)

    radar_payload = data.get("market_radar")
    fig_treemap = generate_market_treemap_figure(radar_payload, theme_key)
    fig_sector = generate_sector_heatmap_figure(radar_payload, theme_key)
    breadth_ui = generate_market_breadth_ui(radar_payload)

    dt_styles = get_datatable_styles(theme_key)

    peer_df = pd.DataFrame(data["peer_matrix"])
    peer_table = dash_table.DataTable(
        data=peer_df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in peer_df.columns],
        style_header=dt_styles["style_header"],
        style_data=dt_styles["style_data"],
        style_cell=dt_styles["style_cell"],
        style_table={"overflowX": "auto"}
    )

    insights_list = html.Ul([html.Li(dcc.Markdown(item)) for item in data["insights"]], className="mb-0 ps-3")

    risk = data["risk_metrics"]
    bench_name = data.get("benchmark_symbol", "^NSEI")
    kpi_cards = [
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Total Invested", className="text-muted"),
                                       html.H4(f"{curr}{risk.get('total_invested'):,}", className="fw-bold mb-0")]),
                         className="executive-card"), width=3),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Current Value", className="text-muted"),
                                       html.H4(f"{curr}{risk.get('current_value'):,}", className="fw-bold mb-0")]),
                         className="executive-card"), width=3),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Total P&L", className="text-muted"),
                                       html.H4(f"{curr}{risk.get('total_pnl'):,} ({risk.get('pnl_pct')}%)",
                                               className="fw-bold mb-0 text-success" if risk.get("total_pnl",
                                                                                                 0) >= 0 else "fw-bold mb-0 text-danger")]),
                         className="executive-card"), width=3),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small(f"Beta ({bench_name}) / Sharpe", className="text-muted"),
                                       html.H4(f"β: {risk.get('portfolio_beta')} | SR: {risk.get('sharpe_ratio')}",
                                               className="fw-bold mb-0 text-info")]), className="executive-card"),
                width=3),
    ]

    fig_corr = generate_correlation_figure(risk["correlation_matrix"], theme_key)

    fig_growth = go.Figure()
    port_line_color = "#00E676" if theme_key == "CYBORG_TERMINAL" else "#22C55E"
    bench_line_color = "#00E5FF" if theme_key == "CYBORG_TERMINAL" else "#94A3B8"

    fig_growth.add_trace(go.Scatter(x=[1, 2, 3, 4, 5], y=[100, 104, 102, 108, 112], name="Portfolio",
                                    line=dict(color=port_line_color, width=2)))
    fig_growth.add_trace(go.Scatter(x=[1, 2, 3, 4, 5], y=[100, 101, 103, 105, 107], name=f"Benchmark ({bench_name})",
                                    line=dict(color=bench_line_color, dash="dash")))
    apply_theme_layout(fig_growth, theme_key)
    fig_growth.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320)

    port_df = pd.DataFrame(risk.get("summary_table", []))
    port_table = dash_table.DataTable(
        data=port_df.to_dict("records") if not port_df.empty else [],
        columns=[{"name": i, "id": i} for i in port_df.columns] if not port_df.empty else [],
        style_header=dt_styles["style_header"],
        style_data=dt_styles["style_data"],
        style_cell=dt_styles["style_cell"],
        style_table={"overflowX": "auto"}
    )

    return (
        title, subtitle, fig_price, fig_radar, peer_table, insights_list,
        fig_treemap, fig_sector, breadth_ui, kpi_cards, fig_corr, fig_growth, port_table
    )


@app.callback(
    Output("executive-modal", "is_open"),
    [Input("open-report-btn", "n_clicks"), Input("close-modal-btn", "n_clicks")],
    [State("executive-modal", "is_open")]
)
def toggle_executive_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("executive-modal-body", "children"),
    Input("session-store", "data")
)
def render_executive_report_modal(data):
    if not data:
        return html.Div("No active session data.")

    ticker = data["ticker"]
    curr = data.get("currency_symbol", "₹")
    risk = data["risk_metrics"]

    return html.Div(
        [
            html.H5(f"Executive Intelligence Summary: {ticker}", className="fw-bold mb-3"),
            html.P(f"Data Health Index: {data['dhs']['dhs_score']}% ({data['dhs']['status']})",
                   className="fw-semibold text-info"),
            html.Hr(),
            html.H6("Core Decision Takeaways:", className="fw-bold"),
            html.Ul([html.Li(dcc.Markdown(item)) for item in data["insights"]]),
            html.Hr(),
            html.H6("Portfolio Standing:", className="fw-bold"),
            html.P(
                f"Capital Invested: {curr}{risk.get('total_invested'):,} | Market Value: {curr}{risk.get('current_value'):,}"),
            html.P(
                f"Systematic Exposure (Beta vs {data.get('benchmark_symbol')}): {risk.get('portfolio_beta')} | Sharpe Ratio: {risk.get('sharpe_ratio')}")
        ]
    )


@app.callback(
    Output("download-pdf", "data"),
    Input("btn-export-pdf", "n_clicks"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def export_pdf_handler(n_clicks, session_data):
    if not n_clicks or not session_data:
        return dash.no_update
    ticker = session_data.get("ticker", "ASSET")
    pdf_bytes = generate_pdf_bytes(session_data)
    return dcc.send_bytes(pdf_bytes, filename=f"Executive_Report_{ticker}.pdf")


@app.callback(
    Output("download-excel", "data"),
    Input("btn-export-excel", "n_clicks"),
    State("session-store", "data"),
    prevent_initial_call=True
)
def export_excel_handler(n_clicks, session_data):
    if not n_clicks or not session_data:
        return dash.no_update
    ticker = session_data.get("ticker", "ASSET")
    excel_bytes = generate_excel_bytes(session_data)
    return dcc.send_bytes(excel_bytes, filename=f"Executive_Terminal_{ticker}.xlsx")


if __name__ == "__main__":
    app.run(debug=True, port=8050)