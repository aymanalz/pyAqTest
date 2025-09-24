"""
Results Tab Callbacks
=====================
Callbacks specifically for the Results tab functionality.
"""
import os
import pandas as pd
import dash
from dash import html, dcc
import base64
import dash_bootstrap_components as dbc
import pandas as pd
from .data_storage import get_data_storage
from .components import create_results_table
from .data_storage import add_data


def register_results_callbacks(app):
    """Register results-specific callbacks"""

    @app.callback(
        dash.dependencies.Output('results-test-selector', 'options'),
        [dash.dependencies.Input('batch-table-info', 'children')],
        prevent_initial_call=True
    )
    def populate_results_selector(_batch_children):
        """Populate the Results tab dropdown with test_id options."""
        data_storage = get_data_storage()
        df = data_storage.get('csv_batch_data')
        if df is None:
            return []
        if 'field' not in df.columns:
            return []
        df_t = df.set_index('field').transpose()
        if 'test_id' not in df_t.columns:
            return []
        unique_tests = df_t['test_id'].unique().tolist()
        return [{"label": str(t), "value": str(t)} for t in unique_tests]

    # Do not auto-select a default test; require explicit user selection

    @app.callback(
        dash.dependencies.Output('results-selection-message', 'children'),
        [dash.dependencies.Input('results-test-selector', 'value'),
         dash.dependencies.Input('batch-progress-interval', 'n_intervals')],
        prevent_initial_call=True
    )
    def update_results_selection_message(selected_test_id, _n):
        """Display a message only when a user selects a test id."""
        if not selected_test_id:
            return ""

        data_storage = get_data_storage()
        # Resolve output folder (handle relative path based on uploaded INI location)
        parsed = data_storage.get('parsed_config') or {}
        out_rel = parsed.get('Output Info', {}).get('output_folder')
        ini_path = data_storage.get('file_path') or data_storage.get('server_run_path')
        if out_rel:
            if os.path.isabs(out_rel):
                output_folder = out_rel
            else:
                base_dir = os.path.dirname(ini_path) if ini_path else os.getcwd()
                output_folder = os.path.join(base_dir, out_rel)
        else:
            output_folder = os.getcwd()

        # Optionally cache results dataframe (not required for image display)
        estimatedKFn = os.path.join(output_folder, 'estimated_conductivity.csv')
        if "results_df" not in data_storage and os.path.exists(estimatedKFn):
            try:
                result_df = pd.read_csv(estimatedKFn)
                add_data('results_df', result_df)
            except Exception:
                pass

        # Build expected image paths
        fitplot_fn = os.path.join(output_folder, 'fit_plots', f"{selected_test_id}.png")
        recovery_fn = None
        try:
            batch_obj = data_storage.get('batch_obj')
            if batch_obj is not None and hasattr(batch_obj, 'df_batch'):
                df_batch = batch_obj.df_batch
                test_file = df_batch.loc[df_batch["test_id"] == selected_test_id, "test_data_file"].values[0]
                test_file = os.path.basename(test_file)
                test_file = os.path.splitext(test_file)[0] + ".png"
                recovery_fn = os.path.join(output_folder, 'recovery_splits', test_file)
        except Exception:
            recovery_fn = None

        # Build two images: recovery and fit plot
        elems = []
        try:
            if recovery_fn and os.path.exists(recovery_fn):
                with open(recovery_fn, "rb") as f:
                    rec_b64 = base64.b64encode(f.read()).decode("ascii")
                elems.append(
                    dbc.Col([
                        html.H6("Recovery Data Splits", className="mb-2"),
                        html.Img(
                            src=f"data:image/png;base64,{rec_b64}",
                            style={"maxWidth": "100%", "height": "auto"}
                        ),
                    ], width=6)
                )
            if os.path.exists(fitplot_fn):
                with open(fitplot_fn, "rb") as f:
                    fit_b64 = base64.b64encode(f.read()).decode("ascii")
                elems.append(
                    dbc.Col([
                        html.H6("Fitted Model Plot", className="mb-2"),
                        html.Img(
                            src=f"data:image/png;base64,{fit_b64}",
                            style={"maxWidth": "100%", "height": "auto"}
                        ),
                    ], width=6)
                )
        except Exception:
            pass

        if elems:
            return dbc.Row(elems)

        # Not ready yet; show lightweight progress note
        return dbc.Alert(
            f"Preparing plots for {selected_test_id}...",
            color="info",
            dismissable=False,
        )

    @app.callback(
        dash.dependencies.Output("summary-stats", "children"),
        [dash.dependencies.Input("run-batch-btn", "n_clicks"),
         dash.dependencies.Input('results-test-selector', 'value')],
        prevent_initial_call=True,
    )
    def update_summary_stats(n_clicks_batch, selected_result_test):
        """Update the summary stats when analysis runs."""
        if not n_clicks_batch:
            return ""

        data_storage = get_data_storage()

        # If a processed results frame exists, summarize it; otherwise show
        # a helpful placeholder.
        df = data_storage.get("csv_batch_data")
        if df is None:
            return dbc.Alert(
                "No data available to summarize.", color="secondary"
            )

        num_rows = len(df)
        num_cols = len(df.columns)
        chosen = selected_result_test if selected_result_test else "None"

        return html.Ul(
            [
                html.Li(f"Rows: {num_rows}"),
                html.Li(f"Columns: {num_cols}"),
                html.Li(f"Results selection: {chosen}"),
            ]
        )
    
 

    # @app.callback(
    #     dash.dependencies.Output("results-table", "children"),
    #     [dash.dependencies.Input("run-batch-btn", "n_clicks"),
    #      dash.dependencies.Input('results-test-selector', 'value')],
    #     prevent_initial_call=True,
    # )
    # def update_results_table(n_clicks_batch, selected_result_test):
    #     """Update the results table when analysis runs."""
    #     data_storag = get_data_storage()
    #     output_folder = data_storag['parsed_config']['Output Info']['output_folder']
    #     estimatedKFn = os.path.join(output_folder, 'estimated_conductivity.csv')
    #     result_df = pd.read_csv(estimatedKFn)
    #     if not n_clicks_batch:
    #         return ""

    #     # Placeholder table for now. Replace with actual results dataframe
    #     # when available in the shared data store.
    #     return create_results_table()


