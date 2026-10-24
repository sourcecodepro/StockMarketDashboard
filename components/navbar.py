import dash_bootstrap_components as dbc
from dash import dcc, html


def create_navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.I(className="bi bi-graph-up-arrow me-2 text-primary")),
                            dbc.Col(
                                dbc.NavbarBrand(
                                    "THE EXECUTIVE TERMINAL",
                                    className="ms-2 fw-bold text-uppercase",
                                    style={"letterSpacing": "0.1em", "fontSize": "1.25rem"}
                                )
                            ),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="#",
                    style={"textDecoration": "none"},
                ),
                dbc.Nav(
                    [
                        dbc.NavItem(
                            html.Div(
                                id="dhs-badge-container",
                                className="me-3 d-flex align-items-center"
                            )
                        ),
                        dbc.NavItem(
                            dbc.Select(
                                id="theme-selector",
                                options=[
                                    {"label": "Formal Dark (Slate)", "value": "FORMAL_DARK"},
                                    {"label": "Corporate Light", "value": "LIGHT_CORPORATE"},
                                    {"label": "Cyborg Terminal", "value": "CYBORG_TERMINAL"},
                                ],
                                value="FORMAL_DARK",
                                style={"width": "190px"},
                                size="sm",
                                className="me-2"
                            )
                        ),
                        dbc.NavItem(
                            dbc.Button(
                                [html.I(className="bi bi-file-earmark-text me-1"), "Executive Report"],
                                id="open-report-btn",
                                color="outline-info",
                                size="sm",
                                className="fw-semibold"
                            )
                        ),
                    ],
                    className="ms-auto d-flex align-items-center",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="mb-3 border-bottom border-secondary",
    )