# Project 4: SQL Agent with Tool Use (Laboratory Experiment 4)

A complete ReAct (Reasoning + Action + Observation) database agent framework equipped with specialized database tools (`list_tables`, `get_schema`, `execute_query`, `validate_sql`, `get_sample_rows`, `calculate_data_summary`), unit test suite, automated benchmark evaluation, and a rare dark glassmorphic Visual Web Studio.

## Quick Start (Run Command)

Execute the full system with a single command:

```bash
python main.py
```

### Options:
- `python main.py` : Seeds database schemas, executes unit tests, runs evaluation benchmark, and launches the Visual Studio UI at `http://localhost:8080`.
- `python main.py --cli` : Runs unit tests and evaluation suite in CLI validation mode without opening the web server.
- `python main.py --port 9090` : Runs web studio on a custom port.

## ReAct Architecture

```
User Question ──► ReAct Loop ──► Thought: Reason next step
                                        │
                                        ▼
                                 Action: Call Tool
               (list_tables / get_schema / execute_query / validate_sql)
                                        │
                                        ▼
                               Observation: DB Output
                                        │
                                        ▼
                                 Final Answer & Charts
```

- **Database Engine (`db/`)**: Seeds relational SQLite databases (`ecommerce.db`, `hr.db`, `university.db`).
- **Tool Registry (`tools/`)**: Implements database tools with structured input schemas.
- **ReAct Agent (`agent/`)**: ReAct loop parser and reasoning engine supporting offline intelligence and online LLM APIs.
- **Evaluation (`evaluation/`)**: Automated benchmark dataset measuring step efficiency and execution accuracy.
- **Visual Studio (`web/`)**: High-end dark glassmorphic web dashboard with interactive ReAct trajectory visualizer, tool sandbox, ERD schema browser, and auto-generated data charts.
