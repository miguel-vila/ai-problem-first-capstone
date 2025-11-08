"""
Simple runner to create dataset and optionally run evaluation.

Usage:
    python run_evaluation.py
"""

import subprocess
import sys


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}\n")

    try:
        subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   Stock Recommendation Evaluation Runner                 ║
║   Creates dataset and runs evaluation                    ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Step 1: Create dataset
    print("Step 1: Creating evaluation dataset...")
    success = run_command(
        "python create_evaluation_dataset.py",
        "Creating Opik dataset with 15 scenarios"
    )

    if not success:
        print("\n❌ Failed to create dataset. Please check the error above.")
        sys.exit(1)

    # Ask user if they want to run evaluation
    print("\n" + "="*60)
    response = input("\n📊 Would you like to run the evaluation now? (y/n): ").strip().lower()

    if response in ['y', 'yes']:
        print("\n⚠️  NOTE: Running evaluation will make API calls and may take several minutes.")
        print("   Each scenario requires: stock data API + news search + LLM calls")

        confirm = input("\nContinue? (y/n): ").strip().lower()

        if confirm in ['y', 'yes']:
            # Get latest dataset name
            # Note: The dataset name includes timestamp, we'd need to get it from create script
            print("\n💡 To run evaluation, use:")
            print("   python evaluate_workflow.py --dataset-name <dataset_name>")
            print("\n   You can find the dataset name in the output above (starts with 'stock_recommendation_eval_')")
        else:
            print("\n✅ Dataset created! You can run evaluation later with:")
            print("   python evaluate_workflow.py --dataset-name <dataset_name>")
    else:
        print("\n✅ Dataset created! You can run evaluation later with:")
        print("   python evaluate_workflow.py --dataset-name <dataset_name>")

    print("\n" + "="*60)
    print("📖 Evaluation Metrics:")
    print("   • action_match: Does output match expected BUY/NOT_BUY?")
    print("   • guardrail_check: Were any guardrails triggered? (should be 0)")
    print("   • has_reasoning: Is there substantive reasoning?")
    print("="*60)


if __name__ == "__main__":
    main()
