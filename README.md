# Finance Python Projects

This repository contains a collection of finance-oriented projects implemented in Python,
with a focus on corporate finance, valuation, and buy-side / M&A use cases.

The objective is to translate standard financial modeling techniques (typically built in Excel)
into clean, reproducible, and auditable Python code.

---

## Projects

### 01 — Comparable Companies Analysis
A full Comparable Companies (Comps) valuation engine.

**Key features:**
- Enterprise Value computation
- Trading multiples (EV/Revenue, EV/EBITDA, P/E)
- Peer set statistics (mean, median)
- Outlier handling via winsorisation
- Implied valuation for a target company
- Valuation range (P25 / P50 / P75)
- Automated valuation report generation

**Structure:**
- `data/raw/`        : raw peer financials (excluded from version control)
- `data/processed/`  : processed outputs with computed multiples
- `src/`             : core valuation logic
- `reports/`         : generated valuation summary

Run the project:
```bash
python src/compute_multiples.py
