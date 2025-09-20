"""
Global Data Storage
==================
Simplified data storage with two functions: get_data_storage and add_data.
"""

# Global data storage dictionary
_data_storage = {}

def get_data_storage():
    """Get the global data storage dictionary"""
    return _data_storage

def add_data(key, value):
    """Add data to the global storage"""
    _data_storage[key] = value
