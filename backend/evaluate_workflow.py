"""
Evaluate the stock recommendation workflow against the test dataset.

This script runs the workflow on each scenario in the dataset and evaluates
whether the actual recommendations match the expected outcomes.

Usage:
    python evaluate_workflow.py --dataset-name <dataset_name>
"""

import asyncio
import argparse
import os
from opik import Opik
from opik.evaluation import evaluate
from opik.evaluation.metrics.score_result import ScoreResult
from app.workflow_agent import WorkflowAgent
from app.models import RiskAppetite, TimeHorizon, AdvisorState
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv
from opik.evaluation.metrics import BaseMetric
from opik.evaluation.metrics.llm_judges.g_eval_presets import ComplianceRiskJudge

# Load environment variables
load_dotenv()


# Custom metric: Check if suggested action matches expected
class ActionMatchMetric(BaseMetric):
    def __init__(self):
        super().__init__(name="action_match", track=True)
    def score(self, input: dict, expected_output: dict, output: dict, **ignored_kwargs):
        response = output.get("response")
        print(f'output: {response.get("suggested_action").value}, expected_output: {expected_output.get("suggested_action")}')
        """Check if the suggested action matches the expected action."""
        actual_action = response.get("suggested_action").value
        expected_action = expected_output.get("suggested_action")

        match = actual_action == expected_action
        score = 1.0 if match else 0.0

        return ScoreResult(
            name="action_match",
            value=score,
            reason=f"Expected: {expected_action}, Got: {actual_action}"
        )


# Custom metric: Check if guardrail overrode the decision
class GuardrailCheckMetric(BaseMetric):
    def __init__(self):
        super().__init__(name="guardrail_check", track=True)
    def score(self, input: dict, expected_output: dict, output: dict, **ignored_kwargs):
        """Check if guardrail was triggered (should be False for all scenarios)."""
        guardrail_override = output.get('response').get("guardrail_override")

        was_triggered = guardrail_override is not None
        score = 0.0 if was_triggered else 1.0

        reason = "Guardrail triggered (unexpected)" if was_triggered else "No guardrail trigger (expected)"

        return ScoreResult(
            name="guardrail_check",
            value=score,
            reason=reason
        )

class WrappedComplianceRiskJudge(BaseMetric):
    def __init__(self):
        super().__init__(name="reasoning_compliance_risk_judge", track=True)
        self.judge = ComplianceRiskJudge(model="gpt-4", track=False)

    def score(self, input: dict, expected_output: dict, output: dict, **ignored_kwargs):
        """Use ComplianceRiskJudge to evaluate the response."""
        response = output.get("response")
        reasoning = response.get("reasoning", "")

        judge_result = self.judge.score(output=reasoning)

        return ScoreResult(
            name="reasoning_compliance_risk_judge",
            value=judge_result.value,
            reason=judge_result.reason,
            metadata=judge_result.metadata,
            scoring_failed=judge_result.scoring_failed
        )

# Task function that wraps the workflow
async def evaluate_task(input_data: dict, workflow_agent: WorkflowAgent) -> dict:
    """
    Run the workflow for a single input scenario.

    Args:
        input_data: Dictionary with ticker_symbol, risk_appetite, time_horizon
        workflow_agent: Instance of WorkflowAgent

    Returns:
        Dictionary with suggested_action, reasoning, and other outputs
    """
    # Convert string risk appetite to enum
    risk_appetite_map = {
        "Low": RiskAppetite.LOW,
        "Medium": RiskAppetite.MEDIUM,
        "High": RiskAppetite.HIGH
    }

    time_horizon_map = {
        "Short-term": TimeHorizon.SHORT_TERM,
        "Medium-term": TimeHorizon.MEDIUM_TERM,
        "Long-term": TimeHorizon.LONG_TERM
    }

    # Build state (TypedDict style)
    state = {
        'ticker_symbol': input_data["ticker_symbol"],
        'risk_appetite': risk_appetite_map[input_data["risk_appetite"]],
        'time_horizon': time_horizon_map[input_data["time_horizon"]]
    }

    # Run workflow
    result = await workflow_agent.ainvoke(state)

    response = result.get('response')
    print(f'result for {input_data["ticker_symbol"]}: {response.suggested_action}')
    response_dict = {
        'suggested_action': response.suggested_action,
        'reasoning': response.reasoning,
    }
    if hasattr(response, 'guardrail_override'):
        response_dict['guardrail_override'] = response.guardrail_override
    return {'output': {'response': response_dict}} # wrapped like this to match the runtime output format (so the online metric also works)


async def run_evaluation(dataset_name: str):
    """Run evaluation on the specified dataset."""

    print(f"🔍 Starting evaluation on dataset: {dataset_name}")

    # Initialize Opik client
    opik_client = Opik()

    # Get dataset
    try:
        dataset = opik_client.get_dataset(name=dataset_name)
        dataset_items = list(dataset.get_items())
        print(f"✅ Found dataset with {len(dataset_items)} items")
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return

    # Initialize workflow agent with MCP tools
    print("🤖 Initializing workflow agent...")
    alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not alpha_vantage_api_key:
        print("❌ Error: ALPHA_VANTAGE_API_KEY not found in environment")
        return

    alpha_vantage_mcp_url = f'https://mcp.alphavantage.co/mcp?apikey={alpha_vantage_api_key}'

    async with streamablehttp_client(alpha_vantage_mcp_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            overview_tool = [tool for tool in tools if tool.name == 'COMPANY_OVERVIEW'][0]
            workflow_agent = WorkflowAgent(overview_tool=overview_tool)

            # Create async wrapper for the task
            async def task_wrapper(item):
                return await evaluate_task(item["input"], workflow_agent)

            # Run evaluation
            print("🏃 Running evaluation...")
            print("⏳ This may take several minutes depending on the number of scenarios...\n")

            eval_results = evaluate(
                dataset=dataset,
                task=lambda item: asyncio.run(task_wrapper(item)),
                scoring_metrics=[
                    ActionMatchMetric(),
                    GuardrailCheckMetric(),
                    WrappedComplianceRiskJudge()
                ],
                experiment_name=f"workflow_eval_{dataset_name}"
            )

            print("\n✅ Evaluation complete!")
            print("📊 View results in Opik UI")

            return eval_results


def main():
    parser = argparse.ArgumentParser(description="Evaluate stock recommendation workflow")
    parser.add_argument(
        "--dataset-name",
        type=str,
        help="Name of the Opik dataset to evaluate against"
    )

    args = parser.parse_args()

    if not args.dataset_name:
        print("❌ No dataset name provided.\n")
        print("💡 Create a dataset first by running: python create_evaluation_dataset.py")
        print("💡 Then run this script with: python evaluate_workflow.py --dataset-name <name>")
        print("\n📋 Check the Opik UI to see available datasets")
        return

    # Run async evaluation
    asyncio.run(run_evaluation(args.dataset_name))


if __name__ == "__main__":
    main()
