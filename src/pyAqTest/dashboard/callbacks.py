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

def create_ini_config_form(config_dict, filename):
    """Create a neat form with INI config file content"""
    form_elements = []
    
    # Add file info header
    form_elements.append(
        dbc.Card([
            dbc.CardHeader([
                html.H5(f"📄 {filename}", className="mb-0"),
                html.Small("INI Configuration File", className="text-muted")
            ]),
            dbc.CardBody([
                # File path info
                html.P(f"📁 Path: {config_dict.get('file_path', 'Unknown')}", className="mb-2"),
                html.P(f"📊 Sections: {len(config_dict)}", className="mb-0")
            ])
        ], className="mb-3")
    )
    
    # Create form for each section
    for section_name, section_data in config_dict.items():
        if section_name == "file_path":
            continue
            
        # Section header
        form_elements.append(
            dbc.Card([
                dbc.CardHeader([
                    html.H6(f"🔧 {section_name.replace('_', ' ').title()}", className="mb-0")
                ]),
                dbc.CardBody([
                    # Create form fields for each key-value pair
                    dbc.Row([
                        dbc.Col([
                            dbc.Label(key.replace('_', ' ').title(), className="fw-bold"),
                            dbc.Input(
                                value=str(value),
                                id=f"config-{section_name}-{key}",
                                className="mb-2"
                            )
                        ], width=6) for key, value in section_data.items()
                    ])
                ])
            ], className="mb-3")
        )
    
    # Add action buttons
    form_elements.append(
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Button("💾 Save Changes", color="primary", className="me-2"),
                        dbc.Button("🔄 Reset", color="secondary", className="me-2"),
                        dbc.Button("📤 Export", color="info")
                    ], width=12)
                ])
            ])
        ])
    )
    
    return form_elements

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
                        dbc.Button("Choose File", color="primary", id="choose-file-btn"),
                        html.Hr(),
                        html.H6("File Details", className="mb-3"),
                        dbc.Tabs([
                            dbc.Tab(
                                label="Settings File Details",
                                tab_id="settings-tab",
                                children=[
                                    html.Div(id='load-file-info', children="No file selected")
                                ]
                            ),
                            dbc.Tab(
                                label="Batch Table",
                                tab_id="batch-table-tab",
                                children=[
                                    html.Div(id='batch-table-info', children="No batch data loaded")
                                ]
                            )
                        ], id="file-details-tabs", active_tab="settings-tab"),
                        html.Hr(),
                        html.H6("Recent Files:", className="mt-3"),
                        html.Div(id='recent-files', children="No recent files")
                    ], width=12)
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
    
    # Callback for Choose File button to trigger file input
    @app.callback(
        dash.dependencies.Output('file-input', 'style'),
        [dash.dependencies.Input('choose-file-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def trigger_file_input(n_clicks):
        """Trigger file input when Choose File button is clicked"""
        if n_clicks:
            # Temporarily show file input overlay when Choose File is clicked
            return {"display": "block", "position": "fixed", "top": "0", "left": "0", "width": "100vw", "height": "100vh", "z-index": "9999", "opacity": "0", "cursor": "pointer"}
        return {"display": "none"}
    
    # Callback to hide file input after file selection
    @app.callback(
        dash.dependencies.Output('file-input', 'style', allow_duplicate=True),
        [dash.dependencies.Input('file-input', 'contents')],
        prevent_initial_call=True
    )
    def hide_file_input_after_selection(contents):
        """Hide file input after file is selected"""
        if contents is not None:
            return {"display": "none"}
        return dash.no_update

    # Callback for file input to handle .ini file selection
    @app.callback(
        dash.dependencies.Output('load-file-info', 'children'),
        [dash.dependencies.Input('file-input', 'contents')],
        [dash.dependencies.State('file-input', 'filename')],
        prevent_initial_call=True
    )
    def handle_file_upload(contents, filename):
        """Handle .ini file upload"""
        if contents is not None:
            # File was selected - capture full file path
            import os
            import base64
            import configparser
            
            full_path = os.path.abspath(filename) if filename else "Unknown path"
            
            # Store in data_storage class (you can expand this class as needed)
            class DataStorage:
                def __init__(self):
                    self.file_path = None
                    self.file_name = None
                    self.file_contents = None
                    self.parsed_config = None
                
                def store_file(self, path, name, contents):
                    self.file_path = path
                    self.file_name = name
                    self.file_contents = contents
                    # Parse the INI file
                    self.parsed_config = self.parse_ini_config(contents)
                
                def parse_ini_config(self, contents):
                    """Parse INI config file"""
                    try:
                        # Decode base64 content
                        decoded = base64.b64decode(contents.split(',')[1]).decode('utf-8')
                        
                        # Parse as INI file
                        config = configparser.ConfigParser()
                        config.read_string(decoded)
                        
                        # Convert to dictionary for easy access
                        config_dict = {}
                        for section in config.sections():
                            config_dict[section] = dict(config[section])
                        
                        return config_dict
                    except Exception as e:
                        return {"error": f"Failed to parse INI file: {str(e)}"}
                
                def get_file_info(self):
                    return {
                        'path': self.file_path,
                        'name': self.file_name,
                        'has_contents': self.file_contents is not None,
                        'parsed_config': self.parsed_config
                    }
            
            # Create or update data storage
            if not hasattr(app, 'data_storage'):
                app.data_storage = DataStorage()
            
            app.data_storage.store_file(full_path, filename, contents)
            
            # Create form with INI config content
            if app.data_storage.parsed_config and "error" not in app.data_storage.parsed_config:
                form_content = create_ini_config_form(app.data_storage.parsed_config, filename)
            else:
                form_content = f"Error loading INI file: {app.data_storage.parsed_config.get('error', 'Unknown error')}"
            
            return form_content
        return "No file selected"
    
    # Callback for load batch button
    @app.callback(
        dash.dependencies.Output('load-file-info', 'children', allow_duplicate=True),
        [dash.dependencies.Input('load-action-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def load_batch_file(n_clicks):
        """Handle load batch file button"""
        if n_clicks:
            return "Load action triggered - use Choose File button to select .ini file"
        return dash.no_update
    
    # Callback for new batch button
    @app.callback(
        dash.dependencies.Output('load-file-info', 'children', allow_duplicate=True),
        [dash.dependencies.Input('new-action-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def new_batch_file(n_clicks):
        """Handle new batch file button"""
        if n_clicks:
            return "New batch action triggered - create new batch configuration"
        return dash.no_update
    
    # Callback for save button
    @app.callback(
        dash.dependencies.Output('load-file-info', 'children', allow_duplicate=True),
        [dash.dependencies.Input('save-action-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def save_batch_file(n_clicks):
        """Handle save button"""
        if n_clicks:
            return "Save action triggered - save current batch configuration"
        return dash.no_update
    
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
