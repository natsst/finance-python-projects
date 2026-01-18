# Comparable Companies Analysis (Trading Multiples)

This project is an interactive **Comparable Companies (Comps) Analysis** application
built in Python using **Streamlit**, following professional **Corporate Finance / M&A**
standards.

It replicates a real-world **trading multiples valuation workflow**, from peer
selection to implied equity value estimation.

---

## Objective

The objective of this project is to:
- Build a clean and transparent Comparable Companies Analysis
- Analyze a peer group using trading multiples
- Exclude the target company from the peer set
- Control for outliers
- Derive implied equity values based on peer medians

The methodology is aligned with **sell-side and buy-side valuation practices**.

---

## Core Features

### Peer Dataset Handling
- Default peer dataset loaded from `data/raw/peers.csv`
- Optional CSV upload to replace the default peer set
- Automatic validation of required columns
- All financial figures are handled in **EUR millions**

---

### Enterprise Value Computation

Enterprise Value is calculated as:

EV = Market Capitalization + Net Debt

The following trading multiples are computed automatically:
- EV / Revenue
- EV / EBITDA
- P / E

---

### Target Company Valuation
- The selected target company is **excluded** from the peer group
- Median peer multiples are applied to target financials
- Implied Enterprise Value and Equity Value are computed
- Multiple valuation methods can be compared side by side

---

### Outlier Treatment
- Optional winsorization of trading multiples
- Customizable lower and upper percentile thresholds
- Improves robustness and credibility of valuation outputs

---

### Statistical Analysis
For each trading multiple, the app computes:
- Mean
- Median
- 25th percentile (P25)
- 75th percentile (P75)

---

### Exports
The app allows exporting:
- Peer multiples table (CSV)
- Valuation summary (TXT)

---

## Input Data Format

Default dataset location:

01_comps/data/raw/peers.csv

Required columns:
- company
- ticker
- currency
- market_cap_m
- net_debt_m
- revenue_ltm_m
- ebitda_ltm_m
- net_income_ltm_m

All monetary values must be expressed in **millions**.

---

## How to Run the App

From the repository root:

./run_finance_apps.command

Then select:

1) Comparable Companies (Comps)

The app will automatically open in your browser.

Alternatively, run directly:

streamlit run 01_comps/app.py --server.port 8503

---

## Project Structure

01_comps/
├── app.py
├── data/
│   └── raw/
│       └── peers.csv
└── README.md

---

## Disclaimer

This project is for **educational and demonstration purposes only**.
It does not constitute investment advice or a valuation opinion.