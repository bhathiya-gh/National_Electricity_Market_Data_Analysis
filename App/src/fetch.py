import os
from datetime import datetime
import pandas as pd
from typing import Optional, Dict

# ... other imports remain ...

class EnergyDataFetcher:
    """Simplified and cleaned up data fetcher"""
    
    def __init__(self, network_code: str = Config.DEFAULT_NETWORK):
        """Initialize the fetcher with configuration"""
        self.client = OEClient()
        self.network_code = network_code

        # === ENSURE data_dir points to repo-relative App/Data ===
        # If FileUtils provides a path, prefer that; otherwise set repo root / App/Data
        try:
            candidate = FileUtils.get_data_path()
        except Exception:
            candidate = None

        if candidate and os.path.isabs(candidate):
            self.data_dir = candidate
        else:
            # use repo root relative path (cwd is repo root when run by GH Actions)
            self.data_dir = os.path.join(os.getcwd(), "App", "Data")

        # create directory if missing
        os.makedirs(self.data_dir, exist_ok=True)
        # You can also keep FileUtils.ensure_directory for compatibility:
        try:
            FileUtils.ensure_directory(self.data_dir)
        except Exception:
            pass

    def _get_cache_filename(self, dataset_key: str, metric: str) -> str:
        """Generate cache filename"""
        # prefer simple, consistent filenames
        safe_dataset = dataset_key.replace(" ", "_")
        safe_metric = metric.upper()
        return f"{self.network_code}_{safe_metric}_{safe_dataset}.csv"

    def _save_to_cache(self, df: pd.DataFrame, dataset_key: str, metric: str) -> None:
        """Save DataFrame to cache (overwrite behaviour)"""
        try:
            filename = self._get_cache_filename(dataset_key, metric)
            filepath = os.path.join(self.data_dir, filename)
            
            df_save = df.copy()
            # add a fetch timestamp column for traceability (optional)
            df_save['fetch_timestamp'] = datetime.utcnow().isoformat()
            df_save['dataset_type'] = dataset_key

            # ensure directory exists (defensive)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # overwrite the file each time (this matches "keep newest only")
            df_save.to_csv(filepath, index=False)
            print(f"📦 Saved cache to {filepath}")

        except Exception as e:
            print(ErrorMessages.format_error('CACHE_SAVE_ERROR', 
                                           dataset=dataset_key, error=str(e)))

    def _load_from_cache(self, dataset_key: str, metric: str) -> Optional[pd.DataFrame]:
        """Load DataFrame from cache if fresh"""
        try:
            filename = self._get_cache_filename(dataset_key, metric)
            filepath = os.path.join(self.data_dir, filename)
            
            if not os.path.exists(filepath):
                return None
            
            # Check cache age (creation time)
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))
            age_hours = (datetime.utcnow() - file_time).total_seconds() / 3600.0
            
            if age_hours > Config.CACHE_EXPIRY_HOURS:
                print(f"🕒 Cache expired for {filename} (age {age_hours:.1f}h > {Config.CACHE_EXPIRY_HOURS}h)")
                return None
            
            df = pd.read_csv(filepath)
            df = DataUtils.safe_convert_datetime(df)
            print(f"📥 Loaded cache from {filepath} ({len(df)} rows, age {age_hours:.1f}h)")
            return df
            
        except Exception as e:
            print(ErrorMessages.format_error('CACHE_LOAD_ERROR', 
                                           dataset=dataset_key, error=str(e)))
            return None
