from .tools_entity import ToolsEntity

class AgentEntity:
    
    def __init__(self, id: int, name: str, description: str, model: int, tools: list[ToolsEntity], reasoning: bool, type_model: str):
        self.id = id
        self.name = name
        self.description = description
        self.model = model
        self.tools = tools
        self.reasoning = reasoning  
        self.type_model = type_model

class AgentResumeEntity:

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name