import sys
from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# -------------------------
# Paths
# -------------------------
APP_DIR = Path(__file__).resolve().parent          # .../02_dcf
SRC_DIR = APP_DIR / "src"                          # .../02_dcf/src
sys.path.append(str(SRC_DIR))
sys.path.append(str(APP_DIR))

from data import assumptions as a
from src.wacc import compute_wacc


def build_fcf_table(
    n_years: int,
    revenue_0: float,
    revenue_growth: float,
    ebit_margin: float,
    tax_rate: float,
    da_pct_rev: float,
    capex_pct_rev: float,
    nwc_pct_rev: float,
) -> pd.DataFrame:
    years = list(range(1, n_years + 1))
    revenue = [revenue_0 * (1 + revenue_growth) ** t for t in years]

    ebit = [r * ebit_margin for r in revenue]
    nopat = [e * (1 - tax_rate) for e in ebit]
    da = [r * da_pct_rev for r in revenue]
    capex = [r * capex_pct_rev for r in revenue]

    nwc = [r * nwc_pct_rev for r in revenue]
    delta_nwc = [nwc[0] - revenue_0 * nwc_pct_rev] + [nwc[i] - nwc[i - 1] for i in range(1, n_years)]

    fcf = [nopat[i] + da[i] - capex[i] - delta_nwc[i] for i in range(n_years)]

    return pd.DataFrame(
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


def discount(values: list[float], rate: float) -> list[float]:
    return [v / (1 + rate) ** t for t, v in enumerate(values, start=1)]


def terminal_value(fcf_last: float, wacc: float, g: float) -> float:
    if wacc <= g:
        raise ValueError("WACC must be strictly greater than terminal growth rate.")
    return fcf_last * (1 + g) / (wacc - g)

def build_dcf_report_text(
    fcf_df: pd.DataFrame,
    wacc: float,
    terminal_g: float,
    net_debt: float,
    pv_fcfs: float,
    pv_tv: float,
    ev: float,
    eq: float,
) -> str:
    lines = []
    lines.append("DISCOUNTED CASH FLOW – SUMMARY")
    lines.append("=" * 40)
    lines.append("")
    lines.append("1. Key Assumptions")
    lines.append(f"Forecast years: {int(fcf_df.shape[0])}")
    lines.append(f"Revenue Year 1: {fcf_df.loc[0, 'Revenue']:,.0f} m€")
    lines.append(f"WACC: {wacc:.2%}")
    lines.append(f"Terminal growth: {terminal_g:.2%}")
    lines.append(f"Net debt: {net_debt:,.0f} m€")
    lines.append("")
    lines.append("2. Valuation Overview")
    lines.append(f"PV of explicit FCFs: {pv_fcfs:,.0f} m€")
    lines.append(f"PV of terminal value: {pv_tv:,.0f} m€")
    lines.append(f"Enterprise Value: {ev:,.0f} m€")
    lines.append(f"Equity Value: {eq:,.0f} m€")
    lines.append("")
    lines.append("3. FCF Snapshot (m€)")
    # Keep it short: year + FCF
    for _, r in fcf_df[["Year", "FCF"]].iterrows():
        lines.append(f"Year {int(r['Year'])}: {float(r['FCF']):,.0f}")
    lines.append("")
    lines.append("4. Notes")
    lines.append("Terminal value is computed using Gordon Growth and discounted at WACC.")
    lines.append("This output is for educational/demonstration purposes only.")
    return "\n".join(lines)

from io import BytesIO

def build_dcf_excel_bytes(
    fcf_df: pd.DataFrame,
    valuation_df: pd.DataFrame,
    sensi_df: pd.DataFrame | None = None,
) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        fcf_df.to_excel(writer, index=False, sheet_name="FCF")
        valuation_df.to_excel(writer, index=False, sheet_name="Valuation")

        if sensi_df is not None:
            sensi_df.to_excel(writer, sheet_name="Sensitivity")

        wb = writer.book

        def format_sheet(name):
            ws = wb[name]
            ws.freeze_panes = "A2"
            for col in ws.columns:
                max_len = max(len(str(c.value)) if c.value else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(10, max_len + 2), 30)

        format_sheet("FCF")
        format_sheet("Valuation")
        if sensi_df is not None:
            format_sheet("Sensitivity")

    output.seek(0)
    return output.getvalue()

st.set_page_config(page_title="DCF Model", layout="wide")
st.title("Discounted Cash Flow (DCF) — Interactive Model")

with st.sidebar:
    st.header("Operating Assumptions")

    n_years = st.number_input("Forecast years", min_value=3, max_value=10, value=int(getattr(a, "N_YEARS", 5)))

    revenue_0 = st.number_input("Revenue (Year 0), m€", min_value=0.0, value=float(getattr(a, "REVENUE_0", 5000.0)))
    revenue_growth = st.number_input("Revenue growth (p.a.)", min_value=-0.50, max_value=0.50, value=float(getattr(a, "REVENUE_GROWTH", 0.04)), format="%.4f")

    ebit_margin = st.number_input("EBIT margin", min_value=-0.50, max_value=0.80, value=float(getattr(a, "EBIT_MARGIN", 0.20)), format="%.4f")
    tax_rate = st.number_input("Tax rate", min_value=0.0, max_value=0.60, value=float(getattr(a, "TAX_RATE", 0.28)), format="%.4f")

    da_pct = st.number_input("D&A (% revenue)", min_value=0.0, max_value=0.30, value=float(getattr(a, "DA_PCT_REVENUE", 0.03)), format="%.4f")
    capex_pct = st.number_input("CAPEX (% revenue)", min_value=0.0, max_value=0.50, value=float(getattr(a, "CAPEX_PCT_REVENUE", 0.04)), format="%.4f")
    nwc_pct = st.number_input("NWC (% revenue)", min_value=0.0, max_value=0.50, value=float(getattr(a, "NWC_PCT_REVENUE", 0.10)), format="%.4f")

    st.divider()
    st.header("Valuation Assumptions")
    terminal_g = st.number_input("Terminal growth (g)", min_value=-0.05, max_value=0.10, value=float(getattr(a, "TERMINAL_GROWTH", 0.025)), format="%.4f")
    net_debt = st.number_input("Net debt, m€", min_value=-1e9, max_value=1e9, value=float(getattr(a, "NET_DEBT", 600.0)))

    st.divider()
    st.header("Discount Rate")
    use_model_wacc = st.checkbox("Use WACC from src/wacc.py", value=True)
    manual_wacc = st.number_input("Manual WACC (if unchecked)", min_value=0.0, max_value=0.30, value=0.08, format="%.4f")

# Compute
fcf_df = build_fcf_table(
    n_years=n_years,
    revenue_0=revenue_0,
    revenue_growth=revenue_growth,
    ebit_margin=ebit_margin,
    tax_rate=tax_rate,
    da_pct_rev=da_pct,
    capex_pct_rev=capex_pct,
    nwc_pct_rev=nwc_pct,
)

wacc = float(compute_wacc()) if use_model_wacc else float(manual_wacc)

col1, col2 = st.columns([1.5, 1.0])

with col1:
    st.subheader("FCF Forecast (Build-up)")
    st.dataframe(fcf_df.round(2), width="stretch")

    st.subheader("Charts")
    fig, ax = plt.subplots()
    ax.plot(fcf_df["Year"], fcf_df["FCF"], marker="o")
    ax.set_xlabel("Year")
    ax.set_ylabel("FCF (m€)")
    ax.set_title("Free Cash Flow Forecast")
    st.pyplot(fig)

    fig2, ax2 = plt.subplots()
    ax2.plot(fcf_df["Year"], fcf_df["Revenue"], marker="o")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Revenue (m€)")
    ax2.set_title("Revenue Forecast")
    st.pyplot(fig2)

with col2:
    st.subheader("DCF Output")
    try:
        fcfs = fcf_df["FCF"].astype(float).tolist()
        pv_fcfs = float(sum(discount(fcfs, wacc)))

        tv = float(terminal_value(fcfs[-1], wacc, terminal_g))
        pv_tv = float(tv / (1 + wacc) ** len(fcfs))

        ev = pv_fcfs + pv_tv
        eq = ev - float(net_debt)

        out = pd.DataFrame(
            {
                "Metric": ["PV explicit FCFs", "PV terminal value", "Enterprise Value", "Net Debt", "Equity Value"],
                "Value (m€)": [pv_fcfs, pv_tv, ev, float(net_debt), eq],
            }
        )

        st.table(out.round(2))
        st.write(f"WACC used: {wacc:.2%}")
        st.write(f"Terminal growth: {terminal_g:.2%}")

        st.subheader("Download")
        report_text = build_dcf_report_text(
            fcf_df=fcf_df,
            wacc=wacc,
            terminal_g=terminal_g,
            net_debt=float(net_debt),
            pv_fcfs=pv_fcfs,
            pv_tv=pv_tv,
            ev=ev,
            eq=eq,
        )

        st.download_button(
            label="Download DCF report (.txt)",
            data=report_text,
            file_name="dcf_summary.txt",
            mime="text/plain",
        )

                # Excel download (FCF + Valuation, Sensitivity optional)
        sensi = None
        sensi_for_export = None
        if "sensi" in locals():
            sensi_for_export = sensi.copy()

        excel_bytes = build_dcf_excel_bytes(
            fcf_df=fcf_df.round(2),
            valuation_df=out.round(2),
            sensi_df=None if sensi_for_export is None else sensi_for_export.round(0),
        )

        st.download_button(
            label="Download DCF model (Excel .xlsx)",
            data=excel_bytes,
            file_name="dcf_model.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.subheader("EV to Equity Waterfall")
        wf = pd.DataFrame(
            {
                "Step": ["Enterprise Value", "Net Debt", "Equity Value"],
                "Value": [ev, -float(net_debt), eq],
            }
        )

        fig3, ax3 = plt.subplots()
        ax3.bar(wf["Step"], wf["Value"])
        ax3.axhline(0, linewidth=1)
        ax3.set_ylabel("m€")
        ax3.set_title("Bridge: EV → Equity")
        st.pyplot(fig3)

        st.subheader("Sensitivity (Equity Value)")
        show_sensi = st.checkbox("Show WACC × g sensitivity table", value=True)

        if show_sensi:
            # Sensitivity grid (simple + credible)
            wacc_grid = np.array([wacc - 0.01, wacc - 0.005, wacc, wacc + 0.005, wacc + 0.01])
            g_grid = np.array([terminal_g - 0.005, terminal_g, terminal_g + 0.005])

            # Guardrails (avoid invalid WACC <= g)
            def equity_value_for(w, g):
                if w <= g:
                    return np.nan
                pv_fcfs_local = float(sum(discount(fcfs, w)))
                tv_local = float(terminal_value(fcfs[-1], w, g))
                pv_tv_local = float(tv_local / (1 + w) ** len(fcfs))
                ev_local = pv_fcfs_local + pv_tv_local
                return ev_local - float(net_debt)

            sensi = pd.DataFrame(
                index=[f"{gg:.2%}" for gg in g_grid],
                columns=[f"{ww:.2%}" for ww in wacc_grid],
                data=[[equity_value_for(ww, gg) for ww in wacc_grid] for gg in g_grid],
            )

            st.caption("Rows: terminal growth (g). Columns: WACC. Values: Equity Value (m€).")
            st.dataframe(sensi.round(0), width="stretch")

    except Exception as e:
        st.error(str(e))

st.caption("Local Streamlit app. Educational use only.")