import asyncio
import json
import os

from app.guardrails.citation_check import check_citations
from dotenv import load_dotenv

load_dotenv(override=True)


async def main():
    # Mock state data (does not contain iPhone unit sales)
    mock_state = {
        "ticker": "AAPL",
        "ratios": {
            "gross_margin": 0.469,
            "operating_margin": 0.32,
            "net_margin": 0.269,
            "fcf_conversion": 0.882,
        },
        "dcf_valuation": {
            "base_case": 1430000000000,
            "bull_case": 1940000000000,
            "bear_case": 1140000000000,
        },
    }

    # Mock report with one completely hallucinated claim
    mock_report = {
        "executive_summary": "Apple Inc. (AAPL) demonstrates elite fundamental metrics: a gross margin of 46.9% and operating margin of 32.0%.",
        "bull_case": "The bull case implies an equity value of $1.94 trillion. Notably, Apple's Q3 2026 iPhone unit sales grew 42% year-over-year, showing massive momentum.",
        "bear_case": "The bear case models an implied equity value of only $1.14 trillion.",
        "synthesized_view": "AAPL is a high-quality compounder. The fundamental engine is intact.",
        "disclaimer": "This is research synthesis, not investment advice.",
    }

    print("Running citation check on report with injected hallucination...")
    result = await check_citations(mock_report, mock_state)

    print("\n--- Citation Check Results ---")
    print(f"Total claims checked: {result.total_claims_checked}")
    print(f"Unsupported claims count: {len(result.unsupported_claims)}")
    print("\nUnsupported Claims Details:")
    for claim in result.unsupported_claims:
        print(f"- {claim}")


if __name__ == "__main__":
    asyncio.run(main())
