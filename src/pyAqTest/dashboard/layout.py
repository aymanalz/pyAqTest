"""
Dashboard Layout Components
==========================
Contains all layout components for the Batch Slug Test Analysis dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import base64

def get_logo():
    """Get logo as base64"""
    try:
        with open('assets/logo.png', 'rb') as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{logo_b64}"
    except:
        return "💧"  # Fallback to emoji

def create_header():
    """Create the header with logo and title"""
    return html.Div([
        # Logo on the left
        html.Div([
            html.Img(
                src=get_logo(),
                style={
                    "height": "150px", 
                    "background": "transparent",
                    "padding": "0",
                    "border": "none",
                    "outline": "none"
                }
            )
        ], style={"display": "flex", "alignItems": "center", "padding": "10px"}),
        
        # Title on the right
        html.Div([
            dbc.NavbarSimple(
                brand=html.Span(
                    "Batch Slug Test Analysis",
                    style={"fontSize": "24px", "fontWeight": "bold"}
                ),
                color="primary",
                dark=True,
            )
        ], style={"flex": "1"})
        
    ], style={"display": "flex", "alignItems": "center", "backgroundColor": "#f8f9fa"})

def create_upload_tab():
    """Create the data upload tab content"""
    return dbc.Tab(
        label="📁 Input",
        tab_id="upload-tab",
        children=[
            html.Div([
                # Vertical tabs on the left, content on the right
                dbc.Row([
                    # Vertical tabs column (narrow)
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Actions", className="card-title mb-3 text-center"),
                                
                                # Vertical action buttons
                                dbc.ButtonGroup([
                                    dbc.Button([
                                        html.I(className="fas fa-upload me-2"),
                                        "Load"
                                    ], 
                                    id="load-action-btn", 
                                    color="primary", 
                                    className="mb-2 w-100",
                                    size="sm"
                                    ),
                                    
                                    dbc.Button([
                                        html.I(className="fas fa-file-plus me-2"),
                                        "New"
                                    ], 
                                    id="new-action-btn", 
                                    color="success", 
                                    className="mb-2 w-100",
                                    size="sm"
                                    ),
                                    
                                    dbc.Button([
                                        html.I(className="fas fa-download me-2"),
                                        "Save"
                                    ], 
                                    id="save-action-btn", 
                                    color="info", 
                                    className="mb-2 w-100",
                                    size="sm"
                                    )
                                ], 
                                vertical=True,
                                style={"width": "100%"}
                                )
                            ])
                        ])
                    ], width=2),
                    
                    # Main content column (wide)
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                # Tab content
                                html.Div(id="action-tab-content", children=[
                                    # Status section
                                    dbc.Row([
                                        dbc.Col([
                                            html.H6("Status", className="mb-3"),
                                            html.Div(id='upload-status', children="No batch file loaded"),
                                            html.Hr(),
                                            html.H6("Recent Actions:", className="mt-3"),
                                            html.Div(id='action-log', children="No actions yet")
                                        ], width=6),
                                        
                                        dbc.Col([
                                            html.H6("File Information", className="mb-3"),
                                            html.Div(id='file-info', children="No files selected"),
                                            html.Hr(),
                                            html.H6("Analysis Options:", className="mt-3"),
                                            html.Div(id='analysis-options', children="Select files to see options")
                                        ], width=6)
                                    ])
                                ]),
                                
                                # Hidden file input for .ini files
                                dcc.Upload(
                                    id="file-input",
                                    children=html.Div(),
                                    style={"display": "none"},
                                    accept=".ini",
                                    multiple=False
                                )
                            ])
                        ])
                    ], width=10)
                ]),
                
                html.Div(id='output-data-upload'),
            ])
        ]
    )

def create_analysis_tab():
    """Create the analysis tab content"""
    return dbc.Tab(
        label="📊 Analysis",
        tab_id="analysis-tab",
        children=[
            html.Div([
                html.H2("Slug Test Analysis", className="mb-4"),
                html.P("View and analyze your slug test data", className="text-muted mb-4"),
                
                # Analysis controls
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
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
                    ], width=4),
                    
                    dbc.Col([
                        dcc.Graph(
                            id='analysis-plot',
                            style={'height': '500px', 'width': '100%'},
                            config={'displayModeBar': True, 'displaylogo': False}
                        )
                    ], width=8)
                ])
            ])
        ]
    )

def create_results_tab():
    """Create the results tab content"""
    return dbc.Tab(
        label="📈 Results",
        tab_id="results-tab",
        children=[
            html.Div([
                html.H2("Analysis Results", className="mb-4"),
                html.P("View detailed results and export data", className="text-muted mb-4"),
                
                # Results summary
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Summary Statistics", className="card-title"),
                                html.Div(id="summary-stats")
                            ])
                        ])
                    ], width=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Export Options", className="card-title"),
                                dbc.ButtonGroup([
                                    dbc.Button("Export CSV", color="success", className="me-2"),
                                    dbc.Button("Export PDF", color="info", className="me-2"),
                                    dbc.Button("Export Excel", color="warning")
                                ], vertical=True)
                            ])
                        ])
                    ], width=6)
                ], className="mb-4"),
                
                # Detailed results table
                html.Div(id="results-table")
            ])
        ]
    )

def create_settings_tab():
    """Create the settings tab content"""
    return dbc.Tab(
        label="⚙️ Settings",
        tab_id="settings-tab",
        children=[
            html.Div([
                html.H2("Application Settings", className="mb-4"),
                html.P("Configure analysis parameters and preferences", className="text-muted mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
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
                    ], width=6),
                    
                    dbc.Col([
                        dbc.Card([
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
                    ], width=6)
                ])
            ])
        ]
    )

def create_main_layout():
    """Create the main dashboard layout"""
    return html.Div([
        # Header
        create_header(),
        
        # Main content area with tabs
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Tab navigation with custom styling
                    dbc.Tabs([
                        create_upload_tab(),
                        create_analysis_tab(),
                        create_results_tab(),
                        create_settings_tab()
                    ], id="main-tabs", active_tab="upload-tab", 
                    style={
                        "fontSize": "18px",
                        "fontWeight": "bold"
                    })
                    
                ], width=12)
            ])
        ], fluid=True)
    ])
