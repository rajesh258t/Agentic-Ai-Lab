import http.server
import socketserver
import json
import urllib.parse
import os
import sys

# Ensure root in path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from db.sample_db_builder import initialize_all_databases
from tools.database_tools import get_default_tools
from agent.react_agent import ReActSQLAgent
from evaluation.evaluator import ReActAgentEvaluator

DATA_DIR = os.path.join(BASE_DIR, "data")
DB_MAP = initialize_all_databases(DATA_DIR)

STATIC_DIR = os.path.join(BASE_DIR, "web", "static")

class ReActStudioHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/databases":
            self._send_json({
                "success": True,
                "databases": list(DB_MAP.keys()),
                "data_dir": DATA_DIR
            })
            return

        elif path == "/api/tools":
            tools = get_default_tools()
            self._send_json({
                "success": True,
                "tools": [t.to_dict() for t in tools.values()]
            })
            return

        elif path == "/api/schema":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            db_name = query_params.get("db", ["ecommerce"])[0]
            db_path = DB_MAP.get(db_name, DB_MAP["ecommerce"])

            tool = get_default_tools()["get_schema"]
            res = tool.execute(db_path)
            self._send_json(res)
            return

        elif path == "/api/benchmark":
            evaluator = ReActAgentEvaluator(DATA_DIR)
            test_cases_file = os.path.join(BASE_DIR, "evaluation", "test_cases.json")
            res = evaluator.run_benchmark(test_cases_file)
            self._send_json({"success": True, "benchmark": res})
            return

        # Serve static files for everything else
        return super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8')
        try:
            data = json.loads(post_body) if post_body else {}
        except Exception:
            data = {}

        if path == "/api/query":
            question = data.get("question", "Which customer spent the highest amount?")
            db_name = data.get("database", "ecommerce")
            model_name = data.get("model", "offline-react-engine")
            api_key = data.get("api_key", "")

            db_path = DB_MAP.get(db_name, DB_MAP["ecommerce"])
            agent = ReActSQLAgent(db_path=db_path, max_iterations=10, llm_api_key=api_key, model_name=model_name)
            
            result = agent.run(question)
            self._send_json({"success": True, "agent_result": result})
            return

        elif path == "/api/tool/execute":
            tool_name = data.get("tool_name", "")
            db_name = data.get("database", "ecommerce")
            params = data.get("params", {})

            db_path = DB_MAP.get(db_name, DB_MAP["ecommerce"])
            tools = get_default_tools()

            if tool_name not in tools:
                self._send_json({"success": False, "error": f"Tool '{tool_name}' not found."})
                return

            tool = tools[tool_name]
            res = tool.execute(db_path, **params)
            self._send_json(res)
            return

        elif path == "/api/custom_sql":
            sql_query = data.get("sql_query", "")
            db_name = data.get("database", "ecommerce")

            db_path = DB_MAP.get(db_name, DB_MAP["ecommerce"])
            tool = get_default_tools()["execute_query"]
            res = tool.execute(db_path, sql_query=sql_query)
            self._send_json(res)
            return

        self.send_error(404, "Endpoint not found")

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Suppress routine GET log clutter
        pass


def run_web_server(port: int = 8080):
    handler = ReActStudioHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 ReAct SQL Agent Studio server running at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server...")
            httpd.server_close()


if __name__ == "__main__":
    run_web_server(8080)
