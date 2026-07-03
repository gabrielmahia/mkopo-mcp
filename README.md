# 💳 mkopo-mcp — Alternative Credit Scoring MCP Server

[![mkopo-mcp Glama score](https://glama.ai/mcp/servers/gabrielmahia/mkopo-mcp/badges/score.svg)](https://glama.ai/mcp/servers/gabrielmahia/mkopo-mcp)
[![smithery badge](https://smithery.ai/badge/@gabrielmahia/mkopo-mcp)](https://smithery.ai/server/@gabrielmahia/mkopo-mcp)


---
**Compatible with `claude-sonnet-5`** (released 2026-06-30) — Anthropic's most agentic
Sonnet yet. Runs multi-step tool chains end-to-end without stopping short.
Install: `pip install mkopo-mcp` · Use with any MCP client.

---


Most East Africans transacting heavily on mobile money have no formal credit file — the data exists in M-PESA history, but no scoring model reads it as an agent-callable tool.

70%+ of Kenyan adults are "credit invisible" — no formal credit history means no access to capital. M-PESA is a de facto financial history record that predicts repayment behaviour. mkopo-mcp makes that intelligence accessible to AI agents.

## The Structural Problem

In mature economies, credit bureaus have 30+ years of credit card, mortgage, and auto loan data per person. That data machine took 50 years to build. In Kenya, most people's financial lives happen in cash and mobile money — invisible to formal credit systems.

**M-PESA is the credit bureau that doesn't know it is one.**

- Regular income deposits → income stability
- Utility payment regularity → discipline signal
- Savings behaviour (M-Shwari, chama) → future orientation
- Fuliza usage ratio → short-term distress indicator
- Business Paybill receipts → verifiable commercial activity

## Tools

| Tool | What it does |
|------|-------------|
| `alternative_credit_score` | Score from M-PESA behavioural signals (300–850 scale) |
| `mpesa_creditworthiness` | Analyse inflow/outflow patterns for loan capacity |
| `credit_report_summary` | Generate structured report like a loan officer would review |
| `loan_eligibility` | Match to appropriate Kenya lender types |
| `credit_improvement_tips` | Personalised steps to improve credit tier |

## Quick Start

```bash
pip install mkopo-mcp       # coming soon to PyPI
mkopo-mcp                   # starts on stdio
```

## Research Basis

- World Bank "Expanding Access to Finance" (2022)
- Breza & Kinnan "Measuring the Equilibrium Impacts of Credit" (2021)
- CBK Prudential Guidelines (2022)
- Kenya CRB Act (Cap. 44A)

⚠️ DEMO data — not a real CRB product. Consult Metropol or CRB Africa for official reports.

---
*© 2026 Gabriel Mahia / AI Kung Fu LLC · MIT License*

## Part of the East Africa Coordination Stack

This MCP server is one of 32 tools in the Kenya coordination infrastructure.
Connect it to [`africa-coord-bus`](https://github.com/gabrielmahia/africa-coord-bus) —
the coordination event bus that routes signals between domains automatically.

```bash
pip install africa-coord-bus
```

All 32 servers: [pypi.org/user/gmahia](https://pypi.org/user/gmahia/)
Live demo: [coord-cascade-demo](https://github.com/gabrielmahia/coord-cascade-demo)

## IP & Collaboration

MIT licensed. Feedback via GitHub Issues only — pull requests are not accepted. Demo data is labeled DEMO and is not suitable for operational decisions. Full policy: [docs/architecture/IP_POLICY.md](docs/architecture/IP_POLICY.md). Security reports: see [SECURITY.md](SECURITY.md).
