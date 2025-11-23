#!/usr/bin/env python3
"""
Data Fetcher for Energy Analytics
Simplified and refactored data fetching with reusable components
"""


from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd
import os
from typing import Dict, Optional

# Import utilities and configuration
from utils import DataUtils, FileUtils, ValidationUtils
from config import Config, ErrorMessages

# Load environment variables from .env
load_dotenv()

from openelectricity import OEClient
from openelectricity.types import DataMetric

class EnergyDataFetcher:
    """Simplified and cleaned up data fetcher"""
    
    def __init__(self, network_code: str = Config.DEFAULT_NETWORK):
        """Initialize the fetcher with configuration"""
        self.client = OEClient()
        self.network_code = network_code
        self.data_dir = FileUtils.get_data_path()
        FileUtils.ensure_directory(self.data_dir)
    
    def fetch_data(self, metric: str = 'POWER', use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """Fetch all required datasets using configuration"""
        results = {}
        
        for dataset_key, config in Config.DATASETS.items():
            print(f"[DEBUG] Fetching {dataset_key} (metric={metric}, use_cache={use_cache})...")
            if use_cache:
                cached_df = self._load_from_cache(dataset_key, metric)
                if cached_df is not None:
                    print(f"[DEBUG] Loaded {dataset_key} from cache ({len(cached_df)} records)")
                    results[dataset_key] = cached_df
                    continue
            # Fetch fresh data
            df = self._fetch_dataset(dataset_key, config, metric)
            if df is not None:
                print(f"[DEBUG] API returned {len(df)} records for {dataset_key}")
                results[dataset_key] = df
                self._save_to_cache(df, dataset_key, metric)
                print(f"[DEBUG] Saved {dataset_key} to cache as CSV.")
            else:
                print(f"[DEBUG] Failed to fetch {dataset_key} from API.")
        print(f"[DEBUG] fetch_data complete. Results: { {k: len(v) for k,v in results.items()} }")
        return results
    
    def _fetch_dataset(self, dataset_key: str, config: dict, metric: str) -> Optional[pd.DataFrame]:
        """Fetch a single dataset from the API"""
        try:
            start_date, end_date = self._calculate_date_range(config)
            metric_enum = self._get_metric_enum(metric)
            
            response = self.client.get_network_data(
                network_code=self.network_code,
                metrics=[metric_enum],
                interval=config['interval'],
                date_start=start_date,
                date_end=end_date
            )
            
            return self._process_api_response(response, config, dataset_key)
            
        except Exception as e:
            print(ErrorMessages.format_error('PLOT_GENERATION_ERROR', 
                                           plot_type=dataset_key, error=str(e)))
            return None
    
    def _calculate_date_range(self, config: dict) -> tuple[datetime, datetime]:
        """Calculate date range based on configuration"""
        end_date = datetime.now()
        
        if config.get('exclude_current_month', False) and 'months_back' in config:
            # Monthly data logic - exclude current month
            current_date = datetime.now()
            if current_date.month == 1:
                end_date = datetime(current_date.year - 1, 12, 1, 0, 0, 0)
            else:
                end_date = datetime(current_date.year, current_date.month - 1, 1, 0, 0, 0)
            
            # Calculate start date
            months_back = config['months_back']
            total_months = end_date.year * 12 + end_date.month - months_back
            start_year = total_months // 12
            start_month = total_months % 12
            if start_month == 0:
                start_month = 12
                start_year -= 1
            
            start_date = datetime(start_year, start_month, 1)
        else:
            # Days-based logic
            start_date = end_date - timedelta(days=config['days_back'])
        
        return start_date, end_date
    
    def _get_metric_enum(self, metric: str) -> DataMetric:
        """Convert metric string to enum"""
        metric_enum = getattr(DataMetric, metric.upper(), None)
        if not metric_enum:
            raise ValueError(ErrorMessages.format_error('INVALID_METRIC', metric=metric))
        return metric_enum
    
    def _process_api_response(self, response, config: dict, dataset_key: str) -> Optional[pd.DataFrame]:
        """Process API response into DataFrame"""
        if not response or not response.data:
            return None
        
        df_data = []
        for series in response.data:
            if series.results:
                for result in series.results:
                    for point in result.data:
                        timestamp, value = point.root
                        df_data.append({
                            'timestamp': timestamp,
                            'value': value,
                            'metric': series.metric,
                            'unit': series.unit,
                            'interval': config['interval'],
                            'network': series.network_code
                        })
        
        if df_data:
            df = pd.DataFrame(df_data)
            df = DataUtils.safe_convert_datetime(df)
            return df.sort_values('timestamp')
        
        return None
    
    def _get_cache_filename(self, dataset_key: str, metric: str) -> str:
        """Generate cache filename"""
        return f"{self.network_code}_{metric}_{dataset_key}.csv"
    
    def _save_to_cache(self, df: pd.DataFrame, dataset_key: str, metric: str) -> None:
        """Save DataFrame to cache"""
        try:
            filename = self._get_cache_filename(dataset_key, metric)
            filepath = os.path.join(self.data_dir, filename)
            print(f"[DEBUG] Saving {dataset_key} to {filepath} (metric={metric})")
            df_save = df.copy()
            df_save['fetch_timestamp'] = datetime.now()
            df_save['dataset_type'] = dataset_key
            df_save.to_csv(filepath, index=False)
            print(f"[DEBUG] CSV write complete for {filepath} ({len(df_save)} records)")
        except Exception as e:
            print(ErrorMessages.format_error('CACHE_SAVE_ERROR', 
                                           dataset=dataset_key, error=str(e)))
    
    def _load_from_cache(self, dataset_key: str, metric: str) -> Optional[pd.DataFrame]:
        """Load DataFrame from cache if fresh"""
        try:
            filename = self._get_cache_filename(dataset_key, metric)
            filepath = os.path.join(self.data_dir, filename)
            print(f"[DEBUG] Attempting to load cache for {dataset_key} from {filepath}")
            if not os.path.exists(filepath):
                print(f"[DEBUG] Cache file does not exist: {filepath}")
                return None
            # Check cache age
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))
            age_hours = (datetime.now() - file_time).total_seconds() / 3600
            print(f"[DEBUG] Cache age for {dataset_key}: {age_hours:.2f} hours (expiry={Config.CACHE_EXPIRY_HOURS} hours)")
            if age_hours > Config.CACHE_EXPIRY_HOURS:
                print(f"[DEBUG] Cache expired for {dataset_key}")
                return None
            df = pd.read_csv(filepath)
            print(f"[DEBUG] Loaded {len(df)} records from cache for {dataset_key}")
            return DataUtils.safe_convert_datetime(df)
        except Exception as e:
            print(ErrorMessages.format_error('CACHE_LOAD_ERROR', 
                                           dataset=dataset_key, error=str(e)))
            return None

# Simplified public interface functions
def fetch_energy_data(network: str = Config.DEFAULT_NETWORK, 
                     metric: str = 'POWER', 
                     use_cache: bool = True) -> Dict[str, pd.DataFrame]:
    """Fetch energy data for a single metric"""
    fetcher = EnergyDataFetcher(network)
    return fetcher.fetch_data(metric, use_cache)

def fetch_power_and_market_data(network: str = Config.DEFAULT_NETWORK, 
                               use_cache: bool = True) -> Dict[str, Dict[str, pd.DataFrame]]:
    """Fetch both POWER and MARKET_VALUE data"""
    print("🔌 Fetching POWER data...")
    power_data = fetch_energy_data(network, 'POWER', use_cache)
    
    print("💰 Fetching MARKET_VALUE data...")
    market_data = fetch_energy_data(network, 'MARKET_VALUE', use_cache)
    
    return {
        'power': power_data,
        'market_value': market_data
    }

# Backward compatibility
def get_power_data(network_code: str = Config.DEFAULT_NETWORK, 
                  force_refresh: bool = False) -> Dict[str, pd.DataFrame]:
    """Legacy function for backward compatibility"""
    return fetch_energy_data(network_code, 'POWER', not force_refresh)

if __name__ == "__main__":
    # Test the fetcher
    print("🔌 Testing Energy Data Fetcher")
    print("=" * 40)
    
    data = fetch_energy_data('NEM', 'POWER', use_cache=True)
    
    if data:
        print(f"\n📊 Successfully fetched {len(data)} datasets:")
        for dataset_key, df in data.items():
            date_range = df['timestamp'].max() - df['timestamp'].min()
            print(f"  • {dataset_key}: {len(df)} records over {date_range.days} days")
    else:
        print("❌ No data retrieved")