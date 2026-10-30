"""Streamlit frontend for the PE market snapshot. Run: streamlit run app.py"""
import pandas as pd
import streamlit as st

from market_data import DEFAULT_COMPS, build_comps, build_macro

st.set_page_config(page_title="PE Market Data", layout="wide")
st.title("PE Market Data")


@st.cache_data(ttl=900, show_spinner="Fetching market data...")
def load(tickers: tuple[str, ...]) -> tuple[pd.DataFrame, pd.DataFrame]:
    return build_comps(list(tickers)), build_macro()


def color_returns(v):
    if pd.isna(v):
        return ""
    return "color: #1a7f37" if v > 0 else "color: #cf222e" if v < 0 else ""


def show(df: pd.DataFrame):
    ret_cols = [c for c in df.columns if c.endswith("%") and c != "Div Yield %"]
    styled = df.style.map(color_returns, subset=ret_cols).format(precision=2, na_rep="–")
    st.dataframe(styled, hide_index=True, use_container_width=True)


with st.sidebar:
    raw = st.text_input("Comp tickers (comma-separated)", ", ".join(DEFAULT_COMPS))
    if st.button("Refresh data"):
        st.cache_data.clear()
tickers = tuple(t.strip().upper() for t in raw.split(",") if t.strip())

if not tickers:
    st.warning("Enter at least one ticker.")
    st.stop()

try:
    comps, macro = load(tickers)
except Exception as e:  # network / Yahoo errors
    st.error(f"Could not fetch data: {e}")
    st.stop()

st.subheader("Market backdrop")
show(macro)

st.subheader("Public comps")
show(comps)
st.download_button("Download comps as CSV", comps.to_csv(index=False), "comps.csv", "text/csv")
st.caption("Source: Yahoo Finance (unofficial, ~15 min cache). For screening only.")
