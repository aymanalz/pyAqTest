"""
Dashboard Utilities
==================
Utility functions for the dashboard.
"""

import configparser
import os
from .data_storage import add_data

def read_ini_file(filename):
    """Read INI file and add all items to data storage"""
    if not os.path.exists(filename):
        print(f"Error: INI file not found: {filename}")
        return False
    
    try:
        # Create config parser
        config = configparser.ConfigParser()
        config.read(filename)
        
        # Add file info to storage
        add_data('ini_filename', filename)
        add_data('ini_file_path', os.path.abspath(filename))
        
        # Add all sections and their items to storage
        for section_name in config.sections():
            for key, value in config.items(section_name):
                # Add each item with section_key format
                storage_key = f"{section_name}_{key}"
                add_data(storage_key, value)
                print(f"Added to storage: {storage_key} = {value}")
        
        # Add sections list
        add_data('ini_sections', config.sections())
        
        print(f"Successfully loaded INI file: {filename}")
        print(f"Found {len(config.sections())} sections: {config.sections()}")
        
        return True
        
    except Exception as e:
        print(f"Error reading INI file {filename}: {str(e)}")
        return False
