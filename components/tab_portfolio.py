import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
from components.tab_stock import apply_theme_layout, create_placeholder_figure


def create_portfolio_tab():
    return html.Div(
        [
            dbc.Row(id="portfolio-kpi-cards-container", className="mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Cross-Asset Pearson Correlation Matrix", className="card-title fw-bold mb-3"),
                                    dcc.Graph(
                                        id="correlation-matrix-graph",
                                        figure=create_placeholder_figure("Upload portfolio CSV to view Correlation Matrix"),
                                        config={"displayModeBar": False}
                                    )
                                ]
                            ),
                            className="executive-card mb-3"
                        ),
                        width=6
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Cumulative Portfolio Growth vs Benchmark", className="card-title fw-bold mb-3"),
                                    dcc.Graph(
                                        id="portfolio-growth-chart",
                                        figure=create_placeholder_figure("Upload portfolio CSV to view Growth Performance"),
                                        config={"displayModeBar": False}
                                    )
                                ]
                            ),
                            className="executive-card mb-3"
                        ),
                        width=6
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Portfolio Position Breakdown & Risk Metrics", className="card-title fw-bold mb-3"),
                                    html.Div(id="portfolio-table-container")
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


def generate_correlation_figure(corr_matrix, theme_key="FORMAL_DARK"):
    if not corr_matrix:
        return create_placeholder_figure("Upload portfolio CSV to view Correlation Matrix")

    tickers = list(corr_matrix.keys())
    z_vals = [[corr_matrix[t1].get(t2, 0.0) for t2 in tickers] for t1 in tickers]

    fig = go.Figure(
        data=go.Heatmap(
            z=z_vals,
            x=tickers,
            y=tickers,
            colorscale="YlGnBu",
            zmin=-1,
            zmax=1,
            colorbar=dict(title="Correlation")
        )
    )
    apply_theme_layout(fig, theme_key)
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=320
    )
    return fig