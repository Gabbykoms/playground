import pandas as pd
from streamlit.testing.v1 import AppTest
import market_data


def test_app_renders(monkeypatch):
    comps = pd.DataFrame({"Ticker": ["KKR"], "1D %": [1.2], "Price": [100.0]})
    macro = pd.DataFrame({"Indicator": ["VIX"], "1D %": [-2.0]})
    monkeypatch.setattr(market_data, "build_comps", lambda t: comps)
    monkeypatch.setattr(market_data, "build_macro", lambda: macro)
    at = AppTest.from_file("../app.py").run()
    assert not at.exception
    assert len(at.dataframe) == 2
