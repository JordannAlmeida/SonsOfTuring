from .tools_entity import ToolsEntity

class AgentEntity:
    
    def __init__(self, id: int, name: str, description: str, model: int, tools: list[ToolsEntity], reasoning: bool, type_model: str, output_parser: str| None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.model = model
        self.type_model = type_model
        self.tools = tools
        self.reasoning = reasoning
        self.output_parser = output_parser
        self.created_at = created_at
        self.updated_at = updated_at

class AgentResumeEntity:

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name