from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    def __init__(self, name: str, description: str, parameters_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema

    @abstractmethod
    def execute(self, db_path: str, **kwargs) -> Dict[str, Any]:
        """
        Executes the tool logic against the database at db_path.
        Returns a standard response dictionary with status, result, and metadata.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema
        }
