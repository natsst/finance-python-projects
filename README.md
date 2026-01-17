# Finance Valuation Projects in Python

This repository contains a set of corporate finance valuation projects implemented in Python, reflecting methodologies used in investment banking, M&A, and corporate finance.

The objective of this repository is to demonstrate:
- A strong understanding of valuation theory
- The ability to translate financial reasoning into structured Python code
- A professional, reproducible approach to financial analysis and reporting

Each project is self-contained, documented, and produces automated outputs.

## Projects Overview

### 01 — Comparable Companies Analysis (Trading Comps)

A market-based valuation using peer trading multiples.

Key features:
- Peer set construction
- Computation of EV/Revenue, EV/EBITDA, and P/E multiples
- Exclusion of the target company from peer statistics
- Outlier handling through winsorization
- Summary statistics (mean, median, quartiles)
- Implied equity valuation and upside/downside analysis
- Automated output files

Directory:
01_comps/

### 02 — Discounted Cash Flow Valuation (DCF)

An intrinsic valuation based on projected free cash flows.

Key features:
- Bottom-up construction of Free Cash Flows from operating drivers
- Explicit assumptions on revenue growth, margins, taxes, CAPEX, and working capital
- WACC computation using CAPM and after-tax cost of debt
- Terminal value estimation using the Gordon Growth method
- Enterprise Value to Equity Value bridge
- Automated DCF valuation report

Directory:
02_dcf/

## Methodological Notes

Comparable Companies Analysis provides a market-based valuation anchor, while Discounted Cash Flow analysis provides an intrinsic, fundamentals-driven valuation. Differences between the two approaches are expected and are an integral part of valuation interpretation.

In practice, trading comparables are typically used to anchor transaction pricing, while DCFs are used as a sanity check and to assess long-term upside potential.

## Technical Stack

Python 3  
pandas, numpy  
Modular project structure  
Reproducible scripts  
Automated text-based reporting  

## How to Run the Projects

From the root of the repository:

python 01_comps/src/compute_multiples.py  
python 02_dcf/src/dcf_valuation.py  

## Disclaimer

These projects are for educational and demonstration purposes only and do not constitute investment advice.
