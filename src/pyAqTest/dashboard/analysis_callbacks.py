"""
Analysis Tab Callbacks
======================
Callbacks specifically for the Analysis tab functionality.
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from .data_storage import get_data_storage


def register_analysis_callbacks(app):
    """Register analysis-specific callbacks"""
    
    @app.callback(
        dash.dependencies.Output('test-selection-card', 'children'),
        [dash.dependencies.Input('batch-table-info', 'children')],
        prevent_initial_call=True
    )
    def create_test_selection_card(batch_table_children):
        """Create the test selection card with dropdown and run button"""
        data_storage = get_data_storage()
        
        if 'csv_batch_data' in data_storage and data_storage['csv_batch_data'] is not None:
            df = data_storage['csv_batch_data']
            
            # Check if 'field' column exists and transpose
            if 'field' in df.columns:
                df_t = df.set_index("field").transpose()
                
                # Get unique test IDs from the transposed dataframe
                if 'test_id' in df_t.columns:
                    unique_tests = df_t['test_id'].unique().tolist()
                    test_options = [{"label": str(test), "value": str(test)} for test in unique_tests]
                    
                    return dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                # Left side - Test selection dropdown
                                dbc.Col([
                                    dbc.Label("Select Tests to Run:", className="fw-bold mb-2"),
                                    dcc.Dropdown(
                                        id="test-selector-dropdown",
                                        options=test_options,
                                        placeholder="Choose tests to analyze...",
                                        multi=True,
                                        style={"fontSize": "14px"}
                                    ),
                                    html.Small("Available tests from CSV data", className="text-muted mt-1")
                                ], width=8),
                                
                                # Right side - Run analysis button
                                dbc.Col([
                                    dbc.Label("Analysis Control:", className="fw-bold mb-2"),
                                    dbc.ButtonGroup([
                                        dbc.Button([
                                            html.I(className="fas fa-play me-2"),
                                            "Run Analysis"
                                        ], 
                                        id="run-analysis-btn", 
                                        color="primary", 
                                        size="lg",
                                        className="w-100"
                                        )
                                    ], vertical=True),
                                    html.Small("Click to start analysis", className="text-muted mt-1")
                                ], width=4)
                            ])
                        ])
                    ], className="mb-4")
                else:
                    return dbc.Alert([
                        html.H5("⚠️ No Test ID Column Found", className="alert-heading"),
                        html.P("The CSV file doesn't contain a 'test_id' column. Please ensure your data has this column for test selection."),
                        html.Hr(),
                        html.P("Available columns:", className="mb-1"),
                        html.Ul([html.Li(col) for col in df.columns.tolist()[:10]], className="mb-0")
                    ], color="warning")
            else:
                return dbc.Alert([
                    html.H5("⚠️ No Field Column Found", className="alert-heading"),
                    html.P("The CSV file doesn't contain a 'field' column. This is required for proper data transposition."),
                    html.Hr(),
                    html.P("Available columns:", className="mb-1"),
                    html.Ul([html.Li(col) for col in df.columns.tolist()[:10]], className="mb-0")
                ], color="warning")
        else:
            return dbc.Alert([
                html.H5("📁 No Data Loaded", className="alert-heading"),
                html.P("Please load a batch file first to see available tests for analysis."),
                html.Hr(),
                html.P("Go to the Input tab and load your INI configuration file.")
            ], color="info")

    @app.callback(
        dash.dependencies.Output('analysis-status', 'children'),
        [dash.dependencies.Input('run-analysis-btn', 'n_clicks')],
        [dash.dependencies.State('test-selector-dropdown', 'value')],
        prevent_initial_call=True
    )
    def run_analysis(n_clicks, selected_tests):
        """Handle the run analysis button click"""
        if n_clicks:
            data_storage = get_data_storage()
            
            if 'csv_batch_data' not in data_storage or data_storage['csv_batch_data'] is None:
                return dbc.Alert("❌ No CSV data loaded. Please load a batch file first.", color="danger")
            
            if not selected_tests:
                return dbc.Alert("⚠️ Please select at least one test to analyze.", color="warning")
            
            # Create analysis status card
            return dbc.Card([
                dbc.CardHeader([
                    html.H5("🚀 Analysis Started", className="mb-0"),
                    html.Small("Processing selected tests...", className="text-muted")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Selected Tests:", className="fw-bold"),
                            html.Ul([html.Li(test) for test in selected_tests], className="mb-0")
                        ], width=6),
                        dbc.Col([
                            html.H6("Progress:", className="fw-bold"),
                            dbc.Progress(
                                value=0,
                                striped=True,
                                animated=True,
                                color="primary",
                                className="mb-2"
                            ),
                            html.Small(f"Running analysis on {len(selected_tests)} test(s))", className="text-muted")
                        ], width=6)
                    ])
                ])
            ], color="success", outline=True)
        
        return ""

    @app.callback(
        dash.dependencies.Output('test-selector-dropdown', 'options', allow_duplicate=True),
        [dash.dependencies.Input('batch-table-info', 'children')],
        prevent_initial_call=True
    )
    def update_test_options(batch_table_children):
        """Update test options when CSV data is loaded"""
        data_storage = get_data_storage()
        
        if 'csv_batch_data' in data_storage and data_storage['csv_batch_data'] is not None:
            df = data_storage['csv_batch_data']
            
            if 'field' in df.columns:
                df_t = df.set_index("field").transpose()
                
                if 'test_id' in df_t.columns:
                    unique_tests = df_t['test_id'].unique().tolist()
                    return [{"label": str(test), "value": str(test)} for test in unique_tests]
        
        return []

    @app.callback(
        [dash.dependencies.Output('test-selector-dropdown', 'value', allow_duplicate=True)],
        [dash.dependencies.Input('batch-table-info', 'children')],
        prevent_initial_call=True
    )
    def reset_test_selection(batch_table_children):
        """Reset test selection when new data is loaded"""
        return [[]]
