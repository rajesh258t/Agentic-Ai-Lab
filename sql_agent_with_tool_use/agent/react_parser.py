import re
import json
from typing import Any, Dict, Optional, Tuple

class ReActStep:
    def __init__(self, step_number: int, thought: str, action_name: Optional[str] = None, action_input: Optional[Any] = None, observation: Optional[Any] = None, is_final: bool = False, final_answer: Optional[str] = None):
        self.step_number = step_number
        self.thought = thought
        self.action_name = action_name
        self.action_input = action_input
        self.observation = observation
        self.is_final = is_final
        self.final_answer = final_answer

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "thought": self.thought,
            "action_name": self.action_name,
            "action_input": self.action_input,
            "observation": self.observation,
            "is_final": self.is_final,
            "final_answer": self.final_answer
        }


class ReActParser:
    @staticmethod
    def parse_llm_output(text: str, step_number: int) -> ReActStep:
        clean_text = text.strip()

        # Check for Final Answer pattern
        final_answer_match = re.search(r"Final\s*Answer\s*:\s*(.*)", clean_text, re.IGNORECASE | re.DOTALL)
        if final_answer_match:
            final_ans = final_answer_match.group(1).strip()
            # Extract Thought before Final Answer if present
            thought_match = re.search(r"Thought\s*:\s*(.*?)(?=Final\s*Answer|$)", clean_text, re.IGNORECASE | re.DOTALL)
            thought = thought_match.group(1).strip() if thought_match else "Formulated final response based on tool observations."
            return ReActStep(
                step_number=step_number,
                thought=thought,
                is_final=True,
                final_answer=final_ans
            )

        # Parse Thought
        thought_match = re.search(r"Thought\s*:\s*(.*?)(?=Action\s*:|$)", clean_text, re.IGNORECASE | re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else clean_text

        # Parse Action
        action_match = re.search(r"Action\s*:\s*([a-zA-Z0-9_\-]+)", clean_text, re.IGNORECASE)
        action_name = action_match.group(1).strip() if action_match else None

        # Parse Action Input
        input_match = re.search(r"Action\s*Input\s*:\s*(.*)", clean_text, re.IGNORECASE | re.DOTALL)
        raw_input = input_match.group(1).strip() if input_match else ""

        parsed_input = ReActParser._parse_action_input(raw_input)

        if not action_name:
            # Fallback if model format was slightly malformed
            if "list_tables" in clean_text.lower():
                action_name = "list_tables"
                parsed_input = {}
            elif "get_schema" in clean_text.lower():
                action_name = "get_schema"
                parsed_input = {}

        return ReActStep(
            step_number=step_number,
            thought=thought,
            action_name=action_name,
            action_input=parsed_input,
            is_final=False
        )

    @staticmethod
    def _parse_action_input(raw_input: str) -> Any:
        if not raw_input:
            return {}

        raw_input = raw_input.strip()

        # Check if JSON code block or JSON string
        if raw_input.startswith("```json"):
            raw_input = re.sub(r"^```json\s*", "", raw_input)
            raw_input = re.sub(r"\s*```$", "", raw_input)
        elif raw_input.startswith("```"):
            raw_input = re.sub(r"^```\s*", "", raw_input)
            raw_input = re.sub(r"\s*```$", "", raw_input)

        if raw_input.startswith("{") and raw_input.endswith("}"):
            try:
                return json.loads(raw_input)
            except Exception:
                pass

        # Try key=value string parsing or key: value
        if ":" in raw_input and "{" not in raw_input:
            kv_dict = {}
            lines = raw_input.split("\n")
            for line in lines:
                if ":" in line:
                    k, v = line.split(":", 1)
                    kv_dict[k.strip().lower().replace(" ", "_")] = v.strip().strip('"\'')
            if kv_dict:
                return kv_dict

        # Single string value fallback
        return raw_input.strip('"\'')
