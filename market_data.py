"""Pull a market snapshot for a PE watchlist and write it to Excel/CSV.

Usage:
    python market_data.py                       # default watchlist -> output/market_snapshot.xlsx
    python market_data.py -t KKR BX APO         # custom tickers
    python market_data.py --csv                 # CSV files instead of Excel
"""
import argparse
from pathlib import Path

import pandas as pd
import yfinance as yf

# Listed alternative asset managers / PE-relevant public comps.
DEFAULT_COMPS = ["KKR", "BX", "APO", "CG", "ARES", "TPG", "BAM"]

# Market backdrop a PE professional watches: equities, rates, credit, vol, oil.
MACRO = {
    "S&P 500": "^GSPC",
    "Russell 2000": "^RUT",
    "VIX": "^VIX",
    "US 10Y Yield (%)": "^TNX",
    "High Yield Bond ETF (HYG)": "HYG",
    "Leveraged Loan ETF (BKLN)": "BKLN",
    "WTI Crude": "CL=F",
}


def returns_from_prices(prices: pd.Series) -> dict:
    """1D / 1M / YTD / 1Y % returns from a daily close series (sorted by date)."""
    prices = prices.dropna()
    if prices.empty:
        return {"Price": None, "1D %": None, "1M %": None, "YTD %": None, "1Y %": None}
    last_date, last = prices.index[-1], prices.iloc[-1]

    def ret_since(cutoff):
        past = prices[prices.index <= cutoff]
        return None if past.empty else round((last / past.iloc[-1] - 1) * 100, 2)

    return {
        "Price": round(float(last), 2),
        "1D %": round((last / prices.iloc[-2] - 1) * 100, 2) if len(prices) > 1 else None,
        "1M %": ret_since(last_date - pd.DateOffset(months=1)),
        "YTD %": ret_since(pd.Timestamp(year=last_date.year - 1, month=12, day=31, tz=last_date.tz)),
        "1Y %": ret_since(last_date - pd.DateOffset(years=1)),
    }


def fetch_history(tickers: list[str]) -> pd.DataFrame:
    """Daily closes for all tickers, ~13 months back."""
    data = yf.download(tickers, period="13mo", auto_adjust=True, progress=False)["Close"]
    if isinstance(data, pd.Series):  # single ticker
        data = data.to_frame(tickers[0])
    return data


def build_comps(tickers: list[str]) -> pd.DataFrame:
    hist = fetch_history(tickers)
    rows = []
    for t in tickers:
        info = yf.Ticker(t).info
        ebitda, debt, cash = info.get("ebitda"), info.get("totalDebt"), info.get("totalCash")
        net_debt = debt - cash if debt is not None and cash is not None else None
        row = {"Ticker": t, "Name": info.get("shortName")}
        row.update(returns_from_prices(hist[t]) if t in hist else {})
        row.update({
            "Mkt Cap ($bn)": _bn(info.get("marketCap")),
            "EV ($bn)": _bn(info.get("enterpriseValue")),
            "EV/EBITDA": _round(info.get("enterpriseToEbitda")),
            "P/E (TTM)": _round(info.get("trailingPE")),
            "Fwd P/E": _round(info.get("forwardPE")),
            "Net Debt/EBITDA": _round(net_debt / ebitda) if net_debt is not None and ebitda else None,
            "Div Yield %": _round(info.get("dividendYield")),
        })
        rows.append(row)
    return pd.DataFrame(rows)


def build_macro() -> pd.DataFrame:
    hist = fetch_history(list(MACRO.values()))
    rows = []
    for name, t in MACRO.items():
        r = returns_from_prices(hist[t]) if t in hist else {}
        rows.append({"Indicator": name, "Ticker": t, **r})
    return pd.DataFrame(rows)


def _bn(x):
    return round(x / 1e9, 2) if x else None


def _round(x):
    return round(x, 2) if isinstance(x, (int, float)) else None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-t", "--tickers", nargs="+", default=DEFAULT_COMPS)
    p.add_argument("-o", "--outdir", default="output")
    p.add_argument("--csv", action="store_true", help="write CSVs instead of one Excel file")
    args = p.parse_args()

    comps, macro = build_comps(args.tickers), build_macro()
    out = Path(args.outdir)
    out.mkdir(exist_ok=True)
    if args.csv:
        comps.to_csv(out / "comps.csv", index=False)
        macro.to_csv(out / "macro.csv", index=False)
    else:
        with pd.ExcelWriter(out / "market_snapshot.xlsx") as xw:
            comps.to_excel(xw, "Comps", index=False)
            macro.to_excel(xw, "Macro", index=False)
    print(comps.to_string(index=False), "\n")
    print(macro.to_string(index=False))
    print(f"\nSaved to {out}/")


if __name__ == "__main__":
    main()
