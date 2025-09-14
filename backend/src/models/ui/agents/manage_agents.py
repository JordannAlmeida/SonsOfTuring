from pydantic import BaseModel
from dataclasses import dataclass

@dataclass
class GetAllAgentsResponse:
    name: str