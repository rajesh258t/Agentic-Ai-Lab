import unittest
import os
import tempfile
import sqlite3
import sys

# Ensure root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.sample_db_builder import create_ecommerce_db
from tools.database_tools import (
    ListTablesTool,
    GetSchemaTool,
    ExecuteQueryTool,
    ValidateSQLTool,
    SampleRowsTool,
    DataSummaryTool
)

class TestDatabaseTools(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_ecommerce.db")
        create_ecommerce_db(self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_list_tables_tool(self):
        tool = ListTablesTool()
        res = tool.execute(self.db_path)
        self.assertTrue(res["success"])
        tables = res["result"]["tables"]
        self.assertIn("customers", tables)
        self.assertIn("orders", tables)
        self.assertIn("products", tables)

    def test_get_schema_tool(self):
        tool = GetSchemaTool()
        res = tool.execute(self.db_path, table_name="customers")
        self.assertTrue(res["success"])
        tables = res["result"]["tables"]
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["table_name"], "customers")
        col_names = [c["name"] for c in tables[0]["columns"]]
        self.assertIn("customer_id", col_names)
        self.assertIn("email", col_names)

    def test_execute_query_tool_valid(self):
        tool = ExecuteQueryTool()
        res = tool.execute(self.db_path, sql_query="SELECT COUNT(*) AS total FROM customers;")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"]["row_count"], 1)
        self.assertEqual(res["result"]["rows"][0]["total"], 5)

    def test_execute_query_tool_security(self):
        tool = ExecuteQueryTool()
        res = tool.execute(self.db_path, sql_query="DROP TABLE customers;")
        self.assertFalse(res["success"])
        self.assertIn("Security Restriction", res["error"])

    def test_validate_sql_tool(self):
        tool = ValidateSQLTool()
        res = tool.execute(self.db_path, sql_query="SELECT name, email FROM customers WHERE country='USA';")
        self.assertTrue(res["success"])
        self.assertTrue(res["result"]["is_valid"])

    def test_sample_rows_tool(self):
        tool = SampleRowsTool()
        res = tool.execute(self.db_path, table_name="products", limit=2)
        self.assertTrue(res["success"])
        self.assertEqual(len(res["result"]["sample_rows"]), 2)

    def test_data_summary_tool(self):
        tool = DataSummaryTool()
        res = tool.execute(self.db_path, table_name="products")
        self.assertTrue(res["success"])
        summary = res["result"]["column_summaries"]
        self.assertIn("price", summary)
        self.assertIn("avg", summary["price"])

if __name__ == "__main__":
    unittest.main()
