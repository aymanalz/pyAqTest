"""
Main Dash Application for Batch Slug Test Analysis
================================================
Clean, consolidated version of the Dash app for slug test analysis.
"""

import dash
import dash_bootstrap_components as dbc

from dashboard import create_main_layout, register_callbacks

class DataStorage:
    pass

data_storage = DataStorage()

def create_app():
    """Create and configure the main Dash app"""
    
    # Initialize the app with Bootstrap theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
        assets_folder='assets'
    )
    
    # Set app title
    app.title = "Batch Slug Test Analysis"
    
    # Add custom CSS for larger, bolder tabs
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                .nav-tabs .nav-link {
                    font-size: 18px !important;
                    font-weight: bold !important;
                    padding: 15px 25px !important;
                    margin: 0 5px !important;
                    border-radius: 8px !important;
                    background-color: #f8f9fa !important;
                    border: 2px solid #dee2e6 !important;
                    color: #495057 !important;
                    transition: all 0.3s ease !important;
                }
                .nav-tabs .nav-link:hover {
                    background-color: #e9ecef !important;
                    border-color: #adb5bd !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
                }
                .nav-tabs .nav-link.active {
                    background-color: #007bff !important;
                    border-color: #007bff !important;
                    color: white !important;
                    font-weight: bold !important;
                    box-shadow: 0 4px 12px rgba(0,123,255,0.3) !important;
                }
                .nav-tabs {
                    border-bottom: 3px solid #dee2e6 !important;
                    margin-bottom: 20px !important;
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    
    # Set the layout
    app.layout = create_main_layout()
    
    # Register all callbacks
    register_callbacks(app)
    
    return app

def main():
    """Main function to run the app"""
    app = create_app()
    
    # Run the app
    app.run(
        debug=True,
        host='127.0.0.1',
        port=8050
    )

if __name__ == '__main__':
    main()