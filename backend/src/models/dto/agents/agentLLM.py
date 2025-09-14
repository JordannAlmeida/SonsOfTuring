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
    


@dataclass
class AgentFactoryInput(BaseModel):
    modelLLM: ModelLLM
    typeModel: str
    name: str
    tools: Optional[list[int]]
    reasoning: bool = False
    description: str