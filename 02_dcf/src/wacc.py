import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from data.assumptions import (
    RISK_FREE_RATE,
    EQUITY_RISK_PREMIUM,
    BETA,
    COST_OF_DEBT,
    TAX_RATE,
    WEIGHT_EQUITY,
    WEIGHT_DEBT,
)


def cost_of_equity():
    return RISK_FREE_RATE + BETA * EQUITY_RISK_PREMIUM


def after_tax_cost_of_debt():
    return COST_OF_DEBT * (1 - TAX_RATE)


def compute_wacc():
    re = cost_of_equity()
    rd = after_tax_cost_of_debt()
    return WEIGHT_EQUITY * re + WEIGHT_DEBT * rd


if __name__ == "__main__":
    wacc = compute_wacc()
    print("=== WACC computation ===")
    print(f"Cost of equity : {cost_of_equity():.2%}")
    print(f"Cost of debt   : {after_tax_cost_of_debt():.2%}")
    print(f"WACC           : {wacc:.2%}")