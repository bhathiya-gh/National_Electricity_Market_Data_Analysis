#!/usr/bin/env python3
"""
Configuration Module
Centralized configuration for the energy analytics application
"""

from typing import Dict, List, Tuple
import os

class Config:
    """Main configuration class"""
    
    # Network settings
    DEFAULT_NETWORK = 'NEM'
    
    # Data settings
    CACHE_EXPIRY_HOURS = 1/60  # 1 minute
    DEFAULT_METRICS = ['POWER', 'MARKET_VALUE']
    
    # Dataset configurations
    DATASETS = {
        'monthly_24months': {
            'interval': '1M',
            'months_back': 23,
            'exclude_current_month': True,
            'display_name': 'Monthly (24 Months)',
            'short_name': 'Monthly'
        },
        'hourly_1month': {
            'interval': '1h',
            'days_back': 30,
            'display_name': 'Hourly (1 Month)',
            'short_name': 'Hourly'
        },
        'fivemin_1week': {
            'interval': '5m',
            'days_back': 7,
            'display_name': '5-Minute (1 Week)',
            'short_name': '5-Minute'
        }
    }
    
    # File paths
    CREDENTIAL_PATHS = ['../credentials.txt', '../../App/credentials.txt', './credentials.txt']
    
    # Plot settings
    PLOT_CONFIG = {
        'figure_size': (16, 8),
        'dpi': 300,
        'color_scheme': {
            'power': '#2E86AB',
            'market': '#A23B72',
            'gradient_start': '#2E86AB',
            'gradient_end': '#A23B72'
        },
        'style': {
            'line_width': 2.5,
            'marker_size': 4,
            'alpha': 0.8,
            'grid_alpha': 0.3
        }
    }
    
    # HTML/CSS styling
    UI_CONFIG = {
        'colors': {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'gradient_start': '#667eea',
            'gradient_end': '#764ba2',
            'success': '#28a745',
            'warning': '#ffc107',
            'warning_bg': '#fff3cd',
            'warning_text': '#856404'
        },
        'fonts': {
            'main': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
            'title_size': '2.5em',
            'subtitle_size': '1.2em',
            'button_size': '1.3em'
        },
        'spacing': {
            'container_padding': '40px',
            'section_margin': '30px',
            'item_gap': '20px'
        }
    }
    
    # Report settings
    REPORT_CONFIG = {
        'title': '🔌⚡ Dynamic Energy Analytics Report',
        'dashboard_title': '📊 Australian Energy Analytics Dashboard',
        'subtitle': 'Comprehensive Power & Market Value Analysis | National Electricity Market (NEM)',
        'update_message': '🔄 Auto-updated with latest data from OpenElectricity API'
    }
    
    # Plot output configurations
    PLOT_OUTPUTS = {
        'monthly_24months': {
            'filename': 'combined_monthly_analysis.png',
            'title': 'Combined Monthly Analysis: Power & Market Trends (24 Months)',
            'short_title': '📊 Combined Monthly Analysis: Power & Market Trends',
            'description': 'Dual-axis chart showing both power consumption and market values over 24 months, revealing correlations between demand and pricing patterns.',
            'anchor_id': 'monthly-plot'
        },
        'hourly_1month': {
            'filename': 'combined_hourly_analysis.png',
            'title': 'Combined Hourly Analysis: Power & Market Patterns (1 Month)',
            'short_title': '⏰ Combined Hourly Analysis: Power & Market Patterns',
            'description': 'Hourly correlation between power consumption and market values over the past month, showing daily patterns and market dynamics.',
            'anchor_id': 'hourly-plot'
        },
        'fivemin_1week': {
            'filename': 'combined_fivemin_analysis.png',
            'title': 'Combined 5-Minute Analysis: Real-time Power & Market (1 Week)',
            'short_title': '⚡ Combined 5-Minute Analysis: Real-time Power & Market',
            'description': 'High-resolution view capturing rapid fluctuations with 5-minute intervals, essential for understanding real-time market behavior.',
            'anchor_id': 'fivemin-plot'
        },
        'daily_averages': {
            'filename': 'combined_daily_averages_analysis.png',
            'title': '24-Hour Period Averages: Hourly Patterns',
            'short_title': '📊 Daily Pattern Intelligence',
            'description': 'Average power consumption and market values for each hour of the day, revealing typical daily demand curves and pricing patterns.',
            'anchor_id': 'daily-plot'
        }
    }
    
    @classmethod
    def get_dataset_config(cls, dataset_key: str) -> Dict:
        """Get configuration for a specific dataset"""
        return cls.DATASETS.get(dataset_key, {})
    
    @classmethod
    def get_plot_config(cls, dataset_key: str) -> Dict:
        """Get plot configuration for a specific dataset"""
        return cls.PLOT_OUTPUTS.get(dataset_key, {})
    
    @classmethod
    def get_color_scheme(cls) -> Dict[str, str]:
        """Get the application color scheme"""
        return cls.PLOT_CONFIG['color_scheme']
    
    @classmethod
    def get_ui_colors(cls) -> Dict[str, str]:
        """Get UI color configuration"""
        return cls.UI_CONFIG['colors']

class ValidationConfig:
    """Configuration for data validation"""
    
    REQUIRED_COLUMNS = {
        'basic': ['timestamp', 'value'],
        'with_metadata': ['timestamp', 'value', 'metric', 'unit', 'network']
    }
    
    MIN_RECORDS = {
        'monthly_24months': 12,  # At least 12 months
        'hourly_1month': 24,     # At least 24 hours
        'fivemin_1week': 288     # At least 1 day worth of 5-min intervals
    }

class ErrorMessages:
    """Centralized error messages"""
    
    DATA_FETCH_ERROR = "❌ No data available. Check your internet connection and API credentials."
    INVALID_METRIC = "❌ Invalid metric: {metric}"
    CACHE_SAVE_ERROR = "⚠️ Warning: Could not save cache for {dataset}: {error}"
    CACHE_LOAD_ERROR = "⚠️ Warning: Could not load cache for {dataset}: {error}"
    PLOT_GENERATION_ERROR = "❌ Error creating {plot_type} plot: {error}"
    FILE_SAVE_ERROR = "❌ Error saving file to {filepath}: {error}"
    INSUFFICIENT_DATA = "❌ Insufficient data for {operation}"
    
    @classmethod
    def format_error(cls, error_type: str, **kwargs) -> str:
        """Format error message with parameters"""
        error_template = getattr(cls, error_type, "❌ Unknown error")
        return error_template.format(**kwargs)

class ConsoleMessages:
    """Centralized console output messages"""
    
    APP_HEADER = """⚡ ENERGY DATA PLOTTING
========================================
🔌 NEM Power & Market Value Analysis
📊 Monthly (24mo) + Hourly (1mo) + 5min (1wk)
📈 Combined & separate plot visualizations"""
    
    COMPLETION_MESSAGE = """✅ GENERATION COMPLETE!
📊 Check docs/ folder for:
   • {plot_count} combined visualization charts
   • Dynamic analytics report with current data
   • Interactive web dashboard
🎯 Generated plots and analytics report with live data"""
    
    PROMPTS = {
        'generate_plots': "▶ Generate energy plots? (y/n): ",
        'cancelled': "⏹ Cancelled.",
        'user_cancelled': "👋 Cancelled by user."
    }
    
    STATUS = {
        'fetching_data': "🔄 Fetching power and market value data...",
        'generating_plots': "🔬 Generating energy plots...",
        'generating_report': "📄 Generating dynamic analytics report...",
        'automated_mode': "🤖 Running in automated mode..."
    }