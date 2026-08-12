import unittest
import os
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.sample_db_builder import create_ecommerce_db, create_hr_db
from agent.react_parser import ReActParser
from agent.react_agent import ReActSQLAgent

class TestReActAgent(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.ecommerce_db = os.path.join(self.tmp_dir.name, "ecommerce.db")
        self.hr_db = os.path.join(self.tmp_dir.name, "hr.db")
        create_ecommerce_db(self.ecommerce_db)
        create_hr_db(self.hr_db)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_react_parser_action(self):
        text = """
        Thought: I need to check all tables in the database first.
        Action: list_tables
        Action Input: {}
        """
        step = ReActParser.parse_llm_output(text, 1)
        self.assertFalse(step.is_final)
        self.assertEqual(step.action_name, "list_tables")
        self.assertEqual(step.thought.strip(), "I need to check all tables in the database first.")

    def test_react_parser_final_answer(self):
        text = """
        Thought: I have retrieved the top customer from the database query.
        Final Answer: Customer Alice Smith spent the most with $1,499.49.
        """
        step = ReActParser.parse_llm_output(text, 2)
        self.assertTrue(step.is_final)
        self.assertIn("Alice Smith", step.final_answer)

    def test_react_agent_execution_ecommerce(self):
        agent = ReActSQLAgent(db_path=self.ecommerce_db)
        res = agent.run("Which customer has spent the highest total amount on orders?")
        self.assertTrue(res["solved"])
        self.assertGreater(res["total_steps"], 0)
        self.assertIsNotNone(res["final_answer"])

    def test_react_agent_execution_hr(self):
        agent = ReActSQLAgent(db_path=self.hr_db)
        res = agent.run("Which employee has the highest salary?")
        self.assertTrue(res["solved"])
        self.assertIn("Jane", res["final_answer"])

if __name__ == "__main__":
    unittest.main()
