# Comparable Companies Analysis (Trading Comps)

This project implements a Comparable Companies Analysis in Python, following a standard investment banking and M&A valuation methodology.

The objective is to estimate the implied valuation of a target company based on peer trading multiples, while applying disciplined data processing and robust statistical practices.

## Objective

- Derive a market-based valuation reference for a target company
- Replicate a professional trading comparables workflow
- Produce clean, reproducible valuation outputs

## Scope of the Analysis

- Construction of a peer group
- Computation of trading multiples:
  - EV / Revenue
  - EV / EBITDA
  - P/E
- Exclusion of the target company from peer statistics
- Outlier handling through winsorization
- Summary statistics (mean, median)
- Valuation range using quartiles (P25 / P50 / P75)
- Implied Enterprise Value and Equity Value for the target company
- Upside / downside versus current market capitalization
- Automated valuation report

## Outputs

- data/processed/peers_with_multiples.csv
- reports/comps_summary.txt

## How to Run

From the root of the repository:

python 01_comps/src/compute_multiples.py

## Notes

This project is intended for educational and demonstration purposes and illustrates a professional approach to trading multiples analysis commonly used in corporate finance and M&A.
