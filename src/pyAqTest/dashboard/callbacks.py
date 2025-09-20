"""
Dashboard Callbacks
==================
Contains all callback functions for the Batch Slug Test Analysis dashboard.
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import base64
import pandas as pd
from .data_storage import get_data_storage, add_data
from .utils import read_ini_file

def create_ini_config_form(config_dict, filename, file_path=None):
    """Create a neat form with INI config file content"""
    form_elements = []
    
    # Get the actual file path from global data storage
    import os
    data_storage = get_data_storage()
    if 'file_path' in data_storage:
        folder_path = os.path.dirname(data_storage['file_path'])
    elif file_path:
        folder_path = os.path.dirname(file_path)
    else:
        folder_path = "Unknown"
    
    # Add file info header
    form_elements.append(
        dbc.Card([
            dbc.CardHeader([
                html.H5(f"📄 {filename}", className="mb-0"),
                html.Small("INI Configuration File", className="text-muted")
            ]),
            dbc.CardBody([
                # File path info
                html.P(f"📁 Path: {folder_path}", className="mb-2"),
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

def create_csv_table(df, filename):
    """Create an interactive table from CSV data"""
    if df is None or df.empty:
        return html.Div([
            html.H6("No data available", className="text-muted"),
            html.P("The CSV file appears to be empty or invalid")
        ])
    
    # Create table header with file info
    header = dbc.Card([
        dbc.CardHeader([
            html.H5(f"📊 {filename}", className="mb-0"),
            html.Small("Batch Data File", className="text-muted")
        ]),
        dbc.CardBody([
            html.P(f"📈 Rows: {len(df)}", className="mb-1"),
            html.P(f"📋 Columns: {len(df.columns)}", className="mb-0")
        ])
    ], className="mb-3")
    
    # Create interactive table using dash_table
    table = dcc.Graph(
        figure={
            'data': [{
                'type': 'table',
                'header': {
                    'values': df.columns.tolist(),
                    'fill': {'color': '#007bff'},
                    'font': {'color': 'white', 'size': 12}
                },
                'cells': {
                    'values': [df[col].tolist() for col in df.columns],
                    'fill': {'color': ['#f8f9fa', 'white']},
                    'font': {'size': 11},
                    'height': 30
                }
            }],
            'layout': {
                'title': f'Batch Data: {filename}',
                'height': min(600, 200 + len(df) * 30),
                'margin': {'l': 10, 'r': 10, 't': 50, 'b': 10}
            }
        },
        config={'displayModeBar': False}
    )
    
    # Add summary statistics
    summary_stats = []
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            summary_stats.append(
                dbc.Row([
                    dbc.Col([html.Strong(f"{col}:")], width=3),
                    dbc.Col([f"Min: {df[col].min():.2f}"], width=3),
                    dbc.Col([f"Max: {df[col].max():.2f}"], width=3),
                    dbc.Col([f"Mean: {df[col].mean():.2f}"], width=3)
                ], className="mb-1")
            )
    
    summary_card = dbc.Card([
        dbc.CardHeader([html.H6("📈 Summary Statistics", className="mb-0")]),
        dbc.CardBody(summary_stats) if summary_stats else html.P("No numeric columns found", className="text-muted")
    ], className="mb-3") if summary_stats else None
    
    # Add export buttons
    export_buttons = dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Button("📊 View Full Data", color="primary", className="me-2"),
                    dbc.Button("📤 Export CSV", color="success", className="me-2"),
                    dbc.Button("📋 Copy Data", color="info")
                ], width=12)
            ])
        ])
    ])
    
    components = [header, table]
    if summary_card:
        components.append(summary_card)
    components.append(export_buttons)
    
    return components

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
                        
                        # Direct file input - no Choose File button needed
                        dcc.Upload(
                            id="file-input",
                            children=html.Div([
                                html.A('📁 Choose .ini File', 
                                       style={'color': 'white', 'textDecoration': 'none', 'fontWeight': 'bold', 'fontSize': '16px'})
                            ], style={'padding': '12px 24px', 'backgroundColor': '#007bff', 'borderRadius': '6px', 'cursor': 'pointer', 'display': 'inline-block', 'border': 'none', 'textAlign': 'center'}),
                            style={"display": "block", "margin": "10px 0"},
                            accept=".ini",
                            multiple=False
                        ),
                        
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
                                    html.Div([
                                        html.H6("Batch Data Table", className="mb-3"),
                                        html.P("CSV data will be automatically loaded from the INI file configuration", className="text-muted mb-3"),
                                        html.Div(id='batch-table-info', children="No batch data loaded")
                                    ])
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
            
            # Use global data storage
            data_storage = get_data_storage()
            add_data('file_path', full_path)
            add_data('file_name', filename)
           
            try:
                decoded = base64.b64decode(contents.split(',')[1]).decode('utf-8')
                config = configparser.ConfigParser()
                config.read_string(decoded)
                config_dict = {}
                for section in config.sections():
                    config_dict[section] = dict(config[section])
                add_data('parsed_config', config_dict)
            except Exception as e:
                add_data('parsed_config', {"error": f"Failed to parse INI file: {str(e)}"})
            
            # Auto-load CSV file if batch_data_file is specified in INI
            parsed_config = data_storage.get('parsed_config', {})
            if parsed_config and "error" not in parsed_config:
                # Check for batch_data_file in Input Info section
                if "Input Info" in parsed_config:
                    input_info = parsed_config["Input Info"]
                    if "batch_data_file" in input_info:
                        csv_path = input_info["batch_data_file"]
                        # Try to load the CSV file
                        try:
                            import pandas as pd
                            # Check if path is relative or absolute
                            if not os.path.isabs(csv_path):
                                # Make relative to INI file directory
                                ini_dir = os.path.dirname(full_path)
                                csv_path = os.path.join(ini_dir, csv_path)
                            
                            # Load CSV file
                            if os.path.exists(csv_path):
                                df = pd.read_csv(csv_path)
                                add_data('csv_batch_data', df)
                                add_data('csv_filename', os.path.basename(csv_path))
                            else:
                                add_data('csv_batch_data', None)
                                add_data('csv_filename', None)
                        except Exception as e:
                            add_data('csv_batch_data', None)
                            add_data('csv_filename', None)
                            print(f"Error loading CSV file: {e}")
            
            # Create form with INI config content
            if parsed_config and "error" not in parsed_config:
                form_content = create_ini_config_form(parsed_config, filename, full_path)
            else:
                form_content = f"Error loading INI file: {parsed_config.get('error', 'Unknown error')}"
            
            return form_content
        return "No file selected"
    
    # Callback to auto-update Batch Table when INI file is loaded
    @app.callback(
        dash.dependencies.Output('batch-table-info', 'children'),
        [dash.dependencies.Input('file-input', 'contents')],
        [dash.dependencies.State('file-input', 'filename')],
        prevent_initial_call=True
    )
    def auto_update_batch_table(contents, filename):
        """Auto-update batch table when INI file is loaded"""
        data_storage = get_data_storage()
        if contents is not None and data_storage.get('csv_batch_data') is not None:
            return create_csv_table(data_storage['csv_batch_data'], data_storage.get('csv_filename'))
        elif contents is not None and data_storage.get('csv_batch_data') is None:
            return html.Div([
                html.H6("No CSV data found", className="text-warning"),
                html.P("The INI file does not contain a valid 'batch_data_file' path in the 'Input Info' section"),
                html.P("Or the CSV file could not be loaded from the specified path")
            ])
        return "No batch data loaded"
    
    # Callback for load batch button
    @app.callback(
        dash.dependencies.Output('load-file-info', 'children', allow_duplicate=True),
        [dash.dependencies.Input('load-action-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def load_batch_file(n_clicks):
        """Handle load batch file button"""
        if n_clicks:
            # Example: Read INI file using utils function
            # You can call this with any INI filename
            # success = read_ini_file("config.ini")
            # if success:
            #     return "INI file loaded successfully!"
            # else:
            #     return "Failed to load INI file"
            
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
