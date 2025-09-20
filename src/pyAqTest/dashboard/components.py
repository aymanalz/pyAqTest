"""
Dashboard Components
==================
Contains reusable UI components for the Batch Slug Test Analysis dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

def create_upload_area():
    """Create the file upload area component"""
    return dcc.Upload(
        id='upload-data',
        children=html.Div([
            html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
            html.Br(),
            'Drag and Drop or ',
            html.A('Select Files', className="btn btn-primary")
        ]),
        style={
            'width': '100%',
            'height': '200px',
            'lineHeight': '200px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '20px 0',
            'backgroundColor': '#f8f9fa',
            'borderColor': '#dee2e6'
        },
        multiple=True
    )

def create_analysis_controls():
    """Create the analysis controls component"""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Analysis Parameters", className="card-title"),
            dbc.Label("Well Name:"),
            dbc.Input(id="well-name", placeholder="Enter well name"),
            html.Br(),
            dbc.Label("Test Date:"),
            dbc.Input(id="test-date", type="date"),
            html.Br(),
            dbc.Button("Run Analysis", id="run-analysis", color="primary", className="mt-2")
        ])
    ])

def create_analysis_plot():
    """Create the analysis plot component"""
    return dcc.Graph(
        id='analysis-plot',
        style={'height': '500px', 'width': '100%'},
        config={'displayModeBar': True, 'displaylogo': False}
    )

def create_summary_card():
    """Create the summary statistics card"""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Summary Statistics", className="card-title"),
            html.Div(id="summary-stats")
        ])
    ])

def create_export_card():
    """Create the export options card"""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Export Options", className="card-title"),
            dbc.ButtonGroup([
                dbc.Button("Export CSV", color="success", className="me-2"),
                dbc.Button("Export PDF", color="info", className="me-2"),
                dbc.Button("Export Excel", color="warning")
            ], vertical=True)
        ])
    ])

def create_analysis_settings_card():
    """Create the analysis settings card"""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Analysis Settings", className="card-title"),
            dbc.Label("Default Analysis Method:"),
            dbc.Select(
                id="analysis-method",
                options=[
                    {"label": "Bouwer & Rice", "value": "bouwer_rice"},
                    {"label": "Butler", "value": "butler"},
                    {"label": "Hvorslev", "value": "hvorslev"}
                ],
                value="bouwer_rice"
            ),
            html.Br(),
            dbc.Label("Time Units:"),
            dbc.Select(
                id="time-units",
                options=[
                    {"label": "Minutes", "value": "minutes"},
                    {"label": "Hours", "value": "hours"},
                    {"label": "Days", "value": "days"}
                ],
                value="minutes"
            ),
            html.Br(),
            dbc.Label("Head Units:"),
            dbc.Select(
                id="head-units",
                options=[
                    {"label": "Feet", "value": "feet"},
                    {"label": "Meters", "value": "meters"}
                ],
                value="feet"
            )
        ])
    ])

def create_display_settings_card():
    """Create the display settings card"""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Display Settings", className="card-title"),
            dbc.Label("Theme:"),
            dbc.Select(
                id="theme-select",
                options=[
                    {"label": "Light", "value": "light"},
                    {"label": "Dark", "value": "dark"},
                    {"label": "Auto", "value": "auto"}
                ],
                value="light"
            ),
            html.Br(),
            dbc.Label("Graph Style:"),
            dbc.Select(
                id="graph-style",
                options=[
                    {"label": "Plotly", "value": "plotly"},
                    {"label": "Matplotlib", "value": "matplotlib"},
                    {"label": "Seaborn", "value": "seaborn"}
                ],
                value="plotly"
            ),
            html.Br(),
            dbc.Button("Save Settings", color="primary", className="mt-3")
        ])
    ])

def create_results_table():
    """Create the results table component"""
    return dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Parameter"),
                html.Th("Value"),
                html.Th("Units"),
                html.Th("Confidence")
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td("Hydraulic Conductivity"),
                html.Td("2.5 × 10⁻⁴"),
                html.Td("ft/s"),
                html.Td("95%")
            ]),
            html.Tr([
                html.Td("Transmissivity"),
                html.Td("1.2 × 10⁻³"),
                html.Td("ft²/s"),
                html.Td("95%")
            ]),
            html.Tr([
                html.Td("Storage Coefficient"),
                html.Td("0.001"),
                html.Td("dimensionless"),
                html.Td("90%")
            ])
        ])
    ], striped=True, bordered=True, hover=True)
