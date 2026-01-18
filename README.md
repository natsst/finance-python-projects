# Finance Python Projects

This repository contains interactive finance applications built in Python, focused on
company valuation and financial analysis, inspired by real-world practices in
investment banking, M&A, and corporate finance.

The projects are designed to be:
- Finance-driven (no toy examples)
- Technically clean and structured
- Fully interactive via Streamlit
- Easy to run using a single launcher

---

## Projects Overview

### Comparable Companies (Trading Multiples)

Interactive application to perform a full Comparable Companies Analysis (Comps).

Main features:
- Peer set loading (default dataset or custom CSV)
- Automatic computation of trading multiples:
  - EV / Revenue
  - EV / EBITDA
  - P / E
- Target company exclusion from peer set
- Outlier treatment via winsorization
- Statistical summary (mean, median, percentiles)
- Implied equity value calculation using median multiples
- Export options:
  - Peer multiples (CSV)
  - Valuation summary (TXT)

Project folder:
01_comps/

---

### Discounted Cash Flow (DCF) Valuation Model

Interactive DCF valuation model with full transparency on assumptions and outputs.

Main features:
- Operating assumptions input (growth, margins, CAPEX, NWC, tax rate)
- Free Cash Flow build-up
- WACC computation (model-based or manual)
- Terminal value using Gordon Growth
- Enterprise Value to Equity Value bridge
- Sensitivity analysis (WACC × terminal growth)
- Export options:
  - Excel valuation model
  - Text valuation summary

Project folder:
02_dcf/

---

## How to Run the Apps (Single Launcher)

1. Install dependencies:
pip install -r requirements.txt

2. Launch the finance apps:
./run_finance_apps.command

You will be prompted to choose:
1) Comparable Companies (Comps)
2) DCF Valuation Model

The selected app will automatically open in your browser.

---

## Repository Structure

finance-python-projects/
├── 01_comps/
│   ├── app.py
│   ├── data/
│   │   └── raw/peers.csv
│   ├── src/
│   └── reports/
├── 02_dcf/
│   ├── app.py
│   ├── data/
│   ├── src/
│   └── reports/
├── run_finance_apps.command
├── requirements.txt
├── README.md
└── .gitignore

---

## Tech Stack

- Python 3
- Streamlit
- Pandas / NumPy
- Matplotlib
- OpenPyXL

---

## Disclaimer

These projects are for educational and demonstration purposes only and do not constitute
investment advice.

---

## Author

Nathan Susset

---

## Topics

python, finance, corporate-finance, valuation, financial-modeling, streamlit
