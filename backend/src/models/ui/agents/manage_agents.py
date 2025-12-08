from pydantic import BaseModel

class GetAllAgentsResponse(BaseModel):
    name: str

class GetAgentByIdResponse(BaseModel):
    id: int
    name: str
    description: str
    model: str
    tools: list[dict]
    reasoning: bool
    type_model: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)