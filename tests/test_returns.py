import pandas as pd
from market_data import returns_from_prices


def test_returns():
    idx = pd.bdate_range("2025-01-02", "2026-01-15")
    prices = pd.Series(range(100, 100 + len(idx)), index=idx, dtype=float)
    r = returns_from_prices(prices)
    assert r["Price"] == prices.iloc[-1]
    assert r["1D %"] == round((prices.iloc[-1] / prices.iloc[-2] - 1) * 100, 2)
    assert r["YTD %"] is not None and r["1Y %"] is not None


def test_empty():
    assert returns_from_prices(pd.Series(dtype=float))["Price"] is None
