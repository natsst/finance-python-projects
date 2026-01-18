# 01_comps/app.py
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path


# ======================================================
# Page config
# ======================================================
st.set_page_config(
    page_title="Comparable Companies – Trading Multiples",
    layout="wide",
)

st.title("Comparable Companies (Trading Multiples) — Interactive App")


# ======================================================
# Paths + constants
# ======================================================
APP_DIR = Path(__file__).resolve().parent
DEFAULT_RAW = APP_DIR / "data" / "raw" / "peers.csv"

# Canonical columns expected by the app (after normalization)
REQUIRED_COLS = ["company", "market_cap", "net_debt", "revenue", "ebitda", "net_income"]

# Column aliases accepted (robust to different naming conventions)
COLUMN_ALIASES = {
    "market_cap": ["market_cap", "market_cap_m", "mkt_cap", "marketcap", "market_capitalization"],
    "net_debt": ["net_debt", "net_debt_m", "netdebt"],
    "revenue": ["revenue", "revenue_ltm", "revenue_ltm_m", "sales", "sales_ltm", "sales_ltm_m"],
    "ebitda": ["ebitda", "ebitda_ltm", "ebitda_ltm_m"],
    "net_income": ["net_income", "net_income_ltm", "net_income_ltm_m", "net_profit", "profit"],
}


# ======================================================
# Helpers
# ======================================================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize / map columns to canonical names used by the app.
    Keeps extra columns (ticker, currency, etc.) untouched.
    """
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    rename_map: dict[str, str] = {}
    for canon, variants in COLUMN_ALIASES.items():
        for v in variants:
            if v in df.columns:
                rename_map[v] = canon
                break

    df = df.rename(columns=rename_map)
    return df


def to_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def safe_div(n: pd.Series, d: pd.Series) -> pd.Series:
    d = d.replace(0, np.nan)
    x = n / d
    return x.replace([np.inf, -np.inf], np.nan)


def winsorize_series(s: pd.Series, p_low: float, p_high: float) -> pd.Series:
    lo = s.quantile(p_low)
    hi = s.quantile(p_high)
    return s.clip(lower=lo, upper=hi)


def stats(s: pd.Series) -> dict[str, float]:
    s = s.dropna()
    if s.empty:
        return {"n": 0}
    return {
        "n": int(s.shape[0]),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "p25": float(s.quantile(0.25)),
        "p75": float(s.quantile(0.75)),
    }


def implied_equity(
    multiple_name: str,
    multiple_value: float,
    target_row: pd.Series,
) -> float:
    """
    Equity implied from a given multiple (uses canonical columns).
    - EV/Revenue and EV/EBITDA -> EV then minus net debt
    - P/E -> Equity directly
    """
    if multiple_name == "EV / Revenue":
        ev = multiple_value * float(target_row["revenue"])
        return ev - float(target_row["net_debt"])
    if multiple_name == "EV / EBITDA":
        ev = multiple_value * float(target_row["ebitda"])
        return ev - float(target_row["net_debt"])
    if multiple_name == "P / E":
        return multiple_value * float(target_row["net_income"])
    raise ValueError("Unsupported multiple")


# ======================================================
# Sidebar controls
# ======================================================
with st.sidebar:
    st.header("Data Source")

    uploaded = st.file_uploader("Upload peers CSV (optional)", type="csv")
    st.caption("If you don’t upload, the app uses 01_comps/data/raw/peers.csv.")

    st.divider()
    st.header("Peer Set")

    target_name = st.text_input("Target company name (to exclude)", value="TargetCo")

    st.divider()
    st.header("Outliers / Winsorization")

    winsorize = st.checkbox("Winsorize multiples", value=True)
    p_low = st.number_input("Winsor lower percentile", min_value=0.00, max_value=0.20, value=0.05, step=0.01)
    p_high = st.number_input("Winsor upper percentile", min_value=0.80, max_value=1.00, value=0.95, step=0.01)


# ======================================================
# Load data
# ======================================================
if uploaded is not None:
    df_raw = pd.read_csv(uploaded)
else:
    if not DEFAULT_RAW.exists():
        st.error(f"Default dataset not found: {DEFAULT_RAW}")
        st.stop()
    df_raw = pd.read_csv(DEFAULT_RAW)

df_raw = normalize_columns(df_raw)

# Validate
missing = [c for c in REQUIRED_COLS if c not in df_raw.columns]
if missing:
    st.error(
        "Missing required columns after normalization.\n\n"
        f"Missing: {missing}\n\n"
        f"Found: {df_raw.columns.tolist()}\n\n"
        "Fix: rename your CSV columns or extend COLUMN_ALIASES in app.py."
    )
    st.stop()

# Coerce numeric
df_raw = to_numeric(df_raw, [c for c in REQUIRED_COLS if c != "company"])

# ======================================================
# Compute multiples
# ======================================================
df = df_raw.copy()

df["EV"] = df["market_cap"] + df["net_debt"]
df["EV / Revenue"] = safe_div(df["EV"], df["revenue"])
df["EV / EBITDA"] = safe_div(df["EV"], df["ebitda"])
df["P / E"] = safe_div(df["market_cap"], df["net_income"])

# Exclude target from peer set
peers = df[df["company"] != target_name].copy()

# Winsorize
if winsorize:
    for col in ["EV / Revenue", "EV / EBITDA", "P / E"]:
        peers[col] = winsorize_series(peers[col], p_low, p_high)

# ======================================================
# Layout
# ======================================================
col_left, col_right = st.columns([1.6, 1.0])

with col_left:
    st.subheader("Peer Set — Trading Multiples")

    display_cols = ["company", "EV / Revenue", "EV / EBITDA", "P / E"]
    if "ticker" in df_raw.columns:
        display_cols.insert(1, "ticker")
    if "currency" in df_raw.columns:
        display_cols.insert(2 if "ticker" in display_cols else 1, "currency")

    st.dataframe(peers[display_cols].round(2), use_container_width=True)

    st.subheader("Downloads")
    st.download_button(
        label="Download peer multiples (CSV)",
        data=peers.to_csv(index=False).encode("utf-8"),
        file_name="comps_multiples.csv",
        mime="text/csv",
    )

    summary_txt = (
        "Comparable Companies — Trading Multiples Summary\n"
        "==============================================\n\n"
        f"Peers (ex target): {int(peers.shape[0])}\n\n"
        f"EV/Revenue median: {stats(peers['EV / Revenue'])['median']:.2f}x\n"
        f"EV/EBITDA  median: {stats(peers['EV / EBITDA'])['median']:.2f}x\n"
        f"P/E        median: {stats(peers['P / E'])['median']:.2f}x\n"
    )
    st.download_button(
        label="Download summary (TXT)",
        data=summary_txt,
        file_name="comps_summary.txt",
        mime="text/plain",
    )

with col_right:
    st.subheader("Multiple Statistics (Peers)")

    stats_df = pd.DataFrame(
        {
            "EV / Revenue": stats(peers["EV / Revenue"]),
            "EV / EBITDA": stats(peers["EV / EBITDA"]),
            "P / E": stats(peers["P / E"]),
        }
    ).T

    stats_df = stats_df.rename(
        columns={"n": "n", "mean": "Mean", "median": "Median", "p25": "P25", "p75": "P75"}
    )[["n", "Mean", "Median", "P25", "P75"]]

    st.table(stats_df.round(2))

    # Target implied valuation
    st.subheader("Target — Implied Equity Value (Median)")
    target_df = df[df["company"] == target_name].copy()

    if target_df.empty:
        st.info("Target not found in dataset. Add it to the CSV or change the target name.")
    else:
        t = target_df.iloc[0]

        med_ev_rev = float(stats(peers["EV / Revenue"])["median"])
        med_ev_ebitda = float(stats(peers["EV / EBITDA"])["median"])
        med_pe = float(stats(peers["P / E"])["median"])

        implied_df = pd.DataFrame(
            {
                "Method": ["EV / Revenue", "EV / EBITDA", "P / E"],
                "Multiple (Median)": [med_ev_rev, med_ev_ebitda, med_pe],
                "Implied Equity (m€)": [
                    implied_equity("EV / Revenue", med_ev_rev, t),
                    implied_equity("EV / EBITDA", med_ev_ebitda, t),
                    implied_equity("P / E", med_pe, t),
                ],
            }
        )

        st.table(implied_df.round({"Multiple (Median)": 2, "Implied Equity (m€)": 0}))

        st.caption(
            "EV = Market Cap + Net Debt. EV multiples imply EV then bridge to Equity by subtracting Net Debt."
        )

st.caption("Local Streamlit app — educational / demo use.")