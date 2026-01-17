import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from data.assumptions import (
    N_YEARS,
    REVENUE_0,
    REVENUE_GROWTH,
    EBIT_MARGIN,
    TAX_RATE,
    DA_PCT_REVENUE,
    CAPEX_PCT_REVENUE,
    NWC_PCT_REVENUE,
)

from pathlib import Path
import pandas as pd

from data.assumptions import (
    N_YEARS,
    REVENUE_0,
    REVENUE_GROWTH,
    EBIT_MARGIN,
    TAX_RATE,
    DA_PCT_REVENUE,
    CAPEX_PCT_REVENUE,
    NWC_PCT_REVENUE,
)

ROOT = Path(__file__).resolve().parents[1]


def build_fcf_table():
    years = list(range(1, N_YEARS + 1))

    # Revenue projection
    revenue = [REVENUE_0 * (1 + REVENUE_GROWTH) ** t for t in years]

    # Operating metrics
    ebit = [r * EBIT_MARGIN for r in revenue]
    nopat = [e * (1 - TAX_RATE) for e in ebit]

    da = [r * DA_PCT_REVENUE for r in revenue]
    capex = [r * CAPEX_PCT_REVENUE for r in revenue]

    # Working capital
    nwc = [r * NWC_PCT_REVENUE for r in revenue]
    delta_nwc = [nwc[0] - REVENUE_0 * NWC_PCT_REVENUE] + [
        nwc[i] - nwc[i - 1] for i in range(1, N_YEARS)
    ]

    # Free Cash Flow
    fcf = [
        nopat[i] + da[i] - capex[i] - delta_nwc[i]
        for i in range(N_YEARS)
    ]

    df = pd.DataFrame(
        {
            "Year": years,
            "Revenue": revenue,
            "EBIT": ebit,
            "NOPAT": nopat,
            "D&A": da,
            "CAPEX": capex,
            "ΔNWC": delta_nwc,
            "FCF": fcf,
        }
    )

    return df


def main():
    df = build_fcf_table()

    print("\n=== FCF Projection (Build-up) ===")
    print(df.round(1).to_string(index=False))

    return df


if __name__ == "__main__":
    main()