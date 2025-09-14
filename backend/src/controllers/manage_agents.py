from fastapi import APIRouter, Depends
from ..config.database.postgres_manager import get_db_connection
from asyncpg import Connection
from ..services.manager_agents import ManagerAgentsService
from typing import List
from ..models.ui.agents.manage_agents import GetAllAgentsResponse

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

async def get_manage_agents_service(db_connection: Connection = Depends(get_db_connection)) -> ManagerAgentsService:
    return ManagerAgentsService(db_connection)

@router.get("/", response_model=List[GetAllAgentsResponse])
async def get_all_agents(
    name_part: str,
    skip: int = 0,
    limit: int = 100
):
    #TODO: call service method to list all agents
    return None