"""
Main Dash Application for Batch Slug Test Analysis
================================================
Clean, consolidated version of the Dash app for slug test analysis.
"""

import dash
import dash_bootstrap_components as dbc

from dashboard import create_main_layout, register_callbacks

def create_app():
    """Create and configure the main Dash app"""
    
    # Initialize the app with default Bootstrap theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,  # Default Bootstrap theme
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"  # Font Awesome icons
        ],
        suppress_callback_exceptions=True,
        assets_folder='assets'
    )
    
    # Set app title
    app.title = "Batch Slug Test Analysis"
    
    # Use default Dash index and theme (no custom index_string)
    
    # Set the layout
    app.layout = create_main_layout()
    
    # Register all callbacks
    register_callbacks(app)
    
    return app

def main():
    """Main function to run the app"""
    # Example: Read INI file and add to data storage
    # You can call this function with any INI filename
    # read_ini_file("config.ini")
    
    app = create_app()
    
    # Run the app
    app.run(
        debug=True,
        host='127.0.0.1',
        port=8050
    )

if __name__ == '__main__':
    main()