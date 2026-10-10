"""Credit scoring is where Kenya's automated-decision rules bite (Data Protection Act 2019 s.35; the AI Bill 2026 is proposed, not law)."""
import asyncio

from fastmcp import Client

from mkopo_mcp import main as m

fn = lambda name: (getattr(m, name).fn if hasattr(getattr(m, name), "fn") else getattr(m, name))
CALLS = {
    "alternative_credit_score": {"months_as_mpesa_user": 36, "has_regular_income_deposits": True, "pays_utilities_on_time": True, "has_savings_behaviour": True, "has_fuliza_debt": False, "has_multiple_income_streams": False, "has_loan_default_history": False},
    "mpesa_creditworthiness": {"avg_monthly_inflow_kes": 60000, "avg_monthly_outflow_kes": 40000, "months_analysed": 12, "fuliza_usage_kes": 0, "has_business_paybill": False},
    "credit_report_summary": {"full_name": "Demo Person", "id_number": "12345678", "employment_type": "formal_employed", "monthly_income_kes": 50000, "existing_loans_count": 1, "has_crb_listing": False},
    "loan_eligibility": {"monthly_income_kes": 50000, "credit_tier": "PRIME", "loan_purpose": "business", "requested_amount_kes": 100000},
}
REAL_LENDERS = ["KCB", "Equity", "Co-operative", "Standard Chartered", "Absa", "M-Shwari", "Tala", "Branch", "Zenka", "Timiza", "Haraka"]


def test_every_scoring_tool_carries_the_automated_decision_notice():
    for name, args in CALLS.items():
        n = fn(name)(**args)["automated_decision_notice"]
        assert "not a lending decision" in n and "section 35" in n and "not law" in n and "human in the loop" in n, name


def test_the_notice_does_not_overstate_the_proposed_law():
    n = m.AUTOMATED_DECISION_NOTICE
    assert "proposed" in n and "would add" in n and "commentators expect" in n  # proposed bill, expectation attributed, nothing stated as enacted


def test_no_real_lender_is_named_as_eligible_for_a_synthetic_score():
    for tier_args in (dict(CALLS["alternative_credit_score"]), dict(CALLS["alternative_credit_score"], months_as_mpesa_user=0, has_regular_income_deposits=False, pays_utilities_on_time=False, has_savings_behaviour=False, has_fuliza_debt=True, has_loan_default_history=True)):
        out = str(fn("alternative_credit_score")(**tier_args))
        assert not [x for x in REAL_LENDERS if x in out], [x for x in REAL_LENDERS if x in out]
        assert "illustrative_lender_types_note" in out


def test_the_id_is_masked_and_identity_parameters_warn_that_this_is_a_demonstration():
    r = fn("credit_report_summary")(**CALLS["credit_report_summary"])
    assert r["report_header"]["id_reference"] == "****5678"
    async def schemas():
        async with Client(m.mcp) as c:
            return {t.name: t.inputSchema for t in await c.list_tools()}
    props = asyncio.run(schemas())["credit_report_summary"]["properties"]
    assert "DEMONSTRATION" in props["full_name"]["description"] and "DEMONSTRATION" in props["id_number"]["description"]


def test_an_input_error_is_not_a_decision_and_carries_no_notice():
    r = fn("mpesa_creditworthiness")(avg_monthly_inflow_kes=0, avg_monthly_outflow_kes=0, months_analysed=3, fuliza_usage_kes=0, has_business_paybill=False)
    assert r["status"] == "ERROR" and "automated_decision_notice" not in r
