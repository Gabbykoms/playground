# PE Market Data

Small CLI that pulls a market snapshot for a private equity workflow (via Yahoo Finance / `yfinance`):

- **Comps sheet** – listed PE/alt-manager comps: price, 1D/1M/YTD/1Y returns, market cap, EV, EV/EBITDA, P/E, net debt/EBITDA, dividend yield.
- **Macro sheet** – S&P 500, Russell 2000, VIX, 10Y yield, HY and leveraged-loan ETFs, WTI.

**Web app (recommended):**
```
pip install -r requirements.txt
streamlit run app.py
```
Shows the macro and comps tables in the browser with a ticker box, refresh button and CSV download.

**CLI:**
```
pip install -r requirements.txt
python market_data.py                 # -> output/market_snapshot.xlsx
python market_data.py -t KKR BX APO   # custom tickers
python market_data.py --csv
pytest
```

Edit `DEFAULT_COMPS` and `MACRO` in `market_data.py` to change the defaults.
Note: Yahoo data is unofficial and for screening only, not a substitute for CapIQ/PitchBook/Bloomberg.
