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
    
    # Initialize the app with light gray/blue theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.LUX,  # Light professional theme
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"  # Font Awesome icons
        ],
        suppress_callback_exceptions=True,
        assets_folder='assets'
    )
    
    # Set app title
    app.title = "Batch Slug Test Analysis"
    
    # Add custom CSS for light gray/blue theme
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                /* Light Gray & Blue Theme - Professional */
                body {
                    background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 50%, #bbdefb 100%) !important;
                    color: #2c3e50 !important;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
                }
                
                /* Light Gray & Blue Tab Styling */
                .nav-tabs {
                    border-bottom: 3px solid #2196f3 !important;
                    margin-bottom: 25px !important;
                    display: flex !important;
                    flex-wrap: nowrap !important;
                    gap: 0 !important;
                }
                .nav-tabs .nav-link {
                    font-size: 16px !important;
                    font-weight: 600 !important;
                    padding: 12px 40px !important;
                    margin: 0 !important;
                    margin-right: 0 !important;
                    margin-left: 0 !important;
                    border-radius: 0px !important;
                    background-color: #f5f5f5 !important;
                    border: 2px solid #e0e0e0 !important;
                    border-right: none !important;
                    color: #2c3e50 !important;
                    transition: all 0.3s ease !important;
                    flex: 1 !important;
                    text-align: center !important;
                    position: relative !important;
                }
                .nav-tabs .nav-link:not(:last-child) {
                    margin-right: -2px !important;
                }
                .nav-tabs .nav-link:first-child {
                    border-radius: 8px 0 0 0 !important;
                }
                .nav-tabs .nav-link:last-child {
                    border-radius: 0 8px 0 0 !important;
                    border-right: 2px solid #e0e0e0 !important;
                }
                .nav-tabs .nav-link:hover {
                    background-color: #e3f2fd !important;
                    transform: translateY(-2px) !important;
                    color: #1976d2 !important;
                    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2) !important;
                }
                .nav-tabs .nav-link.active {
                    background-color: #2196f3 !important;
                    border-color: #2196f3 !important;
                    color: white !important;
                    font-weight: 600 !important;
                    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3) !important;
                }
                
                /* Light Gray & Blue Card Styling */
                .card {
                    border-radius: 12px !important;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
                    border: 1px solid #e0e0e0 !important;
                    background-color: #ffffff !important;
                }
                .card-header {
                    background: linear-gradient(135deg, #f5f5f5 0%, #e3f2fd 100%) !important;
                    border-bottom: 2px solid #2196f3 !important;
                    font-weight: 600 !important;
                    color: #2c3e50 !important;
                    border-radius: 12px 12px 0 0 !important;
                }
                
                /* Light Gray & Blue Button Styling */
                .btn {
                    border-radius: 8px !important;
                    font-weight: 500 !important;
                    transition: all 0.3s ease !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.5px !important;
                }
                .btn:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15) !important;
                }
                .btn-primary {
                    background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%) !important;
                    border: none !important;
                }
                .btn-primary:hover {
                    background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
                }
                .btn-success {
                    background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%) !important;
                    border: none !important;
                }
                .btn-info {
                    background: linear-gradient(135deg, #03a9f4 0%, #0288d1 100%) !important;
                    border: none !important;
                }
                
                /* Light Gray & Blue Input Styling */
                .form-control {
                    border-radius: 8px !important;
                    border: 2px solid #e0e0e0 !important;
                    background-color: #ffffff !important;
                    color: #2c3e50 !important;
                    padding: 12px 16px !important;
                }
                .form-control:focus {
                    border-color: #2196f3 !important;
                    box-shadow: 0 0 0 0.2rem rgba(33, 150, 243, 0.25) !important;
                    background-color: #ffffff !important;
                }
                
                /* Light Gray & Blue Table Styling */
                .table {
                    border-radius: 12px !important;
                    overflow: hidden !important;
                    background-color: #ffffff !important;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
                }
                .table thead th {
                    background: linear-gradient(135deg, #f5f5f5 0%, #e3f2fd 100%) !important;
                    border-bottom: 3px solid #2196f3 !important;
                    font-weight: 600 !important;
                    color: #2c3e50 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.5px !important;
                }
                .table tbody tr:hover {
                    background-color: #e3f2fd !important;
                }
                
                /* Light Gray & Blue Navbar Styling */
                .navbar {
                    background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%) !important;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
                }
                .navbar .navbar-brand {
                    color: #ffffff !important;
                    font-weight: bold !important;
                }
                .navbar .navbar-text {
                    color: #ffffff !important;
                }
                
                /* Light Gray & Blue Dropdown Styling */
                .dropdown-menu {
                    border-radius: 8px !important;
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1) !important;
                    border: 1px solid #e0e0e0 !important;
                    background-color: #ffffff !important;
                }
                
                /* Light Gray & Blue Alert Styling */
                .alert {
                    border-radius: 8px !important;
                    border: none !important;
                }
                .alert-info {
                    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
                    color: #1976d2 !important;
                }
                .alert-warning {
                    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%) !important;
                    color: #f57c00 !important;
                }
                
                /* Light Gray & Blue Progress Bar */
                .progress {
                    border-radius: 8px !important;
                    background-color: #e0e0e0 !important;
                }
                .progress-bar {
                    background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%) !important;
                }
                
                /* Smooth Animations */
                * {
                    transition: all 0.3s ease !important;
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