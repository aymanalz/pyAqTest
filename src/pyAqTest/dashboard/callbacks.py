"""
Dashboard Callbacks
==================
Contains all callback functions for the Batch Slug Test Analysis dashboard.
"""

import dash
from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import base64

def register_callbacks(app):
    """Register all callbacks with the app"""
    
    # Callback for load action button
    @app.callback(
        dash.dependencies.Output('action-tab-content', 'children'),
        [dash.dependencies.Input('load-action-btn', 'n_clicks')]
    )
    def update_load_content(n_clicks):
        """Update content for load action"""
        if n_clicks:
            return [
                dbc.Row([
                    dbc.Col([
                        html.H6("Load Batch File", className="mb-3"),
                        html.P("Select and load an existing batch file for analysis", className="text-muted mb-3"),
                        dbc.Button("Choose File", color="primary", className="me-2"),
                        dbc.Button("Browse", color="secondary")
                    ], width=6),
                    
                    dbc.Col([
                        html.H6("File Details", className="mb-3"),
                        html.Div(id='load-file-info', children="No file selected"),
                        html.Hr(),
                        html.H6("Recent Files:", className="mt-3"),
                        html.Div(id='recent-files', children="No recent files")
                    ], width=6)
                ])
            ]
        return "Select an action"
    
    # Callback for new action button
    @app.callback(
        dash.dependencies.Output('action-tab-content', 'children', allow_duplicate=True),
        [dash.dependencies.Input('new-action-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_new_content(n_clicks):
        """Update content for new action"""
        if n_clicks:
            return [
                dbc.Row([
                    dbc.Col([
                        html.H6("Create New Batch", className="mb-3"),
                        html.P("Start a new batch analysis from scratch", className="text-muted mb-3"),
                        dbc.Button("New Batch", color="success", className="me-2"),
                        dbc.Button("Template", color="info")
                    ], width=6),
                    
                    dbc.Col([
                        html.H6("Batch Settings", className="mb-3"),
                        html.Div(id='new-batch-info', children="Configure your new batch"),
                        html.Hr(),
                        html.H6("Templates:", className="mt-3"),
                        html.Div(id='templates', children="Available templates")
                    ], width=6)
                ])
            ]
        return dash.no_update
    
    # Callback for save action button
    @app.callback(
        dash.dependencies.Output('action-tab-content', 'children', allow_duplicate=True),
        [dash.dependencies.Input('save-action-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_save_content(n_clicks):
        """Update content for save action"""
        if n_clicks:
            return [
                dbc.Row([
                    dbc.Col([
                        html.H6("Save Batch", className="mb-3"),
                        html.P("Save your current batch analysis", className="text-muted mb-3"),
                        dbc.Button("Save As", color="info", className="me-2"),
                        dbc.Button("Export", color="warning")
                    ], width=6),
                    
                    dbc.Col([
                        html.H6("Export Options", className="mb-3"),
                        html.Div(id='save-options', children="Choose export format"),
                        html.Hr(),
                        html.H6("Recent Saves:", className="mt-3"),
                        html.Div(id='recent-saves', children="No recent saves")
                    ], width=6)
                ])
            ]
        return dash.no_update
    
    # Callback for load batch button
    @app.callback(
        [dash.dependencies.Output('upload-status', 'children'),
         dash.dependencies.Output('action-log', 'children')],
        [dash.dependencies.Input('load-batch-btn', 'n_clicks')]
    )
    def load_batch_file(n_clicks):
        """Handle load batch file button"""
        if n_clicks:
            return "Batch file loaded successfully!", f"• Loaded batch file (click #{n_clicks})"
        return "No batch file loaded", "No actions yet"
    
    # Callback for new batch button
    @app.callback(
        [dash.dependencies.Output('upload-status', 'children', allow_duplicate=True),
         dash.dependencies.Output('action-log', 'children', allow_duplicate=True)],
        [dash.dependencies.Input('new-batch-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def new_batch_file(n_clicks):
        """Handle new batch file button"""
        if n_clicks:
            return "New batch file created!", f"• Created new batch file (click #{n_clicks})"
        return dash.no_update, dash.no_update
    
    # Callback for save button
    @app.callback(
        [dash.dependencies.Output('upload-status', 'children', allow_duplicate=True),
         dash.dependencies.Output('action-log', 'children', allow_duplicate=True)],
        [dash.dependencies.Input('save-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def save_batch_file(n_clicks):
        """Handle save button"""
        if n_clicks:
            return "Batch file saved successfully!", f"• Saved batch file (click #{n_clicks})"
        return dash.no_update, dash.no_update
    
    # Callback for upload button
    @app.callback(
        [dash.dependencies.Output('output-data-upload', 'children'),
         dash.dependencies.Output('analysis-plot', 'figure')],
        [dash.dependencies.Input('upload-btn', 'n_clicks')]
    )
    def handle_upload(n_clicks):
        """Handle file upload and display results"""
        if n_clicks is None:
            return "No files uploaded", go.Figure()
        
        try:
            # Create a simple analysis plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[1, 2, 3, 4, 5], 
                y=[10, 11, 12, 13, 14], 
                mode='lines+markers',
                name='Slug Test Data',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title="Slug Test Analysis Results",
                xaxis_title="Time (minutes)",
                yaxis_title="Head (ft)",
                height=500,
                width=None,
                autosize=True,
                margin=dict(l=50, r=50, t=50, b=50),
                template="plotly_white"
            )
            
            return "Successfully uploaded files!", fig
            
        except Exception as e:
            return f"Error uploading file: {str(e)}", go.Figure()
    
    # Callback for clear button
    @app.callback(
        dash.dependencies.Output('upload-status', 'children', allow_duplicate=True),
        [dash.dependencies.Input('clear-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def clear_files(n_clicks):
        """Clear file selection"""
        if n_clicks:
            return "Files cleared"
        return dash.no_update
    
    # Callback for analysis button
    @app.callback(
        dash.dependencies.Output('analysis-plot', 'figure', allow_duplicate=True),
        [dash.dependencies.Input('run-analysis', 'n_clicks')],
        [dash.dependencies.State('well-name', 'value'),
         dash.dependencies.State('test-date', 'value')],
        prevent_initial_call=True
    )
    def run_analysis(n_clicks, well_name, test_date):
        """Run analysis when button is clicked"""
        if n_clicks is None:
            return go.Figure()
        
        # Create analysis plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
            y=[10, 8, 6, 4, 3, 2.5, 2, 1.8, 1.6, 1.5], 
            mode='lines+markers',
            name=f'Well: {well_name or "Unknown"}',
            line=dict(color='red', width=3)
        ))
        
        fig.update_layout(
            title=f"Slug Test Analysis - {well_name or 'Unknown Well'}",
            xaxis_title="Time (minutes)",
            yaxis_title="Head (ft)",
            height=500,
            width=None,
            autosize=True,
            margin=dict(l=50, r=50, t=50, b=50),
            template="plotly_white"
        )
        
        return fig
    
    # Callback for summary statistics
    @app.callback(
        dash.dependencies.Output('summary-stats', 'children'),
        [dash.dependencies.Input('analysis-plot', 'figure')]
    )
    def update_summary_stats(figure):
        """Update summary statistics based on analysis"""
        if not figure or not figure.get('data'):
            return "No data available"
        
        # Mock summary statistics
        stats = [
            html.P("📊 Analysis Summary:", className="fw-bold"),
            html.P("• Hydraulic Conductivity: 2.5 × 10⁻⁴ ft/s"),
            html.P("• Transmissivity: 1.2 × 10⁻³ ft²/s"),
            html.P("• Storage Coefficient: 0.001"),
            html.P("• Recovery Time: 45 minutes"),
            html.P("• R² Value: 0.98")
        ]
        
        return stats
    
    # Callback for results table
    @app.callback(
        dash.dependencies.Output('results-table', 'children'),
        [dash.dependencies.Input('analysis-plot', 'figure')]
    )
    def update_results_table(figure):
        """Update results table based on analysis"""
        if not figure or not figure.get('data'):
            return "No results available"
        
        # Mock results table
        table = dbc.Table([
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
        
        return table
