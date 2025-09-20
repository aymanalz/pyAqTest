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
import os
import configparser
from .data_storage import get_data_storage, add_data

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
    """Create an interactive table from CSV data with column selection and search"""
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
    
    # Column selection and search controls
    controls_card = dbc.Card([
        dbc.CardHeader([html.H6("🔍 Table Controls", className="mb-0")]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Search Columns:", className="fw-bold"),
                    dbc.Input(
                        id="column-search",
                        placeholder="Type to search columns...",
                        value="",
                        debounce=True
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Show Columns:", className="fw-bold"),
                    dcc.Dropdown(
                        id="column-selector",
                        options=[{"label": col, "value": col} for col in df.columns],
                        value=df.columns[:10].tolist() if len(df.columns) > 10 else df.columns.tolist(),
                        multi=True,
                        style={"fontSize": "14px"}
                    )
                ], width=6)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("📋 Select All", id="select-all-cols", color="outline-primary", size="sm", className="me-2"),
                    dbc.Button("❌ Clear All", id="clear-all-cols", color="outline-secondary", size="sm", className="me-2"),
                    dbc.Button("🔄 Reset View", id="reset-view", color="outline-info", size="sm")
                ], width=12)
            ])
        ])
    ], className="mb-3")
    
    # Create interactive table using dash_table with initial subset
    initial_cols = df.columns[:10].tolist() if len(df.columns) > 10 else df.columns.tolist()
    table = dcc.Graph(
        id="csv-data-table",
        figure={
            'data': [{
                'type': 'table',
                'header': {
                    'values': initial_cols,
                    'fill': {'color': '#007bff'},
                    'font': {'color': 'white', 'size': 12}
                },
                'cells': {
                    'values': [df[col].tolist() for col in initial_cols],
                    'fill': {'color': ['#f8f9fa', 'white']},
                    'font': {'size': 11},
                    'height': 30
                }
            }],
            'layout': {
                'title': f'Batch Data: {filename} (Showing {len(initial_cols)} of {len(df.columns)} columns)',
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
    
    components = [header, controls_card, table]
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
            
            # Create form with INI config content
            parsed_config = data_storage.get('parsed_config', {})
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
        if contents is None:
            return "No batch data loaded"
        
        # Load CSV data directly in this callback to avoid timing issues
        try:
            # Parse INI file
            decoded = base64.b64decode(contents.split(',')[1]).decode('utf-8')
            config = configparser.ConfigParser()
            config.read_string(decoded)
            config_dict = {}
            for section in config.sections():
                config_dict[section] = dict(config[section])
            
            # Check for batch_data_file in Input Info section
            if "Input Info" in config_dict:
                input_info = config_dict["Input Info"]
                if "batch_data_file" in input_info:
                    csv_path = input_info["batch_data_file"]
                    
                    # Get full path to INI file
                    full_path = os.path.abspath(filename) if filename else "Unknown path"
                    
                    # Check if path is relative or absolute
                    if not os.path.isabs(csv_path):
                        # Make relative to INI file directory
                        ini_dir = os.path.dirname(full_path)
                        csv_path = os.path.join(ini_dir, csv_path)
                    
                    # Load CSV file
                    if os.path.exists(csv_path):
                        df = pd.read_csv(csv_path)
                        # Store in global storage for other callbacks
                        add_data('csv_batch_data', df)
                        add_data('csv_filename', os.path.basename(csv_path))
                        return create_csv_table(df, os.path.basename(csv_path))
                    else:
                        return html.Div([
                            html.H6("CSV file not found", className="text-warning"),
                            html.P(f"Could not find CSV file at: {csv_path}")
                        ])
                else:
                    return html.Div([
                        html.H6("No batch_data_file found", className="text-warning"),
                        html.P("The INI file does not contain a 'batch_data_file' key in the 'Input Info' section")
                    ])
            else:
                return html.Div([
                    html.H6("No Input Info section found", className="text-warning"),
                    html.P("The INI file does not contain an 'Input Info' section")
                ])
        except Exception as e:
            return html.Div([
                html.H6("Error loading data", className="text-danger"),
                html.P(f"Error: {str(e)}")
            ])
    
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
    
    # Callback for column search functionality
    @app.callback(
        dash.dependencies.Output('column-selector', 'options'),
        [dash.dependencies.Input('column-search', 'value')],
        prevent_initial_call=True
    )
    def filter_column_options(search_term):
        """Filter column options based on search term"""
        data_storage = get_data_storage()
        if 'csv_batch_data' not in data_storage or data_storage['csv_batch_data'] is None:
            return []
        
        df = data_storage['csv_batch_data']
        all_columns = df.columns.tolist()
        
        if not search_term:
            return [{"label": col, "value": col} for col in all_columns]
        
        # Filter columns that contain the search term (case insensitive)
        filtered_columns = [col for col in all_columns if search_term.lower() in col.lower()]
        return [{"label": col, "value": col} for col in filtered_columns]
    
    # Callback for updating table based on selected columns
    @app.callback(
        dash.dependencies.Output('csv-data-table', 'figure'),
        [dash.dependencies.Input('column-selector', 'value')],
        prevent_initial_call=True
    )
    def update_table_display(selected_columns):
        """Update table display based on selected columns"""
        data_storage = get_data_storage()
        if 'csv_batch_data' not in data_storage or data_storage['csv_batch_data'] is None:
            return {'data': [], 'layout': {'title': 'No data available'}}
        
        df = data_storage['csv_batch_data']
        filename = data_storage.get('csv_filename', 'Unknown')
        
        if not selected_columns:
            selected_columns = df.columns[:10].tolist() if len(df.columns) > 10 else df.columns.tolist()
        
        # Create table with selected columns
        table_data = [{
            'type': 'table',
            'header': {
                'values': selected_columns,
                'fill': {'color': '#007bff'},
                'font': {'color': 'white', 'size': 12}
            },
            'cells': {
                'values': [df[col].tolist() for col in selected_columns],
                'fill': {'color': ['#f8f9fa', 'white']},
                'font': {'size': 11},
                'height': 30
            }
        }]
        
        return {
            'data': table_data,
            'layout': {
                'title': f'Batch Data: {filename} (Showing {len(selected_columns)} of {len(df.columns)} columns)',
                'height': min(600, 200 + len(df) * 30),
                'margin': {'l': 10, 'r': 10, 't': 50, 'b': 10}
            }
        }
    
    # Callback for select all columns button
    @app.callback(
        dash.dependencies.Output('column-selector', 'value', allow_duplicate=True),
        [dash.dependencies.Input('select-all-cols', 'n_clicks')],
        prevent_initial_call=True
    )
    def select_all_columns(n_clicks):
        """Select all columns when button is clicked"""
        if n_clicks:
            data_storage = get_data_storage()
            if 'csv_batch_data' in data_storage and data_storage['csv_batch_data'] is not None:
                return data_storage['csv_batch_data'].columns.tolist()
        return dash.no_update
    
    # Callback for clear all columns button
    @app.callback(
        dash.dependencies.Output('column-selector', 'value', allow_duplicate=True),
        [dash.dependencies.Input('clear-all-cols', 'n_clicks')],
        prevent_initial_call=True
    )
    def clear_all_columns(n_clicks):
        """Clear all column selections when button is clicked"""
        if n_clicks:
            return []
        return dash.no_update
    
    # Callback for reset view button
    @app.callback(
        [dash.dependencies.Output('column-selector', 'value', allow_duplicate=True),
         dash.dependencies.Output('column-search', 'value', allow_duplicate=True)],
        [dash.dependencies.Input('reset-view', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_table_view(n_clicks):
        """Reset table view to show first 10 columns"""
        if n_clicks:
            data_storage = get_data_storage()
            if 'csv_batch_data' in data_storage and data_storage['csv_batch_data'] is not None:
                df = data_storage['csv_batch_data']
                initial_cols = df.columns[:10].tolist() if len(df.columns) > 10 else df.columns.tolist()
                return initial_cols, ""
        return dash.no_update, dash.no_update
