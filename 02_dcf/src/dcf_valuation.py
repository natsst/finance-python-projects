# 02_dcf/src/dcf_valuation.py
from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

# ======================================================
# Path setup (make src/ and data/ importable)
# ======================================================
SRC_DIR = Path(__file__).resolve().parent      # .../02_dcf/src
ROOT = SRC_DIR.parent                          # .../02_dcf
sys.path.append(str(SRC_DIR))                  # allows import fcf_model, wacc
sys.path.append(str(ROOT))                     # allows import data.assumptions

from fcf_build import build_fcf_table
from wacc import compute_wacc
from data.assumptions import TERMINAL_GROWTH, NET_DEBT


# ======================================================
# Core DCF helpers
# ======================================================
def discount(values: list[float], rate: float) -> list[float]:
    """Discount cash flows occurring at t=1..N."""
    return [v / (1 + rate) ** t for t, v in enumerate(values, start=1)]


def terminal_value(fcf_last: float, wacc: float, g: float) -> float:
    """Gordon Growth terminal value at end of explicit forecast."""
    if wacc <= g:
        raise ValueError("WACC must be strictly greater than terminal growth rate.")
    return fcf_last * (1 + g) / (wacc - g)


# ======================================================
# Report writer
# ======================================================
def write_dcf_report(valuation_df: pd.DataFrame, wacc: float) -> None:
    report_path = ROOT / "reports" / "dcf_summary.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("DISCOUNTED CASH FLOW – SUMMARY\n")
        f.write("=" * 40 + "\n\n")

        f.write("1. Valuation Overview\n")
        for _, row in valuation_df.iterrows():
            f.write(f"{row['Metric']}: {row['Value (m€)']:,.0f} m€\n")

        f.write("\n2. Key Assumptions\n")
        f.write(f"WACC: {wacc:.2%}\n")
        f.write(f"Terminal growth: {TERMINAL_GROWTH:.2%}\n")
        f.write(f"Net debt: {NET_DEBT:,.0f} m€\n")

        f.write("\n3. Conclusion\n")
        f.write(
            "The DCF valuation implies a robust enterprise and equity value. "
            "As expected for a 5-year explicit forecast, a significant portion "
            "of value is driven by terminal assumptions.\n"
        )

    print(f"\nDCF report written to: {report_path}")


# ======================================================
# Main
# ======================================================
def main() -> pd.DataFrame:
    # Build explicit FCFs
    fcf_df = build_fcf_table()
    fcfs = fcf_df["FCF"].astype(float).tolist()

    # Discount rate
    wacc = float(compute_wacc())

    # PV of explicit FCFs
    discounted_fcfs = discount(fcfs, wacc)
    pv_explicit = float(sum(discounted_fcfs))

    # Terminal value
    tv = float(terminal_value(fcfs[-1], wacc, float(TERMINAL_GROWTH)))
    pv_tv = float(tv / (1 + wacc) ** len(fcfs))

    # EV -> Equity bridge
    enterprise_value = pv_explicit + pv_tv
    equity_value = enterprise_value - float(NET_DEBT)

    valuation = pd.DataFrame(
        {
            "Metric": [
                "PV of explicit FCFs",
                "PV of terminal value",
                "Enterprise Value",
                "Net Debt",
                "Equity Value",
            ],
            "Value (m€)": [
                pv_explicit,
                pv_tv,
                enterprise_value,
                float(NET_DEBT),
                equity_value,
            ],
        }
    )

    print("\n=== DCF Valuation ===")
    print(valuation.round(1).to_string(index=False))
    print(f"\nWACC used: {wacc:.2%}")
    print(f"Terminal growth: {TERMINAL_GROWTH:.2%}")

    # Write report
    write_dcf_report(valuation, wacc)

    return valuation


if __name__ == "__main__":
    main()