#!/usr/bin/env python3
"""
Shared Utilities Module
Common functionality used across the energy analytics application
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

class DataUtils:
    """Utilities for data processing and validation"""
    
    @staticmethod
    def get_network_name(data_dict: Dict[str, pd.DataFrame]) -> str:
        """Extract network name from any dataset"""
        for df in data_dict.values():
            if not df.empty and 'network' in df.columns:
                return df['network'].iloc[0]
        return 'NEM'  # Default fallback
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, required_columns: List[str] = None) -> bool:
        """Validate DataFrame has required structure"""
        if df is None or df.empty:
            return False
        
        if required_columns:
            return all(col in df.columns for col in required_columns)
        
        return True
    
    @staticmethod
    def safe_convert_datetime(df: pd.DataFrame, column: str = 'timestamp') -> pd.DataFrame:
        """Safely convert datetime column"""
        df_copy = df.copy()
        if column in df_copy.columns:
            df_copy[column] = pd.to_datetime(df_copy[column])
        return df_copy
    
    @staticmethod
    def calculate_basic_stats(df: pd.DataFrame, value_column: str = 'value') -> Dict[str, Any]:
        """Calculate basic statistics for a dataset"""
        if not DataUtils.validate_dataframe(df, [value_column]):
            return {'error': 'Invalid data'}
        
        values = df[value_column]
        stats = {
            'count': len(values),
            'min': float(values.min()),
            'max': float(values.max()),
            'mean': float(values.mean()),
            'std': float(values.std()) if len(values) > 1 else 0.0
        }
        
        # Add date range if timestamp exists
        if 'timestamp' in df.columns:
            df_datetime = DataUtils.safe_convert_datetime(df)
            stats['date_range'] = {
                'start': df_datetime['timestamp'].min(),
                'end': df_datetime['timestamp'].max()
            }
        
        return stats

class FileUtils:
    """Utilities for file operations"""
    
    @staticmethod
    def ensure_directory(path: str) -> None:
        """Create directory if it doesn't exist"""
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def get_project_root() -> str:
        """Get the project root directory"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(current_dir))
    
    @staticmethod
    def get_docs_path() -> str:
        """Get the docs directory path"""
        return os.path.join(FileUtils.get_project_root(), 'docs')
    
    @staticmethod
    def get_data_path() -> str:
        """Get the data directory path"""
        return os.path.join(FileUtils.get_project_root(), 'App', 'Data')
    
    @staticmethod
    def save_json(data: Any, filepath: str) -> bool:
        """Save data to JSON file"""
        try:
            FileUtils.ensure_directory(os.path.dirname(filepath))
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"❌ Error saving JSON to {filepath}: {e}")
            return False
    
    @staticmethod
    def load_json(filepath: str) -> Optional[Any]:
        """Load data from JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON from {filepath}: {e}")
        return None

class FormatUtils:
    """Utilities for data formatting and display"""
    
    @staticmethod
    def format_number(value: Union[int, float], precision: int = 2) -> str:
        """Format number with appropriate precision"""
        if abs(value) >= 1e9:
            return f"{value/1e9:.{precision}f}B"
        elif abs(value) >= 1e6:
            return f"{value/1e6:.{precision}f}M"
        elif abs(value) >= 1e3:
            return f"{value/1e3:.{precision}f}K"
        else:
            return f"{value:.{precision}f}"
    
    @staticmethod
    def format_currency(value: Union[int, float], precision: int = 2) -> str:
        """Format value as currency"""
        formatted = FormatUtils.format_number(abs(value), precision)
        sign = "-" if value < 0 else ""
        return f"${sign}{formatted}"
    
    @staticmethod
    def format_power(value: Union[int, float], precision: int = 0) -> str:
        """Format power value with MW unit"""
        formatted = FormatUtils.format_number(value, precision)
        return f"{formatted} MW"
    
    @staticmethod
    def format_date_range(start_date: datetime, end_date: datetime) -> str:
        """Format date range for display"""
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        return f"{start_str} to {end_str}"
    
    @staticmethod
    def get_dataset_display_name(dataset_key: str) -> str:
        """Convert dataset key to display-friendly name"""
        display_names = {
            'monthly_24months': 'MONTHLY 24MONTHS',
            'hourly_1month': 'HOURLY 1MONTH',
            'fivemin_1week': 'FIVEMIN 1WEEK'
        }
        return display_names.get(dataset_key, dataset_key.upper().replace('_', ' '))

class ValidationUtils:
    """Utilities for data validation and error checking"""
    
    @staticmethod
    def check_data_availability(power_data: Dict, market_data: Dict) -> Dict[str, bool]:
        """Check which datasets are available"""
        availability = {}
        
        datasets = ['monthly_24months', 'hourly_1month', 'fivemin_1week']
        for dataset in datasets:
            power_available = (dataset in power_data and 
                             DataUtils.validate_dataframe(power_data[dataset]))
            market_available = (dataset in market_data and 
                              DataUtils.validate_dataframe(market_data[dataset]))
            availability[dataset] = power_available and market_available
        
        return availability
    
    @staticmethod
    def validate_plot_requirements(power_data: Dict, market_data: Dict, dataset_key: str) -> bool:
        """Validate that both power and market data are available for plotting"""
        return (dataset_key in power_data and dataset_key in market_data and
                DataUtils.validate_dataframe(power_data[dataset_key]) and
                DataUtils.validate_dataframe(market_data[dataset_key]))

class TrendAnalyzer:
    """Utilities for trend analysis"""
    
    @staticmethod
    def analyze_trend_direction(values: List[float]) -> str:
        """Analyze trend direction from values"""
        if len(values) < 2:
            return 'insufficient_data'
        
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        return 'increasing' if second_half > first_half else 'decreasing'
    
    @staticmethod
    def find_peak_period(df: pd.DataFrame, value_column: str = 'value') -> int:
        """Find the month with peak values"""
        if not DataUtils.validate_dataframe(df, [value_column, 'timestamp']):
            return 1
        
        df_datetime = DataUtils.safe_convert_datetime(df)
        df_datetime['month'] = df_datetime['timestamp'].dt.month
        monthly_avg = df_datetime.groupby('month')[value_column].mean()
        return int(monthly_avg.idxmax())
    
    @staticmethod
    def find_low_period(df: pd.DataFrame, value_column: str = 'value') -> int:
        """Find the month with lowest values"""
        if not DataUtils.validate_dataframe(df, [value_column, 'timestamp']):
            return 1
        
        df_datetime = DataUtils.safe_convert_datetime(df)
        df_datetime['month'] = df_datetime['timestamp'].dt.month
        monthly_avg = df_datetime.groupby('month')[value_column].mean()
        return int(monthly_avg.idxmin())
    
    @staticmethod
    def calculate_volatility(values: List[float]) -> float:
        """Calculate volatility index (coefficient of variation)"""
        if len(values) < 2:
            return 0.0
        
        mean_val = sum(values) / len(values)
        if mean_val == 0:
            return 0.0
        
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        return std_dev / abs(mean_val)
    
    @staticmethod
    def analyze_dataset_trends(df: pd.DataFrame, value_column: str = 'value') -> Dict[str, Any]:
        """Complete trend analysis for a dataset"""
        if not DataUtils.validate_dataframe(df, [value_column]):
            return {'error': 'Invalid data for trend analysis'}
        
        values = df[value_column].tolist()
        
        return {
            'trend_direction': TrendAnalyzer.analyze_trend_direction(values),
            'peak_month': TrendAnalyzer.find_peak_period(df, value_column),
            'low_month': TrendAnalyzer.find_low_period(df, value_column),
            'volatility': TrendAnalyzer.calculate_volatility(values)
        }