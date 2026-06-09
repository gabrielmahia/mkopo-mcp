#!/usr/bin/env python3
# mkopo-mcp — Alternative Credit Scoring MCP Server
# © 2026 Gabriel Mahia / AI Kung Fu LLC — MIT License
#
# The problem: 70%+ of Kenyan adults are "credit invisible" — no formal credit history.
# The insight: M-PESA is a de facto financial history that predicts repayment behaviour.
# Western parallel: FICO score, Experian API, Nova Credit (immigrant credit), Petal card.
# Methodology: Inspired by academic literature on alternative credit scoring:
#   - World Bank "Expanding Access to Finance" (2022)
#   - Kendall, Mylenko & Ponce "Measuring Financial Access" (2010)
#   - Breza & Kinnan "Measuring the Equilibrium Impacts of Credit" (2021)
#
# TRUST INTEGRITY: All scoring is DEMO/educational. No real credit decisions.
# Not affiliated with CRB Africa, Metropol, TransUnion Kenya, or any lender.
# =============================================================================

from __future__ import annotations
import json
import datetime
from typing import Annotated
from fastmcp import FastMCP

mcp = FastMCP(
    name="mkopo-mcp",
    instructions="""Alternative credit scoring MCP server for Kenya.
    Provides tools to estimate creditworthiness from behavioural signals
    when formal credit history is absent.
    
    IMPORTANT: All scoring is DEMO/synthetic for educational purposes.
    Not a regulated credit bureau. Not for use in actual lending decisions.
    Consult a licensed lender and Kenya CRB before any credit decision.
    """,
)

# Behavioural signals that predict creditworthiness (research-backed)
POSITIVE_SIGNALS = [
    "Regular M-PESA deposits (consistent income pattern)",
    "Utility payment regularity (KPLC, Nairobi Water)",
    "Low month-end balance depletion (savings behaviour)",
    "Long tenure as M-PESA user (stability signal)",
    "Regular small savings contributions (e.g., chama, M-Shwari)",
    "Business transaction diversity (multiple income streams)",
    "Airtime purchase frequency (proxy for phone activity = employability)",
]

NEGATIVE_SIGNALS = [
    "Overdraft or negative Fuliza balance (short-term distress)",
    "Irregular or absent income deposits",
    "High Fuliza usage relative to income",
    "Gaps in mobile money activity (financial exclusion periods)",
    "Large unexplained single transactions (irregular income pattern)",
]

def _score_from_signals(positive_count: int, negative_count: int, months: int) -> dict:
    """Calculate a demo credit score from signal counts."""
    base = 300
    positive_weight = 40
    negative_weight = 60
    tenure_bonus = min(50, months * 2)
    raw = base + (positive_count * positive_weight) - (negative_count * negative_weight) + tenure_bonus
    score = max(300, min(850, raw))
    tier = (
        "PRIME" if score >= 720 else
        "NEAR_PRIME" if score >= 660 else
        "SUBPRIME" if score >= 580 else
        "THIN_FILE"
    )
    return {"score": score, "tier": tier}


@mcp.tool(
    description=(
        "Estimate an alternative credit score from M-PESA behavioural signals. "
        "Western parallel: FICO score / Nova Credit for immigrants with no US history. "
        "Inputs are self-reported for demo purposes — a real implementation would "
        "connect to licensed M-PESA data-sharing APIs with customer consent. "
        "DEMO — not a real credit bureau product."
    ),
    annotations={"readOnlyHint": True},
)
def alternative_credit_score(
    months_as_mpesa_user: Annotated[int, "How many months the person has used M-PESA (0-240)"],
    has_regular_income_deposits: Annotated[bool, "Receives regular deposits (salary, business income) at least twice monthly"],
    pays_utilities_on_time: Annotated[bool, "Has paid KPLC or water bills via M-PESA in past 6 months"],
    has_savings_behaviour: Annotated[bool, "Makes regular small savings (M-Shwari, chama, SACCO, KCB M-PESA)"],
    has_fuliza_debt: Annotated[bool, "Currently has unpaid Fuliza (Safaricom overdraft) balance"],
    has_multiple_income_streams: Annotated[bool, "Receives income from more than one source (multiple employers, business + salary)"],
    has_loan_default_history: Annotated[bool, "Has defaulted on any previous loan (M-Shwari, KCB, bank, chama)"],
) -> dict:
    positive = sum([
        has_regular_income_deposits,
        pays_utilities_on_time,
        has_savings_behaviour,
        has_multiple_income_streams,
    ])
    negative = sum([has_fuliza_debt, has_loan_default_history])
    result = _score_from_signals(positive, negative, months_as_mpesa_user)

    tier_desc = {
        "PRIME": "Strong creditworthiness. Eligible for most formal loan products.",
        "NEAR_PRIME": "Good creditworthiness. Eligible for most microfinance and digital lenders.",
        "SUBPRIME": "Moderate risk. Digital lenders may apply higher rates. Focus on savings first.",
        "THIN_FILE": "Insufficient history. Build signals: save consistently, pay utilities, reduce Fuliza.",
    }

    return {
        "status": "OK",
        "demo_credit_score": result["score"],
        "credit_tier": result["tier"],
        "tier_description": tier_desc[result["tier"]],
        "score_range": "300 (lowest) to 850 (highest) — mirrors Kenya CRB credit score scale",
        "positive_signals_found": positive,
        "risk_signals_found": negative,
        "eligible_lenders_demo": {
            "PRIME": ["KCB", "Equity Bank", "Co-operative Bank", "Standard Chartered", "Absa"],
            "NEAR_PRIME": ["M-Shwari", "Tala", "Branch", "Zenka", "Timiza"],
            "SUBPRIME": ["Tala (reduced limit)", "Branch (reduced limit)", "Haraka"],
            "THIN_FILE": ["Chama/SACCO internal loans", "M-Shwari (starter limit KES 200)"],
        }.get(result["tier"], []),
        "note": "DEMO — Synthetic scoring model. Not a CRB product. Consult Metropol, CRB Africa, or TransUnion Kenya for real credit reports.",
        "source": "mkopo-mcp. Methodology: World Bank Financial Inclusion Database 2022, Breza & Kinnan (2021).",
    }


@mcp.tool(
    description=(
        "Analyse M-PESA transaction patterns to assess creditworthiness. "
        "Takes simplified transaction summary inputs (no raw transaction data). "
        "Western parallel: Plaid income verification, Finicity, Experian Boost. "
        "DEMO — requires informed customer consent in production."
    ),
    annotations={"readOnlyHint": True},
)
def mpesa_creditworthiness(
    avg_monthly_inflow_kes: Annotated[int, "Average monthly M-PESA inflows (deposits received) in KES"],
    avg_monthly_outflow_kes: Annotated[int, "Average monthly M-PESA outflows (payments made) in KES"],
    months_analysed: Annotated[int, "Number of months of M-PESA history available (1-24)"],
    fuliza_usage_kes: Annotated[int, "Average monthly Fuliza (overdraft) usage in KES (0 if none)"],
    has_business_paybill: Annotated[bool, "Receives payments to a business Paybill or Till number"],
) -> dict:
    if avg_monthly_inflow_kes <= 0:
        return {"status": "ERROR", "message": "Monthly inflow must be positive"}

    savings_rate = max(0, (avg_monthly_inflow_kes - avg_monthly_outflow_kes) / avg_monthly_inflow_kes)
    fuliza_ratio = fuliza_usage_kes / avg_monthly_inflow_kes if avg_monthly_inflow_kes > 0 else 0
    debt_service_capacity_kes = int(avg_monthly_inflow_kes * 0.3)  # 30% of income = standard debt service ratio

    # DSR: recommended loan repayment should not exceed 30% of income
    affordable_loan_kes = debt_service_capacity_kes * 12  # annual
    affordable_loan_12m_kes = int(affordable_loan_kes * 0.85)  # 85% of theoretical max

    risk_flags = []
    if fuliza_ratio > 0.15: risk_flags.append("High Fuliza usage (>15% of income)")
    if savings_rate < 0.05: risk_flags.append("Very low savings rate (<5%) — income fully consumed")
    if months_analysed < 3: risk_flags.append("Short history — lenders prefer 6+ months")
    if avg_monthly_outflow_kes > avg_monthly_inflow_kes: risk_flags.append("Outflows exceed inflows — negative net flow")

    strengths = []
    if savings_rate > 0.15: strengths.append(f"Good savings rate: {savings_rate*100:.0f}% of income")
    if has_business_paybill: strengths.append("Business income verification possible via Paybill history")
    if months_analysed >= 12: strengths.append(f"Strong {months_analysed}-month history")
    if fuliza_ratio < 0.05: strengths.append("Low Fuliza dependency")

    return {
        "status": "OK",
        "financial_profile": {
            "avg_monthly_income_kes": avg_monthly_inflow_kes,
            "avg_monthly_expenses_kes": avg_monthly_outflow_kes,
            "savings_rate_pct": f"{savings_rate*100:.1f}%",
            "fuliza_to_income_ratio": f"{fuliza_ratio*100:.1f}%",
            "history_months": months_analysed,
        },
        "creditworthiness_signals": {
            "strengths": strengths,
            "risk_flags": risk_flags,
        },
        "loan_capacity_estimate": {
            "max_monthly_repayment_kes": debt_service_capacity_kes,
            "affordable_12m_loan_kes": affordable_loan_12m_kes,
            "basis": "30% Debt Service Ratio (Kenya bank standard)",
            "note": "Estimate only — actual approval depends on lender policy and CRB check",
        },
        "note": "DEMO — Synthetic analysis. Real lenders conduct formal CRB checks via Metropol or CRB Africa.",
        "source": "mkopo-mcp. Reference: CBK Prudential Guidelines 2022, Kenya CRB Regulations.",
    }


@mcp.tool(
    description=(
        "Generate a structured credit report summary — the document a loan officer "
        "would review. Western parallel: Experian or Equifax credit report. "
        "DEMO — not a real CRB product."
    ),
    annotations={"readOnlyHint": True},
)
def credit_report_summary(
    full_name: Annotated[str, "Applicant full name (for report header only)"],
    id_number: Annotated[str, "National ID number (used as report reference — not stored)"],
    employment_type: Annotated[str, "Employment type: formal_employed, self_employed, casual_labour, farmer, gig_worker, unemployed"],
    monthly_income_kes: Annotated[int, "Declared monthly income in KES"],
    existing_loans_count: Annotated[int, "Number of active loans (digital, bank, chama, SACCO)"],
    has_crb_listing: Annotated[bool, "Has been listed with a Kenya Credit Reference Bureau (CRB)"],
) -> dict:
    today = datetime.date.today().isoformat()
    debt_burden = min(5, existing_loans_count)

    income_tier = (
        "HIGH" if monthly_income_kes >= 100000 else
        "MIDDLE" if monthly_income_kes >= 30000 else
        "LOW" if monthly_income_kes >= 10000 else "VERY_LOW"
    )

    risk_level = "HIGH" if has_crb_listing else ("MEDIUM" if existing_loans_count > 2 else "LOW")

    return {
        "status": "OK",
        "report_header": {
            "applicant_name": full_name,
            "id_reference": id_number[-4:].rjust(len(id_number), "*"),  # mask ID
            "report_date": today,
            "report_type": "DEMO Alternative Credit Summary",
        },
        "income_assessment": {
            "declared_income_kes": monthly_income_kes,
            "income_tier": income_tier,
            "employment_type": employment_type,
            "income_verification_method": "M-PESA statement or payslip (not verified in demo)",
        },
        "credit_profile": {
            "active_loans": existing_loans_count,
            "debt_burden_rating": f"{debt_burden}/5 (higher = more indebted)",
            "crb_adverse_listing": has_crb_listing,
            "overall_risk_level": risk_level,
        },
        "recommended_products": {
            "formal_bank": not has_crb_listing and income_tier in ("HIGH", "MIDDLE"),
            "microfinance": not has_crb_listing,
            "digital_lender": not has_crb_listing,
            "chama_sacco": True,  # always available
        },
        "improvement_actions": [
            "Clear CRB listing immediately if listed (contact Metropol or CRB Africa)",
            "Reduce active loan count to 2 or fewer before applying for new credit",
            "Build 6+ months of consistent M-PESA savings history (M-Shwari)",
            "Obtain a payslip or business records to support income declaration",
        ] if risk_level in ("HIGH", "MEDIUM") else [
            "Maintain current payment discipline",
            "Consider increasing savings contributions",
            "Review loan products annually as income grows",
        ],
        "disclaimer": "DEMO REPORT — Not a real CRB product. For official Kenya credit report: crbafrica.co.ke or metropol.co.ke",
        "source": "mkopo-mcp. Reference: Kenya CRB Act (Cap. 44A), CBK Prudential Guidelines.",
    }


@mcp.tool(
    description=(
        "Estimate loan eligibility across Kenya lender types. "
        "Western parallel: LendingTree loan comparison, Bankrate. "
        "DEMO — not actual loan offers."
    ),
    annotations={"readOnlyHint": True},
)
def loan_eligibility(
    monthly_income_kes: Annotated[int, "Monthly income in KES"],
    credit_tier: Annotated[str, "Credit tier from alternative_credit_score: PRIME, NEAR_PRIME, SUBPRIME, THIN_FILE"],
    loan_purpose: Annotated[str, "Loan purpose: business_working_capital, home_improvement, education, emergency, agriculture, equipment"],
    requested_amount_kes: Annotated[int, "Requested loan amount in KES"],
) -> dict:
    LENDER_PRODUCTS = {
        "PRIME": [
            {"lender": "KCB", "type": "Bank", "max_kes": 5000000, "rate_pa": "13-18%", "term": "Up to 60 months", "requirement": "3 months payslip"},
            {"lender": "Equity Bank", "type": "Bank", "max_kes": 3000000, "rate_pa": "14-19%", "term": "Up to 48 months", "requirement": "Business records or payslip"},
            {"lender": "M-Shwari", "type": "Digital", "max_kes": 50000, "rate_pa": "~84%", "term": "30 days", "requirement": "M-PESA history"},
        ],
        "NEAR_PRIME": [
            {"lender": "Tala", "type": "Digital", "max_kes": 30000, "rate_pa": "~120%", "term": "30-60 days", "requirement": "M-PESA history, Tala app score"},
            {"lender": "Branch", "type": "Digital", "max_kes": 70000, "rate_pa": "~180%", "term": "Up to 12 months", "requirement": "M-PESA + phone data"},
            {"lender": "SACCO", "type": "SACCO", "max_kes": 300000, "rate_pa": "12-15%", "term": "Up to 36 months", "requirement": "SACCO membership, savings"},
        ],
        "SUBPRIME": [
            {"lender": "Tala (reduced)", "type": "Digital", "max_kes": 3000, "rate_pa": "~120%", "term": "30 days", "requirement": "M-PESA history"},
            {"lender": "Chama internal loan", "type": "Chama", "max_kes": 50000, "rate_pa": "5-15%", "term": "Chama terms", "requirement": "Chama membership"},
        ],
        "THIN_FILE": [
            {"lender": "M-Shwari (starter)", "type": "Digital", "max_kes": 500, "rate_pa": "~84%", "term": "30 days", "requirement": "Safaricom M-PESA account"},
            {"lender": "Chama internal loan", "type": "Chama", "max_kes": 20000, "rate_pa": "5-15%", "term": "Chama terms", "requirement": "Join a chama first"},
        ],
    }

    eligible = LENDER_PRODUCTS.get(credit_tier, LENDER_PRODUCTS["THIN_FILE"])
    affordable = [p for p in eligible if p["max_kes"] >= requested_amount_kes]
    max_capacity = int(monthly_income_kes * 0.3 * 12)

    return {
        "status": "OK",
        "loan_request": {
            "requested_kes": requested_amount_kes,
            "purpose": loan_purpose,
            "credit_tier": credit_tier,
        },
        "affordability_check": {
            "monthly_income_kes": monthly_income_kes,
            "max_affordable_annual_repayment_kes": max_capacity,
            "requested_vs_capacity": "WITHIN CAPACITY" if requested_amount_kes <= max_capacity else "EXCEEDS CAPACITY",
        },
        "eligible_products": affordable if affordable else eligible[:2],
        "recommendation": (
            f"With {credit_tier} tier and KES {monthly_income_kes:,}/month income, "
            f"{'the requested KES {:,} is feasible — compare rates below.'.format(requested_amount_kes) if affordable else 'consider a smaller loan amount or building credit history first.'}"
        ),
        "note": "DEMO — Not actual loan offers. Rates are market estimates. Always read full terms before signing.",
        "source": "mkopo-mcp. Reference: Kenya Bankers Association product catalogue 2024.",
    }


@mcp.tool(
    description=(
        "Generate actionable credit improvement tips personalised to the user's situation. "
        "Western parallel: Credit Karma improvement recommendations. "
        "DEMO educational content."
    ),
    annotations={"readOnlyHint": True},
)
def credit_improvement_tips(
    current_tier: Annotated[str, "Current credit tier: PRIME, NEAR_PRIME, SUBPRIME, THIN_FILE"],
    has_fuliza_debt: Annotated[bool, "Has unpaid Fuliza balance"],
    has_crb_listing: Annotated[bool, "Has CRB adverse listing"],
    months_saving: Annotated[int, "Months of consistent savings history (0-60)"],
) -> dict:
    tips = []
    timeline_months = 0

    if has_crb_listing:
        tips.append({
            "priority": 1, "action": "Clear CRB listing",
            "how": "Contact Metropol (metropol.co.ke) or CRB Africa (crbafrica.co.ke) to get your report. Pay the listed debt and request clearance.",
            "impact": "Unlocks access to formal bank credit. Typically takes 2-4 weeks after payment.",
            "cost_estimate": "CRB report: KES 100 (free via Safaricom once/year). Clearance: pay the owed amount."
        })
        timeline_months = max(timeline_months, 3)

    if has_fuliza_debt:
        tips.append({
            "priority": 2, "action": "Pay off Fuliza balance",
            "how": "Repay current Fuliza via M-PESA. Then set a personal cap below your typical daily balance.",
            "impact": "Removes negative cash flow signal. Immediately improves M-PESA credit history.",
            "cost_estimate": "Your current Fuliza balance only."
        })
        timeline_months = max(timeline_months, 1)

    if months_saving < 6:
        tips.append({
            "priority": 3, "action": "Build 6 months of M-Shwari/savings history",
            "how": "Save at least KES 200-500/month in M-Shwari, KCB M-PESA Savings, or a SACCO. Consistency matters more than amount.",
            "impact": f"After 6 months: unlocks M-Shwari credit limit increases. Currently {months_saving} months built.",
            "cost_estimate": "KES 200-500/month minimum"
        })
        timeline_months = max(timeline_months, 6 - months_saving)

    if current_tier in ("THIN_FILE", "SUBPRIME"):
        tips.append({
            "priority": 4, "action": "Join a SACCO or chama with internal lending",
            "how": "Find a registered SACCO (sasra.go.ke) in your sector. Contribute monthly for 3+ months before requesting a loan.",
            "impact": "SACCOs offer the best rates in Kenya (12-15% p.a.) for members with savings history.",
            "cost_estimate": "Membership: KES 500-2,000. Monthly contributions: KES 500-5,000."
        })
        timeline_months = max(timeline_months, 3)

    tips.append({
        "priority": 5, "action": "Pay all bills via M-PESA",
        "how": "Pay KPLC, water, rent, and insurance via M-PESA Paybill. This creates a verifiable payment trail.",
        "impact": "Each utility payment is a positive behavioural signal for alternative credit scoring.",
        "cost_estimate": "No additional cost — redirect existing payments through M-PESA."
    })

    return {
        "status": "OK",
        "current_tier": current_tier,
        "estimated_improvement_timeline_months": timeline_months,
        "tips": tips,
        "target_tier": {
            "THIN_FILE": "SUBPRIME in 6 months, NEAR_PRIME in 12-18 months",
            "SUBPRIME": "NEAR_PRIME in 6-12 months with consistent action",
            "NEAR_PRIME": "PRIME in 12-24 months with formal credit history",
            "PRIME": "Maintain: pay on time, keep utilisation below 30%, grow savings",
        }.get(current_tier, "See tips above"),
        "note": "DEMO — Educational guidance. For personalised advice, contact a Kenya Bankers Association member bank.",
        "source": "mkopo-mcp. Reference: CBK Financial Consumer Protection Guidelines 2022.",
    }


def main():
    mcp.run()

if __name__ == "__main__":
    main()
