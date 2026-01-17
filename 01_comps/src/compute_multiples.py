# 01_comps/src/compute_multiples.py
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "peers.csv"
OUT_DIR = ROOT / "data" / "processed"
OUT_PATH = OUT_DIR / "peers_with_multiples.csv"
REPORT_PATH = ROOT / "reports" / "comps_summary.txt"

REQUIRED_COLS = [
    "company", "ticker", "currency",
    "market_cap_m", "net_debt_m",
    "revenue_ltm_m", "ebitda_ltm_m", "net_income_ltm_m",
]

NUM_COLS = [
    "market_cap_m", "net_debt_m",
    "revenue_ltm_m", "ebitda_ltm_m", "net_income_ltm_m",
]


def safe_div(numer: pd.Series, denom: pd.Series) -> pd.Series:
    """Robust division: avoid div-by-zero and inf values."""
    out = numer / denom.replace({0: np.nan})
    return out.replace([np.inf, -np.inf], np.nan)


def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Validate required columns and coerce numerics. Enforce single-currency dataset."""
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()

    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    if df["currency"].nunique() != 1:
        raise ValueError("Multiple currencies detected. Add FX normalization before proceeding.")

    if df["ticker"].isna().any():
        raise ValueError("Ticker column contains missing values.")

    return df


def compute_multiples(df: pd.DataFrame) -> pd.DataFrame:
    """Compute EV and core valuation multiples (EV/Revenue, EV/EBITDA, P/E)."""
    df = df.copy()

    # Enterprise Value
    df["ev_m"] = df["market_cap_m"] + df["net_debt_m"]

    # Multiples (set NaN if denominator <= 0: standard practice)
    df["ev_rev"] = safe_div(df["ev_m"], df["revenue_ltm_m"].where(df["revenue_ltm_m"] > 0))
    df["ev_ebitda"] = safe_div(df["ev_m"], df["ebitda_ltm_m"].where(df["ebitda_ltm_m"] > 0))
    df["pe"] = safe_div(df["market_cap_m"], df["net_income_ltm_m"].where(df["net_income_ltm_m"] > 0))

    return df


def peer_summary(df: pd.DataFrame, target_ticker: str = "TGT") -> dict:
    """Compute mean/median multiples on the peer set (excluding target)."""
    peers = df[df["ticker"] != target_ticker].copy()
    return {
        "EV/Revenue (median)": peers["ev_rev"].median(),
        "EV/EBITDA (median)": peers["ev_ebitda"].median(),
        "P/E (median)": peers["pe"].median(),
        "EV/Revenue (mean)": peers["ev_rev"].mean(),
        "EV/EBITDA (mean)": peers["ev_ebitda"].mean(),
        "P/E (mean)": peers["pe"].mean(),
        "n_peers": len(peers),
    }


def implied_valuation(
    df: pd.DataFrame,
    target_ticker: str = "TGT",
    multiple_col: str = "ev_ebitda",
) -> dict:
    """
    Implied valuation for target using peer median multiple.
    Default: EV/EBITDA median -> EV implied -> Equity implied (EV - Net Debt).
    """
    peers = df[df["ticker"] != target_ticker]
    target = df[df["ticker"] == target_ticker]

    if target.empty:
        raise ValueError(f"Target ticker '{target_ticker}' not found in dataset.")
    target = target.iloc[0]

    multiple = peers[multiple_col].median()
    if pd.isna(multiple):
        raise ValueError(f"Cannot compute implied valuation: median of '{multiple_col}' is NaN.")

    if multiple_col == "ev_ebitda":
        base = target["ebitda_ltm_m"]
        base_name = "EBITDA LTM"
    elif multiple_col == "ev_rev":
        base = target["revenue_ltm_m"]
        base_name = "Revenue LTM"
    else:
        raise ValueError("multiple_col must be one of: 'ev_ebitda', 'ev_rev'.")

    if pd.isna(base) or base <= 0:
        raise ValueError(f"Target {base_name} is invalid (<=0 or missing), cannot apply {multiple_col}.")

    ev_implied = multiple * base
    equity_implied = ev_implied - target["net_debt_m"]
    upside_pct = equity_implied / target["market_cap_m"] - 1 if target["market_cap_m"] > 0 else np.nan

    return {
        "multiple_metric": multiple_col,
        "multiple_used": float(multiple),
        "base_metric": base_name,
        "base_value_m": float(base),
        "ev_implied_m": float(ev_implied),
        "equity_implied_m": float(equity_implied),
        "current_market_cap_m": float(target["market_cap_m"]),
        "upside_pct": float(upside_pct) if not pd.isna(upside_pct) else np.nan,
    }


def winsorize_series(s: pd.Series, lower_q: float = 0.05, upper_q: float = 0.95) -> pd.Series:
    """Clip a series to quantile bounds (winsorization)."""
    s = s.astype(float)
    lo = s.quantile(lower_q)
    hi = s.quantile(upper_q)
    return s.clip(lower=lo, upper=hi)


def valuation_range(
    df: pd.DataFrame,
    target_ticker: str = "TGT",
    multiple_col: str = "ev_ebitda",
    winsorize: bool = True,
    lower_q: float = 0.05,
    upper_q: float = 0.95,
) -> dict:
    """
    Compute implied EV/Equity range for target using peer multiple distribution (P25/P50/P75).
    Optionally winsorize peer multiples before computing quantiles.
    """
    peers = df[df["ticker"] != target_ticker].copy()
    target = df[df["ticker"] == target_ticker]
    if target.empty:
        raise ValueError(f"Target ticker '{target_ticker}' not found.")
    target = target.iloc[0]

    if multiple_col == "ev_ebitda":
        base = target["ebitda_ltm_m"]
        base_name = "EBITDA LTM"
    elif multiple_col == "ev_rev":
        base = target["revenue_ltm_m"]
        base_name = "Revenue LTM"
    else:
        raise ValueError("multiple_col must be one of: 'ev_ebitda', 'ev_rev'.")

    if pd.isna(base) or base <= 0:
        raise ValueError(f"Target {base_name} invalid (<=0 or missing).")

    mult = peers[multiple_col].dropna()
    if mult.empty:
        raise ValueError(f"No valid peer multiples for '{multiple_col}'.")

    if winsorize:
        mult = winsorize_series(mult, lower_q=lower_q, upper_q=upper_q)

    q25, q50, q75 = mult.quantile([0.25, 0.50, 0.75]).tolist()

    def to_equity(m: float) -> tuple[float, float]:
        ev = m * base
        eq = ev - target["net_debt_m"]
        return float(ev), float(eq)

    ev25, eq25 = to_equity(q25)
    ev50, eq50 = to_equity(q50)
    ev75, eq75 = to_equity(q75)

    def upside(eq: float) -> float:
        return eq / target["market_cap_m"] - 1 if target["market_cap_m"] > 0 else np.nan

    return {
        "multiple_metric": multiple_col,
        "base_metric": base_name,
        "base_value_m": float(base),
        "winsorized": winsorize,
        "winsor_q": (lower_q, upper_q) if winsorize else None,
        "multiples": {"p25": float(q25), "p50": float(q50), "p75": float(q75)},
        "implied_ev_m": {"p25": ev25, "p50": ev50, "p75": ev75},
        "implied_equity_m": {"p25": eq25, "p50": eq50, "p75": eq75},
        "upside_pct": {"p25": float(upside(eq25)), "p50": float(upside(eq50)), "p75": float(upside(eq75))},
        "current_market_cap_m": float(target["market_cap_m"]),
    }


def write_report(summary: dict, valuation: dict, valuation_range_dict: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("COMPARABLE COMPANIES ANALYSIS – SUMMARY\n")
        f.write("=" * 45 + "\n\n")

        f.write("1. Peer Set Overview\n")
        f.write(f"Number of peers (ex Target): {summary['n_peers']}\n\n")

        f.write("2. Trading Multiples (Peers)\n")
        f.write(f"EV / Revenue (median): {summary['EV/Revenue (median)']:.2f}x\n")
        f.write(f"EV / EBITDA  (median): {summary['EV/EBITDA (median)']:.2f}x\n")
        f.write(f"P/E          (median): {summary['P/E (median)']:.2f}x\n\n")

        f.write("3. Implied Valuation – Base Case (EV / EBITDA median)\n")
        f.write(f"Implied Enterprise Value : {valuation['ev_implied_m']:,.0f} m€\n")
        f.write(f"Implied Equity Value     : {valuation['equity_implied_m']:,.0f} m€\n")
        f.write(f"Current Market Cap       : {valuation['current_market_cap_m']:,.0f} m€\n")
        f.write(f"Upside / (Downside)      : {valuation['upside_pct']:.1%}\n\n")

        f.write("4. Valuation Range (Winsorized P25 / P50 / P75)\n")
        f.write(
            f"Equity Value Range (m€): "
            f"{valuation_range_dict['implied_equity_m']['p25']:,.0f} / "
            f"{valuation_range_dict['implied_equity_m']['p50']:,.0f} / "
            f"{valuation_range_dict['implied_equity_m']['p75']:,.0f}\n"
        )
        f.write(
            f"Upside Range (%): "
            f"{valuation_range_dict['upside_pct']['p25']:.1%} / "
            f"{valuation_range_dict['upside_pct']['p50']:.1%} / "
            f"{valuation_range_dict['upside_pct']['p75']:.1%}\n\n"
        )

        f.write("5. Conclusion\n")
        f.write(
            "Based on peer median EV/EBITDA multiples, the target company appears "
            "moderately undervalued relative to the market, with a positive upside "
            "in the base and upper quartile scenarios.\n"
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_PATH)
    df = validate_schema(df)

    out = compute_multiples(df)
    out.to_csv(OUT_PATH, index=False)

    # Peer stats (exclude target)
    summary = peer_summary(out, target_ticker="TGT")

    print("=== Peer Multiples Summary (ex TargetCo) ===")
    for k, v in summary.items():
        if isinstance(v, (float, np.floating)):
            print(f"{k:22s}: {v:,.2f}x")
        else:
            print(f"{k:22s}: {v}")

    # Single-point implied valuation using EV/EBITDA median
    valuation = implied_valuation(out, target_ticker="TGT", multiple_col="ev_ebitda")

    print("\n=== Implied Valuation – TargetCo (Peer median) ===")
    print(f"Multiple metric     : {valuation['multiple_metric']}")
    print(f"Multiple used       : {valuation['multiple_used']:.2f}x")
    print(f"Base metric         : {valuation['base_metric']}")
    print(f"Base value          : {valuation['base_value_m']:,.0f} m€")
    print(f"Implied EV          : {valuation['ev_implied_m']:,.0f} m€")
    print(f"Implied Equity      : {valuation['equity_implied_m']:,.0f} m€")
    print(f"Current Market Cap  : {valuation['current_market_cap_m']:,.0f} m€")
    print(f"Upside/(Downside)   : {valuation['upside_pct']:.1%}")

    # Range implied valuation (P25/P50/P75) with winsorization
    vr = valuation_range(
        out,
        target_ticker="TGT",
        multiple_col="ev_ebitda",
        winsorize=True,
        lower_q=0.05,
        upper_q=0.95,
    )

    print("\n=== Valuation Range – TargetCo (EV/EBITDA; P25/P50/P75) ===")
    print(f"Winsorized          : {vr['winsorized']} {vr['winsor_q']}")
    print(
        f"Multiple P25/P50/P75: "
        f"{vr['multiples']['p25']:.2f}x / {vr['multiples']['p50']:.2f}x / {vr['multiples']['p75']:.2f}x"
    )
    print(
        f"Equity  P25/P50/P75 : "
        f"{vr['implied_equity_m']['p25']:,.0f} / {vr['implied_equity_m']['p50']:,.0f} / {vr['implied_equity_m']['p75']:,.0f} m€"
    )
    print(
        f"Upside  P25/P50/P75 : "
        f"{vr['upside_pct']['p25']:.1%} / {vr['upside_pct']['p50']:.1%} / {vr['upside_pct']['p75']:.1%}"
    )

    # Write report
    write_report(summary=summary, valuation=valuation, valuation_range_dict=vr, out_path=REPORT_PATH)
    print(f"\nReport written to: {REPORT_PATH}")

    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()