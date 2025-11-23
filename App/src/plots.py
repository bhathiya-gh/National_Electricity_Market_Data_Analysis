#!/usr/bin/env python3
"""
Simplified Plotting Module
Refactored with reusable components and reduced complexity
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import utilities and configuration
from utils import DataUtils, FileUtils, ValidationUtils, FormatUtils
from config import Config

class PlotBuilder:
    """Reusable plot building components"""
    
    @staticmethod
    def setup_figure() -> Tuple[plt.Figure, plt.Axes]:
        """Create and configure base figure"""
        fig, ax = plt.subplots(figsize=Config.PLOT_CONFIG['figure_size'])
        return fig, ax
    
    @staticmethod
    def setup_dual_axis(ax: plt.Axes, 
                       power_data: pd.DataFrame, 
                       market_data: pd.DataFrame,
                       title: str) -> Tuple[plt.Axes, plt.Axes]:
        """Setup dual-axis plot with power and market data"""
        colors = Config.get_color_scheme()
        style = Config.PLOT_CONFIG['style']
        
        # Setup primary axis (power)
        ax.set_xlabel('Date and Time', fontsize=12, fontweight='bold')
        ax.set_ylabel('Power Consumption (MW)', color=colors['power'], fontsize=12, fontweight='bold')
        ax.plot(power_data['timestamp'], power_data['value'], 
               color=colors['power'], linewidth=style['line_width'], 
               alpha=style['alpha'], label='Power Consumption')
        ax.tick_params(axis='y', labelcolor=colors['power'])
        ax.grid(True, alpha=style['grid_alpha'])
        
        # Setup secondary axis (market)
        ax2 = ax.twinx()
        ax2.set_ylabel('Market Value (AUD)', color=colors['market'], fontsize=12, fontweight='bold')
        ax2.plot(market_data['timestamp'], market_data['value'], 
                color=colors['market'], linewidth=style['line_width'], 
                alpha=style['alpha'], label='Market Value')
        ax2.tick_params(axis='y', labelcolor=colors['market'])
        
        # Add title
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        
        return ax, ax2
    
    @staticmethod
    def add_legend(ax1: plt.Axes, ax2: plt.Axes) -> None:
        """Add combined legend to dual-axis plot"""
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', 
                  frameon=True, fancybox=True, shadow=True, fontsize=10)
    
    @staticmethod
    def finalize_plot(filepath: str) -> None:
        """Finalize and save plot"""
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(filepath, dpi=Config.PLOT_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

class EnergyPlotter:
    """Simplified energy data plotter"""
    
    def __init__(self, power_data: Dict[str, pd.DataFrame], market_data: Dict[str, pd.DataFrame]):
        """Initialize with data"""
        self.power_data = power_data
        self.market_data = market_data
        self.network = DataUtils.get_network_name(power_data)
        self.docs_dir = FileUtils.get_docs_path()
        FileUtils.ensure_directory(self.docs_dir)
    
    def generate_all_plots(self) -> List[Dict]:
        """Generate all available plots"""
        plots_info = []
        
        print("📊 Generating combined energy data plots...")
        
        # Get data availability
        availability = ValidationUtils.check_data_availability(self.power_data, self.market_data)
        
        # Generate plots for available datasets
        plot_generators = {
            'monthly_24months': self._create_combined_plot,
            'hourly_1month': self._create_combined_plot,
            'fivemin_1week': self._create_combined_plot
        }
        
        for dataset_key, is_available in availability.items():
            if is_available:
                plot_info = plot_generators[dataset_key](dataset_key)
                if plot_info:
                    plots_info.append(plot_info)
        
        # Generate daily averages plot if hourly data is available
        if availability.get('hourly_1month', False):
            daily_plot = self._create_daily_averages_plot()
            if daily_plot:
                plots_info.append(daily_plot)
        
        # Save plots information
        self._save_plots_info(plots_info)
        
        print(f"✅ Generated {len(plots_info)} combined plots in {self.docs_dir}")
        return plots_info
    
    def _create_combined_plot(self, dataset_key: str) -> Optional[Dict]:
        """Generic combined plot generator"""
        try:
            plot_config = Config.get_plot_config(dataset_key)
            if not plot_config:
                return None
            
            # Prepare data
            power_df = DataUtils.safe_convert_datetime(self.power_data[dataset_key])
            market_df = DataUtils.safe_convert_datetime(self.market_data[dataset_key])
            
            # Setup plot
            filepath = os.path.join(self.docs_dir, plot_config['filename'])
            fig, ax1 = PlotBuilder.setup_figure()
            
            # Create dual-axis plot
            full_title = f"{self.network} - {plot_config['title']}"
            ax1, ax2 = PlotBuilder.setup_dual_axis(ax1, power_df, market_df, full_title)
            
            # Add dataset-specific formatting
            if dataset_key == 'monthly_24months':
                self._customize_monthly_plot(ax1, ax2)
            
            # Add legend and finalize
            PlotBuilder.add_legend(ax1, ax2)
            PlotBuilder.finalize_plot(filepath)
            
            print(f"✅ Generated: {plot_config['filename']}")
            return {
                'filename': plot_config['filename'],
                'title': plot_config['short_title'],
                'description': plot_config['description']
            }
            
        except Exception as e:
            print(f"❌ Error creating {dataset_key} plot: {e}")
            plt.close()
            return None
    
    def _create_daily_averages_plot(self) -> Optional[Dict]:
        """Create 24-hour pattern averages plot"""
        try:
            plot_config = Config.get_plot_config('daily_averages')
            
            # Prepare hourly data
            power_df = DataUtils.safe_convert_datetime(self.power_data['hourly_1month'])
            market_df = DataUtils.safe_convert_datetime(self.market_data['hourly_1month'])
            
            # Calculate hourly averages and convert to DataFrame format
            power_hourly = self._calculate_hourly_averages(power_df)
            market_hourly = self._calculate_hourly_averages(market_df)
            
            # Convert to DataFrame for consistent plotting
            power_plot_df = pd.DataFrame({
                'timestamp': power_hourly.index,
                'value': power_hourly.values
            })
            market_plot_df = pd.DataFrame({
                'timestamp': market_hourly.index,
                'value': market_hourly.values
            })
            
            # Setup plot
            filepath = os.path.join(self.docs_dir, plot_config['filename'])
            fig, ax1 = PlotBuilder.setup_figure()
            
            # Use existing dual-axis setup with custom labels
            full_title = f"{self.network} - {plot_config['title']}"
            ax1, ax2 = PlotBuilder.setup_dual_axis(ax1, power_plot_df, market_plot_df, full_title)
            
            # Customize for hourly display
            self._customize_hourly_plot(ax1, ax2)
            
            # Add legend and finalize
            PlotBuilder.add_legend(ax1, ax2)
            PlotBuilder.finalize_plot(filepath)
            
            print(f"✅ Generated: {plot_config['filename']}")
            return {
                'filename': plot_config['filename'],
                'title': plot_config['short_title'],
                'description': plot_config['description']
            }
            
        except Exception as e:
            print(f"❌ Error creating daily averages plot: {e}")
            plt.close()
            return None
    
    def _customize_hourly_plot(self, ax1: plt.Axes, ax2: plt.Axes) -> None:
        """Customize plot for hourly data display"""
        # Update labels for hourly context
        ax1.set_xlabel('Hour of Day (0-23)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Power (MW)', color=Config.get_color_scheme()['power'], fontsize=12, fontweight='bold')
        ax2.set_ylabel('Average Market Value (AUD)', color=Config.get_color_scheme()['market'], fontsize=12, fontweight='bold')
        
        # Set hourly-specific formatting
        ax1.set_xlim(0, 23)
        ax1.set_xticks(range(0, 24, 2))
        
        # Add markers for better visibility
        style = Config.PLOT_CONFIG['style']
        for line in ax1.get_lines():
            line.set_marker('o')
            line.set_markersize(style['marker_size'])
        for line in ax2.get_lines():
            line.set_marker('s')
            line.set_markersize(style['marker_size'])
    
    def _customize_monthly_plot(self, ax1: plt.Axes, ax2: plt.Axes) -> None:
        """Customize plot for monthly data display"""
        style = Config.PLOT_CONFIG['style']
        
        # Add markers for monthly data points
        for line in ax1.get_lines():
            line.set_marker('o')
            line.set_markersize(style['marker_size'])
        for line in ax2.get_lines():
            line.set_marker('s')
            line.set_markersize(style['marker_size'])
        
        # Format currency axis for billions
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e9:.1f}B'))

    def _calculate_hourly_averages(self, df: pd.DataFrame) -> pd.Series:
        """Calculate average values for each hour of the day"""
        df_copy = df.copy()
        df_copy['hour'] = df_copy['timestamp'].dt.hour
        return df_copy.groupby('hour')['value'].mean()
    
    def _save_plots_info(self, plots_info: List[Dict]) -> None:
        """Save plots information to JSON"""
        plots_data = {
            'plots': plots_info,
            'generated_at': datetime.now().isoformat(),
            'network': self.network,
            'total_plots': len(plots_info)
        }
        
        json_path = os.path.join(self.docs_dir, 'plots_info.json')
        FileUtils.save_json(plots_data, json_path)

def generate_energy_plots(power_data: Dict[str, pd.DataFrame], 
                         market_data: Dict[str, pd.DataFrame]) -> List[Dict]:
    """Main function to generate all energy plots"""
    plotter = EnergyPlotter(power_data, market_data)
    return plotter.generate_all_plots()

if __name__ == "__main__":
    print("📊 Energy Data Plotting Module")
    print("Use this module with data from fetch.py")