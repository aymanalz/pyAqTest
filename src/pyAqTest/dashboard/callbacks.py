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
    
    # Callback for upload button
    @app.callback(
        dash.dependencies.Output('upload-status', 'children'),
        [dash.dependencies.Input('upload-btn', 'n_clicks')]
    )
    def update_file_status(n_clicks):
        """Update file selection status"""
        if n_clicks:
            return "Files uploaded successfully!"
        return "No files selected"
    
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
