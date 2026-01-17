Discounted Cash Flow (DCF) Valuation App
=======================================

This project implements a full Discounted Cash Flow (DCF) valuation model in Python,
exposed through an interactive web application built with Streamlit.

The objective is to reproduce a professional corporate finance DCF workflow,
with explicit assumptions, transparent cash flow build-up, and decision-oriented outputs.

Key Features
------------

- explicit 5–10 year Free Cash Flow (FCF) forecast,
- operating build-up:
  - revenue growth,
  - EBIT margin,
  - taxes,
  - D&A, CAPEX, and working capital,
- WACC computation (CAPM-based),
- terminal value using Gordon Growth,
- enterprise value to equity bridge,
- sensitivity analysis (WACC × terminal growth),
- exportable outputs (TXT / Excel),
- interactive web interface.

Project Structure
-----------------

data/
- assumptions.py : centralised financial assumptions

src/
- fcf_build.py   : FCF forecast logic
- wacc.py        : WACC computation
- dcf_valuation.py : standalone DCF valuation engine

app.py
- Streamlit web application

reports/
- exported valuation summaries

How to Run
----------

1. Activate the virtual environment:
   
   source .venv/bin/activate

2. Launch the application:

   streamlit run app.py

3. Open the browser at:

   http://localhost:8501

Usage
-----

Users can:
- adjust operating and valuation assumptions,
- instantly recompute valuation outputs,
- visualize cash flows and valuation bridges,
- download valuation reports and Excel models.

Methodology Notes
-----------------

- Free Cash Flows are discounted at WACC.
- Terminal value is computed using the Gordon Growth formula.
- A large portion of value is driven by terminal assumptions, as in real-world DCFs.
- The model is designed for clarity, auditability, and extensibility.

Disclaimer
----------

This project is for educational and demonstration purposes only.
It does not constitute investment advice.
