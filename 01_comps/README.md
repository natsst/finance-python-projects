Comparable Companies Analysis (Python)
======================================

This project implements a Comparable Companies (Trading Multiples) valuation model in Python,
designed to replicate a standard sell-side / buy-side valuation workflow.

The objective is to compute peer trading multiples, derive implied valuation metrics,
and assess the relative positioning of a target company.

Scope
-----

The model performs:
- peer set analysis (exclusion of target company),
- computation of trading multiples:
  - EV / Revenue
  - EV / EBITDA
  - P/E
- summary statistics (mean, median),
- implied valuation of a target company using peer multiples,
- valuation range using percentile analysis (P25 / P50 / P75).

Project Structure
-----------------

data/
- raw/        : raw peer financials (CSV input)
- processed/  : computed multiples and outputs

src/
- compute_multiples.py : core valuation logic

reports/
- exported valuation summaries (CSV)

How to Run
----------

From the repository root:

python 01_comps/src/compute_multiples.py

The script will:
- load peer financial data,
- compute trading multiples,
- print a valuation summary in the terminal,
- export processed results to data/processed/.

Methodology Notes
-----------------

- Enterprise Value is derived from market capitalization and net debt.
- Outliers can be handled via winsorization.
- Implied equity value is computed from selected peer multiples.

Disclaimer
----------

This project is for educational and demonstration purposes only.
It does not constitute investment advice.
