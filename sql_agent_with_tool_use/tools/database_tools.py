import sqlite3
import time
from typing import Any, Dict, List, Optional
from tools.base_tool import BaseTool

class ListTablesTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="list_tables",
            description="Returns a list of all table names available in the target database schema.",
            parameters_schema={"type": "object", "properties": {}}
        )

    def execute(self, db_path: str, **kwargs) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return {
                "success": True,
                "tool": self.name,
                "result": {"tables": tables, "count": len(tables)},
                "error": None
            }
        except Exception as e:
            return {"success": False, "tool": self.name, "result": None, "error": str(e)}


class GetSchemaTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="get_schema",
            description="Retrieves the detailed SQL DDL schema, column definitions, data types, primary keys, and foreign keys for tables.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Optional table name. If omitted, returns schemas for all tables."
                    }
                }
            }
        )

    def execute(self, db_path: str, table_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            if table_name:
                cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                rows = cursor.fetchall()
            else:
                cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                rows = cursor.fetchall()

            if not rows:
                conn.close()
                return {"success": False, "tool": self.name, "result": None, "error": f"Table '{table_name}' not found in database."}

            schema_details = []
            for name, sql in rows:
                cursor.execute(f"PRAGMA table_info('{name}')")
                columns_raw = cursor.fetchall()
                columns = [
                    {"cid": c[0], "name": c[1], "type": c[2], "notnull": bool(c[3]), "default": c[4], "pk": bool(c[5])}
                    for c in columns_raw
                ]

                cursor.execute(f"PRAGMA foreign_key_list('{name}')")
                fk_raw = cursor.fetchall()
                foreign_keys = [
                    {"id": f[0], "from": f[3], "to_table": f[2], "to_column": f[4]}
                    for f in fk_raw
                ]

                schema_details.append({
                    "table_name": name,
                    "sql": sql,
                    "columns": columns,
                    "foreign_keys": foreign_keys
                })

            conn.close()
            return {
                "success": True,
                "tool": self.name,
                "result": {"tables": schema_details},
                "error": None
            }
        except Exception as e:
            return {"success": False, "tool": self.name, "result": None, "error": str(e)}


class ExecuteQueryTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="execute_query",
            description="Safely executes a read-only SQL SELECT query against the database and returns tabular row results.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "SQL SELECT statement to execute."
                    }
                },
                "required": ["sql_query"]
            }
        )

    def execute(self, db_path: str, sql_query: str = "", **kwargs) -> Dict[str, Any]:
        if not sql_query:
            sql_query = kwargs.get("query", kwargs.get("sql", ""))

        clean_sql = sql_query.strip()
        if not clean_sql.upper().startswith("SELECT") and not clean_sql.upper().startswith("WITH") and not clean_sql.upper().startswith("EXPLAIN"):
            return {
                "success": False,
                "tool": self.name,
                "result": None,
                "error": "Security Restriction: Only read-only SELECT queries are allowed."
            }

        start_time = time.time()
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(clean_sql)
            rows = cursor.fetchall()
            exec_time_ms = round((time.time() - start_time) * 1000, 2)

            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            data = [dict(row) for row in rows]
            conn.close()

            return {
                "success": True,
                "tool": self.name,
                "result": {
                    "columns": columns,
                    "rows": data,
                    "row_count": len(data),
                    "execution_time_ms": exec_time_ms
                },
                "error": None
            }
        except Exception as e:
            exec_time_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "tool": self.name,
                "result": None,
                "error": f"SQL Execution Error: {str(e)}",
                "execution_time_ms": exec_time_ms
            }


class ValidateSQLTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="validate_sql",
            description="Validates SQL syntax, checks table & column existence, and checks for dangerous SQL injection patterns.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "SQL statement to validate."
                    }
                },
                "required": ["sql_query"]
            }
        )

    def execute(self, db_path: str, sql_query: str = "", **kwargs) -> Dict[str, Any]:
        if not sql_query:
            sql_query = kwargs.get("query", kwargs.get("sql", ""))

        clean_sql = sql_query.strip()
        forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "GRANT"]
        tokens = [t.upper() for t in clean_sql.split()]
        
        for forbidden in forbidden_keywords:
            if forbidden in tokens:
                return {
                    "success": False,
                    "tool": self.name,
                    "result": {"is_valid": False, "reason": f"Forbidden DDL/DML keyword '{forbidden}' detected."},
                    "error": f"Forbidden operation '{forbidden}'."
                }

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"EXPLAIN QUERY PLAN {clean_sql}")
            plan = cursor.fetchall()
            conn.close()
            return {
                "success": True,
                "tool": self.name,
                "result": {
                    "is_valid": True,
                    "explanation": [f"Select step {p[0]}: {p[3]}" for p in plan]
                },
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "tool": self.name,
                "result": {"is_valid": False, "reason": str(e)},
                "error": str(e)
            }


class SampleRowsTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="get_sample_rows",
            description="Retrieves top sample rows (default limit 3) from a specific table to inspect example field formats.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Name of the target table."},
                    "limit": {"type": "integer", "description": "Number of sample rows to fetch (default 3)."}
                },
                "required": ["table_name"]
            }
        )

    def execute(self, db_path: str, table_name: str = "", limit: int = 3, **kwargs) -> Dict[str, Any]:
        if not table_name:
            table_name = kwargs.get("table", "")
        if not table_name:
            return {"success": False, "tool": self.name, "result": None, "error": "table_name parameter is required."}

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return {
                "success": True,
                "tool": self.name,
                "result": {"table_name": table_name, "sample_rows": rows, "count": len(rows)},
                "error": None
            }
        except Exception as e:
            return {"success": False, "tool": self.name, "result": None, "error": str(e)}


class DataSummaryTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="calculate_data_summary",
            description="Computes statistical metrics (min, max, average, null count, distinct count) for table columns.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Name of the target table."}
                },
                "required": ["table_name"]
            }
        )

    def execute(self, db_path: str, table_name: str = "", **kwargs) -> Dict[str, Any]:
        if not table_name:
            table_name = kwargs.get("table", "")
        if not table_name:
            return {"success": False, "tool": self.name, "result": None, "error": "table_name parameter is required."}

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            cols = cursor.fetchall()
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]

            summary = {}
            for col in cols:
                col_name = col[1]
                col_type = col[2].upper()

                cursor.execute(f"SELECT COUNT(DISTINCT {col_name}), COUNT(*) - COUNT({col_name}) FROM {table_name}")
                distinct_cnt, null_cnt = cursor.fetchone()

                stats = {"type": col_type, "distinct_count": distinct_cnt, "null_count": null_cnt}

                if any(t in col_type for t in ["INT", "REAL", "NUMERIC", "FLOAT", "DOUBLE"]):
                    cursor.execute(f"SELECT MIN({col_name}), MAX({col_name}), AVG({col_name}) FROM {table_name}")
                    min_v, max_v, avg_v = cursor.fetchone()
                    stats["min"] = min_v
                    stats["max"] = max_v
                    stats["avg"] = round(avg_v, 2) if avg_v is not None else None

                summary[col_name] = stats

            conn.close()
            return {
                "success": True,
                "tool": self.name,
                "result": {"table_name": table_name, "total_rows": total_rows, "column_summaries": summary},
                "error": None
            }
        except Exception as e:
            return {"success": False, "tool": self.name, "result": None, "error": str(e)}


def get_default_tools() -> Dict[str, BaseTool]:
    tools = [
        ListTablesTool(),
        GetSchemaTool(),
        ExecuteQueryTool(),
        ValidateSQLTool(),
        SampleRowsTool(),
        DataSummaryTool()
    ]
    return {t.name: t for t in tools}
