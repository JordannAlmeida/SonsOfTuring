from pydantic import BaseModel
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from models.dto.agents.agentLLM import ModelLLM

class GetAllAgentsResponse(BaseModel):
    id: int
    name: str

class GetAgentByIdResponse(BaseModel):
    id: int
    name: str
    description: str
    model: int
    tools: list[dict]
    reasoning: bool
    type_model: str
    output_parser: Optional[str] = None
    instructions: Optional[str] = None
    has_storage: bool = False
    knowledge_collection_name: Optional[str] = None
    knowledge_description: Optional[str] = None
    knowledge_top_k: Optional[int] = 5

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class ExecuteAgentRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    session_id: Optional[str] = None

class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    model: int = Field(..., ge=1, le=7)
    tools: list[int] = Field(default_factory=list)
    reasoning: bool = Field(default=False)
    type_model: str = Field(..., min_length=1, max_length=255)
    output_parser: Optional[str] = Field(default=None, max_length=255)
    instructions: Optional[str] = Field(default=None)
    has_storage: bool = Field(default=False)
    knowledge_collection_name: Optional[str] = Field(default=None, max_length=255)
    knowledge_description: Optional[str] = Field(default=None)
    knowledge_top_k: Optional[int] = Field(default=5, ge=1)

    @field_validator('model')
    @classmethod
    def validate_model(cls, value: int) -> int:
        try:
            ModelLLM.get_from_int(value)
        except ValueError:
            valid_values = [model.value for model in ModelLLM]
            raise ValueError(f"model must be a valid ModelLLM value. Valid values: {valid_values}")
        return value
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be empty or contain only whitespace")
        return value.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("description cannot be empty or contain only whitespace")
        return value.strip()
    
    @field_validator('type_model')
    @classmethod
    def validate_type_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("type_model cannot be empty or contain only whitespace")
        return value.strip()
    
    @field_validator('tools')
    @classmethod
    def validate_tools(cls, value: list[int]) -> list[int]:
        if value and any(tool_id <= 0 for tool_id in value):
            raise ValueError("all tool IDs must be positive integers")
        if len(value) != len(set(value)):
            raise ValueError("tools list cannot contain duplicate IDs")
        return value

class CreateAgentResponse(BaseModel):
    id: int
    name: str
    description: str
    model: int
    tools: list[int]
    reasoning: bool
    type_model: str
    output_parser: Optional[str] = None
    instructions: Optional[str] = None
    has_storage: bool = False
    knowledge_collection_name: Optional[str] = None
    knowledge_description: Optional[str] = None
    knowledge_top_k: Optional[int] = 5

class UpdateAgentRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    model: Optional[int] = Field(None, ge=1, le=7)
    tools: Optional[list[int]] = Field(None)
    reasoning: Optional[bool] = None
    type_model: Optional[str] = Field(None, min_length=1, max_length=255)
    output_parser: Optional[str] = Field(None, max_length=255)
    instructions: Optional[str] = Field(None)
    has_storage: Optional[bool] = None
    knowledge_collection_name: Optional[str] = Field(None, max_length=255)
    knowledge_description: Optional[str] = Field(None)
    knowledge_top_k: Optional[int] = Field(None, ge=1)

    @field_validator('model')
    @classmethod
    def validate_model(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        try:
            ModelLLM.get_from_int(value)
        except ValueError:
            valid_values = [model.value for model in ModelLLM]
            raise ValueError(f"model must be a valid ModelLLM value. Valid values: {valid_values}")
        return value
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("name cannot be empty or contain only whitespace")
        return value.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("description cannot be empty or contain only whitespace")
        return value.strip()
    
    @field_validator('type_model')
    @classmethod
    def validate_type_model(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("type_model cannot be empty or contain only whitespace")
        return value.strip()
    
    @field_validator('tools')
    @classmethod
    def validate_tools(cls, value: Optional[list[int]]) -> Optional[list[int]]:
        if value is None:
            return value
        if value and any(tool_id <= 0 for tool_id in value):
            raise ValueError("all tool IDs must be positive integers")
        if len(value) != len(set(value)):
            raise ValueError("tools list cannot contain duplicate IDs")
        return value

class UpdateAgentResponse(BaseModel):
    id: int
    name: str
    description: str
    model: int
    tools: list[int]
    reasoning: bool
    type_model: str
    output_parser: Optional[str] = None
    instructions: Optional[str] = None
    has_storage: bool = False
    knowledge_collection_name: Optional[str] = None
    knowledge_description: Optional[str] = None
    knowledge_top_k: Optional[int] = 5