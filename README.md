# Australian National Electricity Market Analytics Dashboard

A comprehensive Python application for analyzing Australian electricity market data, providing insights into power generation and market value correlations across multiple time granularities.

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/australian-energy-analytics.git
   cd australian-energy-analytics
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv nem.env
   # Windows:
   nem.env\Scripts\activate
   # Linux/Mac:
   source nem.env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API credentials:**
   Create `App/credentials.txt`:
   ```
   OPENELECTRICITY_API_KEY=your_api_key_here
   ```

5. **Run the application:**
   ```bash
   cd App/src
   python app.py
   ```

## ✨ Features

- **🔄 Dual Metric Analysis**: Power generation and market value correlation
- **📊 Multi-Granularity Data**: Monthly (24mo), Hourly (1mo), Real-time (5min)
- **📈 Combined Visualizations**: Professional dual-axis line plots
- **🧠 Smart Caching**: 6-hour cache validity for efficient data management
- **📄 Professional Reports**: Comprehensive analytics in text format
- **🎯 Clean File Management**: Fixed filenames, no accumulation

## 📊 Data Analysis

### Time Periods
- **Monthly Trends**: 24 complete months (Oct 2023 - Sep 2025)
- **Hourly Patterns**: Past 30 days for demand analysis
- **Real-time Data**: 5-minute intervals for past 7 days

### Metrics Analyzed
- **Power Generation**: MW/GW capacity and output
- **Market Values**: $/MWh pricing and trends
- **Correlations**: How generation affects market pricing

## 🖼️ Visualizations

The application generates 4 combined analysis plots:

1. **Monthly Trends**: Long-term power vs market value correlation
2. **Daily Patterns**: Average hourly demand and pricing relationships
3. **Hourly Time Series**: Detailed generation vs market response
4. **Real-time Analysis**: 5-minute market dynamics and volatility

## 📁 Project Structure

```
australian-energy-analytics/
├── App/
│   ├── src/
│   │   ├── app.py          # Main application dashboard
│   │   ├── fetch.py        # Data fetching with smart caching
│   │   └── analytics.py    # Analytics and visualization engine
│   ├── Data/               # Cached data files (6 files max)
│   ├── Analytics/          # Output reports and charts (2 files)
│   └── credentials.txt     # API credentials (create this)
├── nem.env/                # Virtual environment
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## 🗺️ Architecture Diagram

```
   ┌────────────────────────────┐
   │  OpenElectricity API/AEMO │
   └────────────┬───────────────┘
           │
         [fetch.py]
           │
   ┌────────────▼────────────┐
   │   App/Data/ (cache)     │
   └────────────┬────────────┘
           │
   ┌────────────▼────────────┐
   │  Analytics & Plots      │
   │ (analytics.py, plots.py)│
   └────────────┬────────────┘
           │
   ┌────────────▼────────────┐
   │ Report Generator        │
   │ (report_generator.py)   │
   └────────────┬────────────┘
           │
   ┌────────────▼────────────┐
   │   docs/ (output)        │
   └────────────┬────────────┘
           │
   ┌────────────▼────────────┐
   │   index.html (Dashboard)│
   └────────────┬────────────┘
           │
   ┌────────────▼────────────┐
   │ GitHub Actions Workflow │
   │  (automation & deploy)  │
   └─────────────────────────┘
```

## 🏗️ Project Architecture

The application is organized into modular components for clarity, maintainability, and automation:

**1. Data Fetching (`fetch.py`)**
   - Handles all API communication with OpenElectricity (AEMO data)
   - Downloads and caches power and market value datasets in `App/Data/`
   - Smart caching: avoids redundant API calls if data is fresh

**2. Analytics & Visualization (`plots.py`, `analytics.py`)**
   - Processes raw data into combined and comparative analytics
   - Generates 4 key visualizations (monthly, daily, hourly, real-time)
   - Saves all charts as PNGs in the `docs/` folder for dashboard use

**3. Report Generation (`report_generator.py`)**
   - Produces a dynamic HTML analytics report (`dual_energy_report.html`)
   - Summarizes statistics, trends, and insights for both power and market data
   - Output is saved in `docs/` for web access

**4. Main Application (`app.py`)**
   - Orchestrates the workflow: fetch → analyze → plot → report
   - Detects if running in CI/CD (GitHub Actions) to force fresh data
   - Entry point for both local and automated runs

**5. Automation (GitHub Actions Workflow)**
   - `.github/workflows/update-analytics.yml` schedules daily runs (cron) and on push
   - Runs the full pipeline, commits new results, and deploys to GitHub Pages

**6. Dashboard (`docs/` folder)**
   - Contains all generated charts, reports, and the main `index.html` dashboard
   - Served automatically via GitHub Pages for public access

**Data Flow:**

1. **Fetch:** `fetch.py` downloads and caches data in `App/Data/`
2. **Analyze & Plot:** `plots.py` and `analytics.py` process data and generate PNG charts in `docs/`
3. **Report:** `report_generator.py` creates an HTML report in `docs/`
4. **Dashboard:** All outputs are linked in `docs/index.html` for easy viewing
5. **Automation:** GitHub Actions runs the above steps daily, updating the dashboard and reports automatically

This modular architecture ensures the project is easy to maintain, extend, and automate for reliable daily analytics updates.

## 🔧 Technical Details

### Dependencies
- `pandas` - Data manipulation and analysis
- `matplotlib` - Professional visualization
- `numpy` - Numerical computing
- `openelectricity` - Australian energy market API
- `python-dotenv` - Environment variable management
- `seaborn` - Statistical visualization enhancement

### API Requirements
Requires OpenElectricity API key from [openelectricity.org](https://openelectricity.org)

### Cache Management
- **Data Files**: 6 fixed files (3 per metric)
- **Analytics Files**: 2 fixed files (report + chart)
- **Auto-refresh**: Files older than 6 hours are updated
- **No accumulation**: Old files are overwritten

## � Sample Output

```
⚡════════════════════════════════════════════════════════════⚡
           AUSTRALIAN ENERGY ANALYTICS DASHBOARD
⚡════════════════════════════════════════════════════════════⚡

📊 ANALYSIS SCOPE:
   🔹 Power Generation Data
   🔹 Market Value Data
   🔹 Combined Correlation Analysis

📅 DATA PERIODS:
   📈 Monthly Trends    : 24 months (Oct 2023 → Sep 2025)
   ⏰ Hourly Patterns   : 1 month (Past 30 days)
   ⚡ Real-time Data    : 1 week (5-minute intervals)

� START ANALYSIS? [y/N]: y

🔄 FETCHING DATA...
   └─ Connecting to Australian Energy Market API...
   ✅ Data fetch completed successfully!

🔬 RUNNING ANALYTICS...
   └─ Processing correlation analysis...
   📊 Creating combined visualizations...

✅════════════════════════════════════════════════════════════✅
               ANALYSIS COMPLETED SUCCESSFULLY!
✅════════════════════════════════════════════════════════════✅
```

## 🚨 Troubleshooting

**No data retrieved?**
- Check internet connection
- Verify API key in `App/credentials.txt`
- Ensure API key is valid and active

**Import errors?**
- Run `pip install -r requirements.txt`
- Activate virtual environment first

**Permission errors?**
- Check write permissions for `Analytics/` and `Data/` folders
- Run as administrator if necessary

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-analysis`)
3. Commit changes (`git commit -am 'Add new analysis feature'`)
4. Push to branch (`git push origin feature/new-analysis`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

### Third-Party APIs & Data Sources
- **[OpenElectricity API](https://openelectricity.org)** - API access layer for Australian electricity market data
- **[Australian Energy Market Operator (AEMO)](https://aemo.com.au)** - **Original data source and authoritative provider** of all National Electricity Market (NEM) data
- **National Electricity Market (NEM)** - Australia's wholesale electricity market operated by AEMO

### Data Attribution & Compliance
**Primary Data Source**: All electricity market data originates from the Australian Energy Market Operator (AEMO), accessed through the OpenElectricity API interface.

**AEMO Data Usage**: This application complies with AEMO's open data policy and terms for non-commercial research and analysis purposes. All data remains property of AEMO.

### Open Source Libraries
- **[pandas](https://pandas.pydata.org/)** - Data manipulation and analysis
- **[matplotlib](https://matplotlib.org/)** - Visualization and plotting framework
- **[seaborn](https://seaborn.pydata.org/)** - Statistical data visualization
- **[numpy](https://numpy.org/)** - Numerical computing foundation
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** - Environment variable management

### Special Thanks
- **OpenElectricity team** for providing accessible API access to Australian energy data
- **Python scientific computing community** for robust data analysis ecosystem
- **AEMO** for maintaining transparent and open electricity market data

### Data Attribution
**Data Source Hierarchy**:
1. **AEMO (Australian Energy Market Operator)** - Authoritative source of all NEM market data
2. **OpenElectricity API** - Technical interface providing programmatic access to AEMO data
3. **This Application** - Analytics and visualization layer

**Legal Notice**: This application uses electricity market data originally collected and published by the Australian Energy Market Operator (AEMO). The data is accessed through the OpenElectricity API under AEMO's open data terms. All market data remains the intellectual property of AEMO and is used in accordance with their data usage policies.

**Data Accuracy**: While this application processes AEMO data accurately, users should refer to official AEMO publications for authoritative market information and regulatory compliance.

Test1