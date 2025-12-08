from pydantic import BaseModel
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ModelLLM(Enum):
    GEMINI = 1
    CLAUDE = 2
    OPEANAI = 3
    XAI = 4
    OLLAMA = 5
    GROQ = 6
    DEEPSEEK = 7

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_from_int(cls, value: int) -> 'ModelLLM':
        for model in cls:
            if model.value == value:
                return model
        raise ValueError(f"No ModelLLM with value {value}")
    


@dataclass
class AgentFactoryInput(BaseModel):
    modelLLM: ModelLLM
    typeModel: str
    name: str
    tools: Optional[list[int]]
    reasoning: bool = False
    description: str
    output_parser: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        if isinstance(data.get("modelLLM"), (int, str)):
            data["modelLLM"] = ModelLLM[data["modelLLM"]] if isinstance(data["modelLLM"], str) else ModelLLM(data["modelLLM"])
        return cls(**data)