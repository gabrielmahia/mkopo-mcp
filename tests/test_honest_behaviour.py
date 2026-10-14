from mkopo_mcp import main as server

_fn = lambda name: (getattr(server, name).fn if hasattr(getattr(server, name), "fn") else getattr(server, name))


def test_an_unknown_credit_tier_says_it_was_treated_as_thin_file():
    r = _fn("loan_eligibility")(50000, "ASTRONAUT", "education", 20000)
    assert r["credit_tier_applied"] == "THIN_FILE"
    assert _fn("loan_eligibility")(50000, "PRIME", "education", 20000)["credit_tier_applied"] == "PRIME"
