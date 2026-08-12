import os
import json
import sqlite3
from typing import Any, Dict, List
from agent.react_agent import ReActSQLAgent

class ReActAgentEvaluator:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def run_benchmark(self, test_cases_file: str) -> Dict[str, Any]:
        with open(test_cases_file, "r", encoding="utf-8") as f:
            test_cases = json.load(f)

        total_cases = len(test_cases)
        solved_count = 0
        total_steps = 0
        tool_call_counts = {}
        case_results = []

        for tc in test_cases:
            db_name = tc["database"]
            db_path = os.path.join(self.data_dir, f"{db_name}.db")
            question = tc["question"]

            agent = ReActSQLAgent(db_path=db_path, max_iterations=8)
            res = agent.run(question)

            is_solved = res.get("solved", False)
            steps = res.get("total_steps", 0)
            total_steps += steps

            if is_solved:
                solved_count += 1

            # Count tool usages
            for step in res.get("trajectory", []):
                act = step.get("action_name")
                if act:
                    tool_call_counts[act] = tool_call_counts.get(act, 0) + 1

            case_results.append({
                "id": tc["id"],
                "database": db_name,
                "question": question,
                "difficulty": tc.get("difficulty", "Medium"),
                "solved": is_solved,
                "steps_taken": steps,
                "final_answer": res.get("final_answer"),
                "trajectory": res.get("trajectory")
            })

        execution_accuracy_rate = round((solved_count / total_cases) * 100, 2) if total_cases > 0 else 0
        avg_steps_per_query = round(total_steps / total_cases, 2) if total_cases > 0 else 0

        return {
            "total_cases": total_cases,
            "solved_count": solved_count,
            "execution_accuracy_rate": execution_accuracy_rate,
            "average_steps_per_query": avg_steps_per_query,
            "tool_call_distribution": tool_call_counts,
            "results": case_results
        }
