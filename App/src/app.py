#!/usr/bin/env python3

import sys

from config import Config, ConsoleMessages, ErrorMessages
from fetch import fetch_power_and_market_data
from plots import generate_energy_plots
from report_generator import generate_energy_report

def main():
    """Main function for dual analytics"""
    
    print(ConsoleMessages.APP_HEADER)
    
    try:
        # Check if running in non-interactive mode (GitHub Actions)
        if not sys.stdin.isatty():
            print(f"\n{ConsoleMessages.STATUS['automated_mode']}")
            confirm = 'y'
        else:
            confirm = input(f"\n{ConsoleMessages.PROMPTS['generate_plots']}").strip().lower()
        
        if confirm != 'y':
            print(ConsoleMessages.PROMPTS['cancelled'])
            return
        
        print(f"\n{ConsoleMessages.STATUS['fetching_data']}")
        
        # Always fetch fresh data (disable cache)
        print("🔄 Fetching fresh data (cache disabled)")
        use_cache = False
        
        # Fetch POWER + MARKET_VALUE
        all_data = fetch_power_and_market_data(Config.DEFAULT_NETWORK, use_cache=use_cache)
        power_data = all_data.get('power', {})
        market_data = all_data.get('market_value', {})
        
        if not power_data and not market_data:
            print(ErrorMessages.DATA_FETCH_ERROR)
            return
        
        print(f"✅ Got Power: {len(power_data)} datasets, Market Value: {len(market_data)} datasets")
        
        print(f"\n{ConsoleMessages.STATUS['generating_plots']}")
        plots_info = generate_energy_plots(power_data=power_data, market_data=market_data)
        
        print(f"\n{ConsoleMessages.STATUS['generating_report']}")
        report_path = generate_energy_report(power_data=power_data, market_data=market_data)
        
        completion_msg = ConsoleMessages.COMPLETION_MESSAGE.format(plot_count=len(plots_info))
        print(f"\n{completion_msg}")
        if report_path:
            print(f"   • Report saved: {report_path}")
        
    except KeyboardInterrupt:
        print(f"\n\n{ConsoleMessages.PROMPTS['user_cancelled']}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure you have:")
        print("   • Internet connection")
        print("   • Required packages installed")

if __name__ == "__main__":
    main()
