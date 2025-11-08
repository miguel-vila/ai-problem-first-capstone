"""
Create an Opik evaluation dataset for stock recommendation scenarios.

This script creates a dataset with 15 test scenarios covering different
risk profiles and expected BUY/NOT_BUY outcomes without triggering guardrails.

Usage:
    python create_evaluation_dataset.py
"""

from opik import Opik
from datetime import datetime

# Initialize Opik client
opik_client = Opik()

# Define 15 evaluation scenarios
# Format: Each scenario has inputs and expected outputs
evaluation_scenarios = [
    # === BUY Scenarios (8 total) ===

    # 1. Low Risk + Stable Dividend Stock
    {
        "ticker_symbol": "KO",  # Coca-Cola, beta ~0.6
        "risk_appetite": "Low",
        "time_horizon": "Long-term",
        "expected_action": "Buy",
        "rationale": "Low beta defensive stock suitable for conservative investors",
        "expected_beta": 0.6
    },

    # 2. Low Risk + Healthcare Blue Chip
    {
        "ticker_symbol": "JNJ",  # Johnson & Johnson, beta ~0.7
        "risk_appetite": "Low",
        "time_horizon": "Medium-term",
        "expected_action": "Buy",
        "rationale": "Stable healthcare giant with consistent dividends",
        "expected_beta": 0.7
    },

    # 3. Low Risk + Consumer Staples
    {
        "ticker_symbol": "PG",  # Procter & Gamble, beta ~0.5
        "risk_appetite": "Low",
        "time_horizon": "Long-term",
        "expected_action": "Buy",
        "rationale": "Defensive consumer staples with stable cash flows",
        "expected_beta": 0.5
    },

    # 4. Medium Risk + Established Tech
    {
        "ticker_symbol": "MSFT",  # Microsoft, beta ~0.9
        "risk_appetite": "Medium",
        "time_horizon": "Medium-term",
        "expected_action": "Buy",
        "rationale": "Strong fundamentals, moderate volatility, market leader",
        "expected_beta": 0.9
    },

    # 5. Medium Risk + Diversified Tech
    {
        "ticker_symbol": "AAPL",  # Apple, beta ~1.0
        "risk_appetite": "Medium",
        "time_horizon": "Long-term",
        "expected_action": "Buy",
        "rationale": "Market leader with strong ecosystem and financials",
        "expected_beta": 1.0
    },

    # 6. High Risk + Growth Tech
    {
        "ticker_symbol": "NVDA",  # NVIDIA, beta ~1.7
        "risk_appetite": "High",
        "time_horizon": "Long-term",
        "expected_action": "Buy",
        "rationale": "High growth potential in AI/semiconductors for aggressive investors",
        "expected_beta": 1.7
    },

    # 7. High Risk + EV Leader
    {
        "ticker_symbol": "TSLA",  # Tesla, beta ~2.0
        "risk_appetite": "High",
        "time_horizon": "Medium-term",
        "expected_action": "Buy",
        "rationale": "High volatility acceptable for high risk tolerance",
        "expected_beta": 2.0
    },

    # 8. Medium Risk + Financial Services
    {
        "ticker_symbol": "V",  # Visa, beta ~0.95
        "risk_appetite": "Medium",
        "time_horizon": "Long-term",
        "expected_action": "Buy",
        "rationale": "Strong payment network with consistent growth",
        "expected_beta": 0.95
    },

    # === NOT_BUY Scenarios (7 total) ===

    # 9. Medium Risk + Volatile Social Media
    {
        "ticker_symbol": "SNAP",  # Snapchat, beta ~1.5
        "risk_appetite": "Medium",
        "time_horizon": "Short-term",
        "expected_action": "Not Buy",
        "rationale": "Negative earnings/user growth trends, competitive pressures",
        "expected_beta": 1.5
    },

    # 10. Medium Risk + Declining Video Conferencing
    {
        "ticker_symbol": "ZM",  # Zoom, beta ~1.2
        "risk_appetite": "Medium",
        "time_horizon": "Short-term",
        "expected_action": "Not Buy",
        "rationale": "Post-pandemic decline, valuation concerns, slowing growth",
        "expected_beta": 1.2
    },

    # 11. High Risk + Speculative EV Startup
    {
        "ticker_symbol": "RIVN",  # Rivian, beta ~1.8
        "risk_appetite": "High",
        "time_horizon": "Short-term",
        "expected_action": "Not Buy",
        "rationale": "Cash burn concerns, production challenges despite risk tolerance",
        "expected_beta": 1.8
    },

    # # 12. Medium Risk + Struggling Fintech
    # {
    #     "ticker_symbol": "SQ",  # Block (Square), beta ~1.6
    #     "risk_appetite": "Medium",
    #     "time_horizon": "Short-term",
    #     "expected_action": "Not Buy",
    #     "rationale": "Regulatory concerns, profitability challenges",
    #     "expected_beta": 1.6
    # },

    # 13. Low Risk + Struggling Retail
    {
        "ticker_symbol": "M",  # Macy's, beta ~0.9
        "risk_appetite": "Low",
        "time_horizon": "Short-term",
        "expected_action": "Not Buy",
        "rationale": "Declining retail sector, e-commerce pressure",
        "expected_beta": 0.9
    },

    # 14. Medium Risk + Overvalued Streaming
    {
        "ticker_symbol": "NFLX",  # Netflix, beta ~1.2
        "risk_appetite": "Medium",
        "time_horizon": "Short-term",
        "expected_action": "Not Buy",
        "rationale": "High valuation, intense competition, subscriber growth concerns",
        "expected_beta": 1.2
    },

    # 15. High Risk + Volatile Biotech
    {
        "ticker_symbol": "MRNA",  # Moderna, beta ~1.5
        "risk_appetite": "High",
        "time_horizon": "Short-term",
        "expected_action": "Not Buy",
        "rationale": "Post-COVID decline in vaccine revenue, pipeline uncertainty",
        "expected_beta": 1.5
    }
]


def create_dataset():
    """Create Opik dataset with evaluation scenarios."""

    dataset_name = f"stock_recommendation_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"Creating dataset: {dataset_name}")
    print(f"Number of scenarios: {len(evaluation_scenarios)}")

    # Create the dataset
    dataset = opik_client.create_dataset(
        name=dataset_name,
        description="Evaluation dataset for stock recommendation system with expected BUY/NOT_BUY outcomes"
    )

    # Prepare items for batch insertion
    items = []
    buy_count = 0
    not_buy_count = 0

    for idx, scenario in enumerate(evaluation_scenarios, 1):
        expected_action = scenario["expected_action"]

        if expected_action == "BUY":
            buy_count += 1
        else:
            not_buy_count += 1

        item = {
            "input": {
                "ticker_symbol": scenario["ticker_symbol"],
                "risk_appetite": scenario["risk_appetite"],
                "time_horizon": scenario["time_horizon"]
            },
            "expected_output": {
                "suggested_action": expected_action
            },
            "metadata": {
                "scenario_id": idx,
                "rationale": scenario["rationale"],
                "expected_beta": scenario["expected_beta"],
                "risk_appetite": scenario["risk_appetite"],
                "time_horizon": scenario["time_horizon"]
            }
        }
        items.append(item)

        print(f"  {idx}. {scenario['ticker_symbol']:6} | Risk: {scenario['risk_appetite']:6} | Expected: {expected_action:8} | Beta: ~{scenario['expected_beta']}")

    # Insert all items
    dataset.insert(items)

    print(f"\n✅ Dataset created successfully!")
    print(f"   Name: {dataset_name}")
    print(f"   Total scenarios: {len(items)}")
    print(f"   Expected BUY: {buy_count}")
    print(f"   Expected NOT_BUY: {not_buy_count}")
    print(f"\n💡 Use this dataset for evaluation in Opik UI or programmatically")

    return dataset


if __name__ == "__main__":
    try:
        dataset = create_dataset()
    except Exception as e:
        print(f"\n❌ Error creating dataset: {e}")
        raise
