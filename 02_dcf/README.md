# Discounted Cash Flow Valuation (DCF)

This project implements a Discounted Cash Flow (DCF) valuation model in Python, following a methodology consistent with investment banking, M&A, and corporate finance practices.

The objective is to estimate the intrinsic value of a company based on projected free cash flows, independent of current market multiples.

## Objective

- Build an intrinsic valuation based on operating fundamentals
- Replicate a bank-ready DCF methodology in Python
- Clearly separate assumptions, cash flow construction, discounting, and valuation
- Produce reproducible and automated valuation outputs

## Scope of the Analysis

The analysis includes the following components:

- Bottom-up construction of Free Cash Flows (FCF)
- Explicit projection of revenues, margins, taxes, CAPEX, and working capital
- WACC computation using:
  - CAPM for cost of equity
  - After-tax cost of debt
  - Target capital structure
- Terminal value estimation using the Gordon Growth method
- Discounting of explicit cash flows and terminal value
- Enterprise Value to Equity Value bridge
- Automated generation of a DCF summary report

## Methodology

### Free Cash Flow Construction

Free Cash Flows are built using the standard operating approach:

FCF = EBIT × (1 − Tax) + D&A − CAPEX − ΔNWC

All drivers are explicitly modeled and parameterized through assumptions.

### Discount Rate (WACC)

The discount rate is derived from a standard WACC framework:

- Cost of equity calculated using CAPM
- Cost of debt adjusted for taxes
- Weighted average based on target capital structure

### Terminal Value

The terminal value is calculated using the Gordon Growth formula:

TV = FCFₙ × (1 + g) / (WACC − g)

The terminal value is discounted back to present value and represents the continuation value beyond the explicit forecast period.

### Enterprise to Equity Bridge

Enterprise Value is converted to Equity Value by subtracting net debt, providing the implied equity valuation.

## Outputs

An automated valuation summary is generated at:

reports/dcf_summary.txt

## How to Run

From the root of the repository:

python 02_dcf/src/dcf_valuation.py

## Notes

This project is intended for educational and demonstration purposes and illustrates a structured and professional implementation of an intrinsic valuation model commonly used in investment banking and M&A.
