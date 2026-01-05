from .tools_entity import ToolsEntity
from typing import Optional

class AgentEntity:
    
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        model: int,
        tools: list[ToolsEntity],
        reasoning: bool,
        type_model: str,
        output_parser: Optional[str] = None,
        instructions: Optional[str] = None,
        has_storage: bool = False,
        knowledge_collection_name: Optional[str] = None,
        knowledge_description: Optional[str] = None,
        knowledge_top_k: Optional[int] = 5,
        created_at=None,
        updated_at=None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.model = model
        self.type_model = type_model
        self.tools = tools
        self.reasoning = reasoning
        self.output_parser = output_parser
        self.instructions = instructions
        self.has_storage = has_storage
        self.knowledge_collection_name = knowledge_collection_name
        self.knowledge_description = knowledge_description
        self.knowledge_top_k = knowledge_top_k
        self.created_at = created_at
        self.updated_at = updated_at

class AgentResumeEntity:

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name