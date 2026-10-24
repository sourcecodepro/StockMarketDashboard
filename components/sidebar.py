import dash_bootstrap_components as dbc
from dash import dcc, html


def create_sidebar():
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H6("ASSET SELECTION (AUTOCOMPLETE)", className="card-subtitle mb-2 text-muted fw-bold"),
                        dcc.Dropdown(
                            id="ticker-dropdown",
                            options=[
                                {"label": "RELIANCE.NS - Reliance Industries Ltd (NSE)", "value": "RELIANCE.NS"},
                                {"label": "TCS.NS - Tata Consultancy Services Ltd (NSE)", "value": "TCS.NS"},
                                {"label": "INFY.NS - Infosys Ltd (NSE)", "value": "INFY.NS"},
                                {"label": "TATAMOTORS.NS - Tata Motors Ltd (NSE)", "value": "TATAMOTORS.NS"},
                                {"label": "NVDA - NVIDIA Corporation (NASDAQ)", "value": "NVDA"},
                                {"label": "AAPL - Apple Inc. (NASDAQ)", "value": "AAPL"},
                                {"label": "MSFT - Microsoft Corporation (NASDAQ)", "value": "MSFT"},
                            ],
                            value="RELIANCE.NS",
                            placeholder="Type stock symbol or name (e.g. Tata, Reliance, Nvidia)...",
                            searchable=True,
                            clearable=False,
                            className="mb-3"
                        ),
                        html.H6("INDIAN WATCHLIST (NSE)", className="card-subtitle mb-2 text-muted fw-bold"),
                        dbc.ButtonGroup(
                            [
                                dbc.Button("RELIANCE", id="btn-rel", color="outline-info", size="sm", n_clicks=0),
                                dbc.Button("TCS", id="btn-tcs", color="outline-info", size="sm", n_clicks=0),
                                dbc.Button("INFY", id="btn-infy", color="outline-info", size="sm", n_clicks=0),
                            ],
                            className="w-100 mb-3",
                            size="sm"
                        ),
                        html.H6("GLOBAL WATCHLIST (US)", className="card-subtitle mb-2 text-muted fw-bold"),
                        dbc.ButtonGroup(
                            [
                                dbc.Button("NVDA", id="btn-nvda", color="outline-secondary", size="sm", n_clicks=0),
                                dbc.Button("AAPL", id="btn-aapl", color="outline-secondary", size="sm", n_clicks=0),
                                dbc.Button("MSFT", id="btn-msft", color="outline-secondary", size="sm", n_clicks=0),
                            ],
                            className="w-100 mb-3",
                            size="sm"
                        ),
                        html.Hr(className="my-3"),
                        html.H6("PORTFOLIO IMPORT", className="card-subtitle mb-2 text-muted fw-bold"),
                        dcc.Upload(
                            id="upload-portfolio",
                            children=html.Div(
                                [
                                    html.I(className="bi bi-cloud-arrow-up fs-4 d-block mb-1 text-primary"),
                                    "Drop or ",
                                    html.A("Select CSV", className="text-primary text-decoration-underline")
                                ]
                            ),
                            style={
                                "width": "100%",
                                "height": "80px",
                                "lineHeight": "20px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "6px",
                                "textAlign": "center",
                                "padding": "12px",
                                "cursor": "pointer"
                            },
                            multiple=False
                        ),
                        html.Div(id="upload-status", className="form-text mt-2 text-success")
                    ]
                ),
                className="executive-card mb-3"
            )
        ]
    )