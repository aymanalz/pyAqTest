"""
Results Tab Callbacks
=====================
Callbacks specifically for the Results tab functionality.
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from .data_storage import get_data_storage
from .components import create_results_table


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

    @app.callback(
        dash.dependencies.Output('results-test-selector', 'value'),
        [dash.dependencies.Input('results-test-selector', 'options')],
        prevent_initial_call=True
    )
    def default_results_selection(options):
        """Set default selection to first option if available."""
        if options:
            return options[0]['value']
        return dash.no_update

    @app.callback(
        dash.dependencies.Output("summary-stats", "children"),
        [dash.dependencies.Input("run-analysis-btn", "n_clicks"),
         dash.dependencies.Input('results-test-selector', 'value')],
        [dash.dependencies.State("test-selector-dropdown", "value")],
        prevent_initial_call=True,
    )
    def update_summary_stats(n_clicks, selected_result_test, selected_tests):
        """Update the summary stats when analysis runs."""
        if not n_clicks:
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
        tests = selected_tests or []
        chosen = selected_result_test if selected_result_test else "None"

        return html.Ul(
            [
                html.Li(f"Rows: {num_rows}"),
                html.Li(f"Columns: {num_cols}"),
                html.Li(f"Selected tests: {len(tests)}"),
                html.Li(f"Results selection: {chosen}"),
            ]
        )

    @app.callback(
        dash.dependencies.Output("results-table", "children"),
        [dash.dependencies.Input("run-analysis-btn", "n_clicks"),
         dash.dependencies.Input('results-test-selector', 'value')],
        [dash.dependencies.State("test-selector-dropdown", "value")],
        prevent_initial_call=True,
    )
    def update_results_table(n_clicks, selected_result_test, selected_tests):
        """Update the results table when analysis runs."""
        if not n_clicks:
            return ""

        # Placeholder table for now. Replace with actual results dataframe
        # when available in the shared data store.
        return create_results_table()


