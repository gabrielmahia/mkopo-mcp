"""Live tools: parsing, provenance, validation and failure behaviour, with the network mocked (CI never depends on the services)."""
import urllib.error

from mkopo_mcp import main as server


def _boom(url, params=None, timeout=20.0):
    raise urllib.error.URLError("down")

def test_macro_indicators_flag_projections_and_merge_rates(monkeypatch):
    import datetime as _dt
    y = _dt.datetime.now(_dt.UTC).year
    imf = {"values": {"PCPIPCH": {"KEN": {str(y - 1): 4.5, str(y): 5.0, str(y + 1): 5.1}}}}
    wb = {"FR.INR.LEND": [{"date": str(y - 1), "value": 15.2}], "FR.INR.DPST": [{"date": str(y - 1), "value": 8.1}]}
    monkeypatch.setattr(server, "_live_get", lambda url, params=None, timeout=20.0: imf if "imf.org" in url else [{}, wb[url.rsplit("/", 1)[1]]])
    r = server.kenya_macro_indicators(2)
    assert [(i["year"], i["imf_projection"]) for i in r["inflation"]] == [(str(y - 1), False), (str(y), True), (str(y + 1), True)]
    assert r["interest_rates"][0] == {"year": str(y - 1), "lending_rate_pct": 15.2, "deposit_rate_pct": 8.1}


def test_macro_indicators_failure_and_bad_input_never_give_figures(monkeypatch):
    monkeypatch.setattr(server, "_live_get", _boom)
    assert "error" in server.kenya_macro_indicators() and "inflation" not in server.kenya_macro_indicators()
    assert "error" in server.kenya_macro_indicators(0)
