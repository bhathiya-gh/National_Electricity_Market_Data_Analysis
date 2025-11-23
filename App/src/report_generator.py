#!/usr/bin/env python3
"""
Report Generator Module
Generate dynamic HTML reports with current data statistics
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional

# Import utilities and configuration
from utils import DataUtils, FileUtils, FormatUtils, TrendAnalyzer
from config import Config, ErrorMessages, ConsoleMessages

class EnergyReportGenerator:
    """Generate comprehensive energy data reports"""
    
    def __init__(self, power_data: Dict[str, pd.DataFrame], market_data: Dict[str, pd.DataFrame]):
        """Initialize with power and market data"""
        self.power_data = power_data
        self.market_data = market_data
        self.network = DataUtils.get_network_name(power_data)
        self.docs_dir = FileUtils.get_docs_path()
        FileUtils.ensure_directory(self.docs_dir)
    
    def _calculate_all_stats(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """Calculate statistics for all datasets using utilities"""
        stats = {}
        for dataset_key, df in data_dict.items():
            if DataUtils.validate_dataframe(df):
                stats[dataset_key] = DataUtils.calculate_basic_stats(df)
            else:
                stats[dataset_key] = {'error': 'Invalid or empty dataset'}
        return stats
    
    def _analyze_dataset_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze trends using TrendAnalyzer utilities"""
        if not DataUtils.validate_dataframe(df, ['value']):
            return {'error': 'No data for trend analysis'}
        
        return TrendAnalyzer.analyze_dataset_trends(df)
    
    def _build_html_report(self, report_data: Dict) -> str:
        """Build complete HTML report from data"""
        html_parts = [
            self._get_html_header(report_data['timestamp']),
            self._build_data_section('Power', report_data['power_stats'], report_data['power_trends'], 'MW'),
            self._build_data_section('Market Value', report_data['market_stats'], report_data['market_trends'], 'AUD'),
            self._get_html_footer()
        ]
        return ''.join(html_parts)
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive HTML report with current data using clean template format"""
        
        # Calculate statistics for all datasets using utilities
        power_stats = self._calculate_all_stats(self.power_data)
        market_stats = self._calculate_all_stats(self.market_data)
        
        # Analyze trends using TrendAnalyzer
        power_trends = self._analyze_dataset_trends(self.power_data.get('monthly_24months', pd.DataFrame()))
        market_trends = self._analyze_dataset_trends(self.market_data.get('monthly_24months', pd.DataFrame()))
        
        # Generate report data
        report_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'network': self.network,
            'power_stats': power_stats,
            'market_stats': market_stats,
            'power_trends': power_trends,
            'market_trends': market_trends,
            'totals': {
                'power_records': sum(len(df) for df in self.power_data.values()),
                'market_records': sum(len(df) for df in self.market_data.values())
            }
        }
        
        return self._build_html_report(report_data)
    
    def _get_html_header(self, timestamp: str) -> str:
        """Generate HTML header with CSS"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{Config.REPORT_CONFIG['title']}</title>
    {self._get_css_styles()}
</head>
<body>
    <div class="container">
        <div class="technical-report-link">
            <a href="./index.html">📊 Back to Dashboard</a>
        </div>
        <h1>{Config.REPORT_CONFIG['title']}</h1>
        <div class="timestamp">
            📊 Generated: {timestamp}<br>
            {Config.REPORT_CONFIG['update_message']}
        </div>"""
    
    def _get_html_footer(self) -> str:
        """Generate HTML footer"""
        return """
        <div class="technical-report-link">
            <a href="./index.html">📊 Back to Dashboard</a>
        </div>
    </div>
</body>
</html>"""
    
    def _build_data_section(self, section_title: str, stats: Dict, trends: Dict, unit_suffix: str) -> str:
        """Build a complete data section"""
        icon = "🔌" if "Power" in section_title else "💰"
        metric_name = "power" if "Power" in section_title else "market_value"
        unit_display = "MW" if unit_suffix == "MW" else "AUD ($)"
        
        section = f"""
        <h2>{icon} {section_title} Data Analysis</h2>
        <div class="metric-info">
            <strong>Network:</strong> {self.network} &nbsp;&nbsp;
            <strong>Metric:</strong> {metric_name} &nbsp;&nbsp;
            <strong>Unit:</strong> {unit_display}
        </div>"""
        
        # Add dataset sections
        for dataset_key, dataset_stats in stats.items():
            if 'error' not in dataset_stats:
                section += self._build_dataset_section(dataset_key, dataset_stats, unit_suffix)
        
        # Add insights section
        if 'error' not in trends:
            section += self._build_insights_section(section_title, trends)
        
        return section
    
    def _build_insights_section(self, section_title: str, trends: Dict) -> str:
        """Build insights section with trend analysis in grid format"""
        return f"""
        <div class="insights-section">
            <div class="insights-title">💡 {section_title} Insights</div>
            <div class="insights-grid">
                <div class="insight-item">
                    <div class="insight-label">Trend Direction</div>
                    <div class="insight-value">{trends.get('trend_direction', 'Unknown').title()}</div>
                </div>
                <div class="insight-item">
                    <div class="insight-label">Peak Month</div>
                    <div class="insight-value">{trends.get('peak_month', 'Unknown')}</div>
                </div>
                <div class="insight-item">
                    <div class="insight-label">Low Month</div>
                    <div class="insight-value">{trends.get('low_month', 'Unknown')}</div>
                </div>
                <div class="insight-item">
                    <div class="insight-label">Volatility Index</div>
                    <div class="insight-value">{trends.get('volatility', 0):.3f}</div>
                </div>
            </div>
        </div>"""
    
    def _get_css_styles(self) -> str:
        """Return CSS styles using configuration"""
        colors = Config.get_ui_colors()
        fonts = Config.UI_CONFIG['fonts']
        spacing = Config.UI_CONFIG['spacing']
        
        return f"""<style>
        body {{
            font-family: {fonts['main']};
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, {colors['gradient_start']} 0%, {colors['gradient_end']} 100%);
            color: #333;
            min-height: 100vh;
            line-height: 1.6;
        }}
        .container {{
            background: white;
            padding: {spacing['container_padding']};
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: {colors['primary']};
            text-align: center;
            margin-bottom: 10px;
            font-size: {fonts['title_size']};
            font-weight: 700;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-style: italic;
            background: linear-gradient(135deg, #e8f4f8 0%, #d4edda 100%);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid {colors['primary']};
        }}
        h2 {{
            color: {colors['secondary']};
            border-bottom: 3px solid {colors['secondary']};
            padding-bottom: 10px;
            margin-top: 40px;
            font-size: 1.8em;
        }}
        .metric-info {{
            background: linear-gradient(135deg, #e8f4f8 0%, #f0f8ff 100%);
            padding: 15px 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 5px solid {colors['primary']};
            font-size: 1.05em;
        }}
        .dataset-section {{
            margin: 30px 0;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 0;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .dataset-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            padding: 15px 25px;
            margin: 0;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0;
            background: white;
        }}
        .stats-table tr {{
            border-bottom: 1px solid #e9ecef;
        }}
        .stats-table tr:last-child {{
            border-bottom: none;
        }}
        .stats-table td {{
            padding: 15px 25px;
            font-size: 1.05em;
        }}
        .stats-table td:first-child {{
            font-weight: 600;
            color: #495057;
            width: 35%;
            background: #f8f9fa;
        }}
        .stats-table td:last-child {{
            color: {colors['primary']};
            font-weight: 500;
        }}
        .insights-section {{
            background: linear-gradient(135deg, #fff9e6 0%, #ffeaa7 100%);
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
            border-left: 5px solid {colors['warning']};
        }}
        .insights-title {{
            font-weight: 700;
            color: {colors['warning_text']};
            margin: 0 0 15px 0;
            font-size: 1.3em;
        }}
        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .insight-item {{
            background: white;
            padding: 12px 15px;
            border-radius: 6px;
            font-size: 1em;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .insight-label {{
            font-weight: 600;
            color: #856404;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .insight-value {{
            color: #495057;
            margin-top: 4px;
            font-size: 1.1em;
        }}
        .technical-report-link {{ 
            text-align: center; 
            margin: 25px 0; 
        }}
        .technical-report-link a {{ 
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white; 
            text-decoration: none; 
            font-weight: bold; 
            font-size: {fonts['button_size']}; 
            padding: 15px 30px;
            border-radius: 25px;
            transition: transform 0.3s ease;
            display: inline-block;
        }}
        .technical-report-link a:hover {{ transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0,0,0,0.2); }}
    </style>"""
    
    def _build_dataset_section(self, dataset_key: str, stats: Dict, unit_suffix: str) -> str:
        """Build a dataset section with formatted statistics in table format"""
        dataset_display = FormatUtils.get_dataset_display_name(dataset_key)
        
        # Format values based on unit type
        if unit_suffix == 'AUD':
            min_val = FormatUtils.format_currency(stats['min'])
            max_val = FormatUtils.format_currency(stats['max'])
            avg_val = FormatUtils.format_currency(stats['mean'])
            std_val = FormatUtils.format_currency(stats['std'])
        else:  # MW
            min_val = FormatUtils.format_power(stats['min'])
            max_val = FormatUtils.format_power(stats['max'])
            avg_val = FormatUtils.format_power(stats['mean'])
            std_val = FormatUtils.format_power(stats['std'])
        
        # Build date range if available
        date_range_row = ""
        if stats.get('date_range'):
            start_date = stats['date_range']['start']
            end_date = stats['date_range']['end']
            date_range = FormatUtils.format_date_range(start_date, end_date)
            date_range_row = f"""
                <tr>
                    <td>Time Period</td>
                    <td>{date_range}</td>
                </tr>"""
        
        section = f"""
        <div class="dataset-section">
            <div class="dataset-title">{dataset_display}</div>
            <table class="stats-table">
                <tr>
                    <td>Total Records</td>
                    <td>{stats['count']:,}</td>
                </tr>{date_range_row}
                <tr>
                    <td>Minimum Value</td>
                    <td>{min_val}</td>
                </tr>
                <tr>
                    <td>Maximum Value</td>
                    <td>{max_val}</td>
                </tr>
                <tr>
                    <td>Average Value</td>
                    <td>{avg_val}</td>
                </tr>
                <tr>
                    <td>Standard Deviation</td>
                    <td>{std_val}</td>
                </tr>
            </table>
        </div>"""
        
        return section
    
    def save_report(self) -> str:
        """Generate and save the comprehensive report"""
        try:
            report_html = self.generate_comprehensive_report()
            report_path = os.path.join(self.docs_dir, 'dual_energy_report.html')
            
            if FileUtils.save_json({'html': report_html}, report_path.replace('.html', '_temp.json')):
                # Save as HTML file
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(report_html)
                
                print(f"📄 Dynamic report saved to {report_path}")
                return report_path
            else:
                raise Exception("Failed to save report data")
            
        except Exception as e:
            print(ErrorMessages.format_error('FILE_SAVE_ERROR', 
                                           filepath=report_path, error=str(e)))
            return ""
    
def generate_energy_report(power_data: Dict[str, pd.DataFrame], 
                          market_data: Dict[str, pd.DataFrame]) -> str:
    """
    Main function to generate energy data report
    
    Args:
        power_data: Dictionary containing power datasets
        market_data: Dictionary containing market datasets
        
    Returns:
        Path to generated report file
    """
    generator = EnergyReportGenerator(power_data, market_data)
    return generator.save_report()

if __name__ == "__main__":
    print("📊 Energy Report Generator Module")
    print("Use this module with data from fetch.py")