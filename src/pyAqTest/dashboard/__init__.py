"""
Dashboard Package
================
Dashboard components for the Batch Slug Test Analysis application.
"""

from .layout import create_main_layout
from .callbacks import register_callbacks
from .components import (
    create_upload_area,
    create_analysis_controls,
    create_analysis_plot,
    create_summary_card,
    create_export_card,
    create_analysis_settings_card,
    create_display_settings_card,
    create_results_table
)

__all__ = [
    'create_main_layout',
    'register_callbacks',
    'create_upload_area',
    'create_analysis_controls',
    'create_analysis_plot',
    'create_summary_card',
    'create_export_card',
    'create_analysis_settings_card',
    'create_display_settings_card',
    'create_results_table'
]
