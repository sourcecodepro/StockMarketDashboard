# The Executive Terminal 📈💼



> An institutional-grade stock analytics and portfolio intelligence platform featuring real-time market radar, deep technical X-rays, and automated executive decision support.



## 📖 Overview



**The Executive Terminal** is a comprehensive Python-based dashboard designed for institutional investors, portfolio managers, and serious traders. Built on top of Plotly Dash, it provides a centralized command center to analyze individual stocks, track active portfolio holdings, evaluate macroeconomic sector rotations, and instantly generate executive-ready PDF and Excel intelligence reports.



## 🛠️ Tech Stack



![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)

![Plotly Dash](https://img.shields.io/badge/Dash-Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)

![YFinance](https://img.shields.io/badge/YFinance-Market_Data-00A859?style=for-the-badge)

![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E92063?style=for-the-badge&logo=pydantic&logoColor=white)



*   **Core Framework:** Dash, Dash Bootstrap Components

*   **Data Processing:** Pandas, NumPy, SciPy, PyArrow

*   **Data Acquisition:** yfinance, Flask-Caching

*   **Visualizations:** Plotly, Matplotlib

*   **Reporting:** ReportLab (PDF), OpenPyXL (Excel)



## ✨ Key Features



*   **🔍 Stock X-Ray:** Deep-dive into individual assets with Price & Technical Alignment charts (EMA 20/50/200, RSI), a 5-axis Fundamental Radar, and Peer Comparative Multiples matrices.

*   **📊 Market Radar:** Visualize macroeconomic trends with Multi-Period Sector Performance Heatmaps, Market Breadth tracking, and Dynamic Treemaps.

*   **💼 Portfolio Intelligence:** Import custom `.csv` portfolios to unlock Portfolio KPI tracking, Cross-Asset Pearson Correlation Matrices, and Risk metrics (Beta, Sharpe Ratio).

*   **🤖 Automated Decision Support:** An integrated rules engine analyzes technical overlaps and fundamental valuation multiples to generate actionable executive takeaways.

*   **🖨️ One-Click Executive Exports:** Generate professionally formatted PDF intelligence briefings or multi-sheet Excel workbooks instantly.

*   **🎨 Dynamic Theming:** Switch seamlessly between Formal Dark (Slate), Corporate Light, and Cyborg Terminal themes.

*   **🛡️ Data Hygiene Engine:** Built-in Data Health Score (DHS) tracks data completeness, handles missing indicators, and provides fallback offline caching mechanisms.



## 🗂️ Folder Structure



```text

└── sourcecodepro-stockmarketdashboard/

    ├── app.py                      # Main Dash application entry point

    ├── pyproject.toml              # Project dependencies and metadata

    ├── assets/                     # CSS stylesheets and dynamic themes

    │   ├── custom.css

    │   ├── theme_cyborg.css

    │   ├── theme_dark.css

    │   └── theme_light.css

    ├── components/                 # UI components and dashboard tabs

    │   ├── navbar.py

    │   ├── sidebar.py

    │   ├── tab_market.py

    │   ├── tab_portfolio.py

    │   └── tab_stock.py

    ├── core/                       # Analytics, engines, and export logic

    │   ├── chart_exporter.py       # Matplotlib static chart generation

    │   ├── data_engine.py          # Market data acquisition & caching

    │   ├── excel_exporter.py       # OpenPyXL workbook formatting

    │   ├── fundamentals.py         # Valuation & peer matrix logic

    │   ├── insight_engine.py       # Automated takeaway generation

    │   ├── market_engine.py        # Sector rotation & breadth math

    │   ├── pdf_exporter.py         # ReportLab PDF building

    │   ├── risk_engine.py          # Portfolio risk metrics (Beta/Sharpe)

    │   ├── sanitization.py         # Data validation & imputation

    │   ├── schemas.py              # Pydantic data models

    │   ├── symbol_search.py        # Ticker autocomplete logic

    │   ├── technicals.py           # EMA/RSI indicator math

    │   └── telemetry.py            # DHS tracking & logging

    ├── data/                       # Local offline fallback data & median JSONs

    └── docs/                       # Architecture documentation and SRS

```



## 🚀 Setup & Prerequisites



### Prerequisites

*   Python 3.11 or higher

*   Git



### Installation



1. **Clone the repository:**

   ```bash

   git clone https://github.com/yourusername/executive-terminal.git

   cd executive-terminal/sourcecodepro-stockmarketdashboard

   ```



2. **Create a virtual environment (recommended):**

   ```bash

   python -m venv venv

   source venv/bin/activate  # On Windows use: venv\Scripts\activate

   ```



3. **Install dependencies:**

   Since the project uses `pyproject.toml`, you can install it via pip:

   ```bash

   pip install .

   ```

   *(Alternatively, if you export a `requirements.txt`, run `pip install -r requirements.txt`)*



## 💻 Usage Instructions



1. **Start the Application:**

   Run the main application file from your terminal:

   ```bash

   python app.py

   ```

2. **Access the Dashboard:**

   Open your web browser and navigate to `http://127.0.0.1:8050/`.

3. **Analyze Stocks:** 

   Use the left sidebar to search for any global ticker symbol (e.g., `AAPL`, `RELIANCE.NS`) or click the quick-access watchlist buttons.

4. **Upload a Portfolio:**

   Drag and drop a CSV file containing your portfolio holdings into the sidebar to activate the **Portfolio Terminal** tab.

5. **Export Intelligence:**

   Click the "Executive Report" button in the top navigation bar to view a summary modal, and select either **Export PDF** or **Export Excel** for offline reporting.



## 📄 License



This project is licensed under the MIT License - see the LICENSE file for details.