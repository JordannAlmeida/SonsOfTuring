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
    


class AgentFactoryInput(BaseModel):
    id: int | None = None
    name: str
    description: str
    modelLLM: ModelLLM
    typeModel: str
    tools: Optional[list[int]]
    reasoning: bool = False
    instructions: Optional[str] = None
    output_parser: Optional[str] = None
    has_storage: bool = False
    knowledge_collection_name: Optional[str] = None
    knowledge_description: Optional[str] = None
    knowledge_top_k: Optional[int] = 5

    @classmethod
    def from_dict(cls, data: dict):
        if isinstance(data.get("modelLLM"), (int, str)):
            data["modelLLM"] = ModelLLM[data["modelLLM"]] if isinstance(data["modelLLM"], str) else ModelLLM(data["modelLLM"])
        return cls(**data)
    
class AgentExecuteOutput(BaseModel):
    response: str
    session_id: str
    content_type: str