# Discounted Cash Flow (DCF) — Interactive Valuation Model

This project is a **fully interactive Discounted Cash Flow (DCF) valuation model**
built in Python using **Streamlit**, designed to replicate a **professional
corporate finance valuation workflow**.

It allows users to dynamically modify assumptions, visualize cash flow forecasts,
run sensitivity analyses, and export results in **Excel-ready format**.

---

## Objective

The objective of this project is to:
- Build a clean and transparent DCF model
- Separate operating assumptions from valuation mechanics
- Allow real-time interaction with key value drivers
- Replicate standards used in **M&A, Private Equity, and Equity Research**

The model follows a **Gordon Growth terminal value approach** and computes both
Enterprise Value and Equity Value.

---

## Core Features

### Operating Forecast
- Multi-year revenue forecast
- EBIT margin-based operating model
- Automatic computation of:
  - NOPAT
  - Depreciation & Amortization
  - CAPEX
  - Net Working Capital variation
- Free Cash Flow (FCF) build-up displayed year by year

---

### Discount Rate (WACC)
- Option to use a model-based WACC computed in `src/wacc.py`
- Manual WACC override available in the interface
- WACC is consistently applied across explicit period and terminal value

---

### Terminal Value
- Terminal Value computed using **Gordon Growth**
- Built-in guardrails preventing invalid configurations (WACC ≤ g)

---

### Valuation Output
The app computes and displays:
- Present Value of explicit FCFs
- Present Value of Terminal Value
- Enterprise Value
- Net Debt
- Equity Value

A **waterfall chart** illustrates the bridge from Enterprise Value to Equity Value.

---

### Sensitivity Analysis
- Interactive **WACC × Terminal Growth (g)** sensitivity table
- Displays Equity Value outcomes
- Invalid combinations (WACC ≤ g) are automatically excluded

---

### Charts & Visualization
- Free Cash Flow forecast chart
- Revenue forecast chart
- EV → Equity waterfall chart

All charts update dynamically based on user inputs.

---

### Exports
The app allows downloading:
- A textual DCF summary report (`.txt`)
- A structured Excel DCF model (`.xlsx`) including:
  - FCF forecast
  - Valuation summary
  - Sensitivity analysis (if activated)

---

## Assumptions Handling

Default assumptions are stored in:

02_dcf/src/data/assumptions.py

This allows:
- Clean separation between logic and assumptions
- Easy modification without touching the app logic
- Reproducibility of valuation scenarios

---

## How to Run the App

From the repository root:

./run_finance_apps.command

Then select:

2) Discounted Cash Flow (DCF)

The app will automatically open in your browser.

Alternatively, run directly:

streamlit run 02_dcf/app.py --server.port 8502

---

## Project Structure

02_dcf/
├── app.py
├── src/
│   ├── wacc.py
│   └── data/
│       └── assumptions.py
└── README.md

---

## Methodology Notes

- All monetary values are expressed in **EUR millions**
- Terminal Value is discounted back to present value using WACC
- The model is deterministic and assumption-driven
- Designed for clarity, auditability, and interview readiness

---

## Disclaimer

This project is for **educational and demonstration purposes only**.
It does not constitute investment advice, valuation advice, or a fairness opinion.