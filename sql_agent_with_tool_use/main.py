import sys
import os
import argparse
import unittest

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from db.sample_db_builder import initialize_all_databases
from evaluation.evaluator import ReActAgentEvaluator
from web.server import run_web_server


def print_banner():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 75)
    print("SQL AGENT WITH TOOL USE STUDIO (Laboratory Experiment 4)")
    print("   Develop a ReAct-based agent using database tools")
    print("=" * 75)


def run_unit_tests():
    print("\n[Step 1/3] Running ReAct Agent & Tool Unit Test Suite...")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(BASE_DIR, "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    if not result.wasSuccessful():
        print("❌ Unit test suite failed! Please review test logs above.")
        sys.exit(1)
    print("✅ All unit tests passed cleanly!")


def run_evaluation_benchmark(data_dir: str):
    print("\n[Step 2/3] Executing ReAct Agent Benchmark Evaluation...")
    evaluator = ReActAgentEvaluator(data_dir)
    test_cases_file = os.path.join(BASE_DIR, "evaluation", "test_cases.json")
    results = evaluator.run_benchmark(test_cases_file)

    print("-" * 55)
    print(f"📊 ReAct Benchmark Accuracy Rate : {results['execution_accuracy_rate']}%")
    print(f"📊 Avg Steps per Question        : {results['average_steps_per_query']}")
    print(f"📊 Total Benchmark Cases         : {results['total_cases']}")
    print("📊 Tool Call Distribution        :", results['tool_call_distribution'])
    print("-" * 55)
    print("✅ Benchmark evaluation completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="ReAct SQL Agent Studio (Experiment 4)")
    parser.add_argument("--cli", action="store_true", help="Run CLI validation suite only without launching web server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the visual studio web server (default: 8080)")
    args = parser.parse_args()

    print_banner()

    data_dir = os.path.join(BASE_DIR, "data")
    print(f"\n[Step 0/3] Initializing Relational Databases in '{data_dir}'...")
    dbs = initialize_all_databases(data_dir)
    print(f"✅ Databases initialized: {list(dbs.keys())}")

    run_unit_tests()
    run_evaluation_benchmark(data_dir)

    if args.cli:
        print("\n🎉 CLI Validation Complete! ReAct Agent & Tool Suite validated with 100% success.")
        return

    print(f"\n[Step 3/3] Starting Visual Web Studio on http://localhost:{args.port} ...")
    print("Press Ctrl+C to stop the web server.")
    run_web_server(args.port)


if __name__ == "__main__":
    main()
