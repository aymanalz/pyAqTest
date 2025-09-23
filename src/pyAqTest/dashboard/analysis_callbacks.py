"""
Analysis Tab Callbacks
======================
Callbacks specifically for the Analysis tab functionality.
"""
import os
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from .data_storage import get_data_storage, add_data


def register_analysis_callbacks(app):
    """Register analysis-specific callbacks"""
    
    @app.callback(
        dash.dependencies.Output('test-selection-card', 'children'),
        [dash.dependencies.Input('batch-table-info', 'children')],
        prevent_initial_call=True
    )
    def create_test_selection_card(batch_table_children):
        """Create analysis run controls with two modes (batch default)."""
        data_storage = get_data_storage()

        test_options = []
        if 'csv_batch_data' in data_storage and data_storage['csv_batch_data'] is not None:
            df = data_storage['csv_batch_data']
            if 'field' in df.columns:
                df_t = df.set_index("field").transpose()
                if 'test_id' in df_t.columns:
                    unique_tests = df_t['test_id'].unique().tolist()
                    test_options = [{"label": str(t), "value": str(t)} for t in unique_tests]

        has_server_ini = bool(get_data_storage().get('server_run_path'))
        return dbc.Card([
            dbc.CardBody([
                dbc.Tabs([
                    dbc.Tab(
                        label="Run from Batch File (XXX)",
                        tab_id="mode-batch",
                        children=[
                            html.P(
                                "Run analysis using the configured batch file.",
                                className="mb-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-play me-2"), "Run Batch (XXX)"],
                                id="run-batch-btn",
                                color="primary",
                                size="lg",
                                className="mt-1",
                                disabled=not has_server_ini
                            )
                        ]
                    ),
                    dbc.Tab(
                        label="Run Selected Tests",
                        tab_id="mode-selected",
                        disabled=True,
                        children=[
                            dbc.Label("Select Tests to Run:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="test-selector-dropdown",
                                options=test_options,
                                placeholder="Choose tests to analyze...",
                                multi=True,
                                disabled=True,
                                style={"fontSize": "14px"}
                            ),
                            html.Small(
                                "Run Selected Tests is inactive for now",
                                className="text-muted mt-1"
                            )
                        ]
                    ),
                ], id="analysis-run-tabs", active_tab="mode-batch")
            ])
        ], className="mb-4")

    # Helper (no decorator): run the batch analysis
    def _run_batch_process():
        data_storage = get_data_storage()
        import pyAqTest
        ini_filename = data_storage.get('server_run_path')
        if not ini_filename:
            return False
        batch = pyAqTest.Batch_Processing(config_obj=ini_filename)
        batch.run_batch()
        add_data('batch_obj', batch)
        return True

    @app.callback(
        dash.dependencies.Output('analysis-status', 'children'),
        [dash.dependencies.Input('run-batch-btn', 'n_clicks')],
        [dash.dependencies.State('test-selector-dropdown', 'value')],
        prevent_initial_call=True
    )
    def run_analysis(n_clicks_batch, selected_tests):
        """Run batch only when Run Batch is clicked."""
        if n_clicks_batch:
            ok = _run_batch_process()
            header = "🚀 Batch Analysis Started" if ok else "❌ Batch Start Failed"
            subtitle = "Processing batch file: XXX" if ok else "Missing INI file path"
            return dbc.Card([
                dbc.CardHeader([
                    html.H5(header, className="mb-0"),
                    html.Small(subtitle, className="text-muted")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Mode:", className="fw-bold"),
                            html.Div("Run from Batch File (XXX)")
                        ], width=6),
                        dbc.Col([
                            html.H6("Progress:", className="fw-bold"),
                            dbc.Progress(value=0, striped=True, animated=True, color="primary", className="mb-2"),
                            html.Small("Running batch analysis...", className="text-muted")
                        ], width=6)
                    ])
                ])
            ], color="success" if ok else "danger", outline=True)

        return ""

    # Removed progress polling logic per user request

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
