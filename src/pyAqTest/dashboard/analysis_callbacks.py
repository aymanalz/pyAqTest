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
        if has_server_ini:
            batch_file_name = data_storage['server_run_path']
        else:
            batch_file_name = "N/A"
        return dbc.Card([
            dbc.CardBody([
                dbc.Tabs([
                    dbc.Tab(
                        label="Run from Batch File",
                        tab_id="mode-batch",
                        children=[
                            html.P(
                                f"Run analysis using the configured batch file {batch_file_name}.",
                                className="mb-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-play me-2"), "Run Batch "],
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
        # Monkey-patch tqdm used inside run_batch to report progress
        try:
            import pyAqTest.batch_processing as bp
            from tqdm import tqdm as real_tqdm

            class TqdmProxy:
                def __init__(self, *args, **kwargs):
                    self._t = real_tqdm(*args, **kwargs)
                    self.total = kwargs.get('total')
                    self.n = 0
                    add_data('batch_progress', {'current': self.n, 'total': self.total})

                def update(self, n=1):
                    self.n += n
                    add_data('batch_progress', {'current': self.n, 'total': self.total})
                    return self._t.update(n)

                def set_postfix_str(self, s):
                    return self._t.set_postfix_str(s)

                def __enter__(self):
                    self._t.__enter__()
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return self._t.__exit__(exc_type, exc, tb)

            bp.tqdm = TqdmProxy
        except Exception:
            pass

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
            subtitle = "Processing batch file: " if ok else "Missing INI file path"
            # reveal the global progress container when starting
            return dbc.Card([
                dbc.CardHeader([
                    html.H5(header, className="mb-0"),
                    html.Small(subtitle, className="text-muted")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Mode:", className="fw-bold"),
                            html.Div("Run from Batch File ")
                        ], width=6),
                        dbc.Col([
                            html.H6("Progress:", className="fw-bold"),
                            html.Div(id='batch-progress-container')
                        ], width=6)
                    ])
                ])
            ], color="success" if ok else "danger", outline=True)

        return ""

    @app.callback(
        [dash.dependencies.Output('batch-progress-interval', 'disabled', allow_duplicate=True),
         dash.dependencies.Output('batch-progress-bar', 'value', allow_duplicate=True),
         dash.dependencies.Output('batch-progress-text', 'children', allow_duplicate=True),
         dash.dependencies.Output('batch-progress-container', 'style', allow_duplicate=True)],
        [dash.dependencies.Input('run-batch-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def _start_progress(_n):
        # Enable interval and reset bar when run starts
        return False, 0, "Starting...", {"display": "block"}

    @app.callback(
        [dash.dependencies.Output('batch-progress-bar', 'value', allow_duplicate=True),
         dash.dependencies.Output('batch-progress-text', 'children', allow_duplicate=True),
         dash.dependencies.Output('batch-progress-interval', 'disabled', allow_duplicate=True),
         dash.dependencies.Output('batch-progress-container', 'style', allow_duplicate=True)],
        [dash.dependencies.Input('batch-progress-interval', 'n_intervals')],
        prevent_initial_call=True
    )
    def _poll_progress(_n):
        prog = get_data_storage().get('batch_progress') or {}
        cur = prog.get('current') or 0
        tot = prog.get('total') or None
        if tot and tot > 0:
            pct = int(100 * cur / tot)
            done = cur >= tot
            return pct, f"{cur} / {tot}", done, ({"display": "none"} if done else {"display": "block"})
        return 0, "Starting...", False, {"display": "block"}

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
