# 02_dcf/data/assumptions.py

# Horizon
N_YEARS = 5

# Revenues
REVENUE_0 = 5_000.0        # m€
REVENUE_GROWTH = 0.04      # 4% p.a.

# Profitability
EBIT_MARGIN = 0.20         # 20% EBIT margin
TAX_RATE = 0.28            # 28%

# Non-cash & investments
DA_PCT_REVENUE = 0.03      # D&A = 3% of revenue
CAPEX_PCT_REVENUE = 0.04   # CAPEX = 4% of revenue

# Working capital
NWC_PCT_REVENUE = 0.10     # Net Working Capital = 10% of revenue

# =========================
# WACC assumptions
# =========================

RISK_FREE_RATE = 0.025
EQUITY_RISK_PREMIUM = 0.055
BETA = 1.10

COST_OF_DEBT = 0.04

WEIGHT_EQUITY = 0.70
WEIGHT_DEBT = 0.30

# =========================
# Terminal value
# =========================

TERMINAL_GROWTH = 0.025   # 2.5%
NET_DEBT = 600.0         # m€