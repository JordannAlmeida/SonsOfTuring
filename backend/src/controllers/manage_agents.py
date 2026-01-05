from fastapi import APIRouter, Depends
from models.dto.agents.agentLLM import AgentExecuteOutput
from services.manager_agents import ManagerAgentsService
from repository.agents_repository import AgentsRepository
from typing import List, Optional
from models.ui.agents.manage_agents import GetAllAgentsResponse, GetAgentByIdResponse, CreateAgentRequest, CreateAgentResponse, ExecuteAgentRequest

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

async def get_manage_agents_service() -> ManagerAgentsService:
    repository = AgentsRepository()
    return ManagerAgentsService(repository)

@router.get("/", response_model=List[GetAllAgentsResponse])
async def get_all_agents(
    name_part: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    service: ManagerAgentsService = Depends(get_manage_agents_service)
):
    return await service.get_all_agents(name_part, skip, limit)

@router.get("/{agent_id}", response_model=GetAgentByIdResponse)
async def get_agent_by_id(
    agent_id: int,
    service: ManagerAgentsService = Depends(get_manage_agents_service)
):
    return await service.get_agent_by_id(agent_id)



@router.post("/{agent_id}/execute", response_model=Optional[AgentExecuteOutput])
async def execute_agent_action(
    agent_id: int,
    request: ExecuteAgentRequest,
    service: ManagerAgentsService = Depends(get_manage_agents_service)
):
    #TODO: pass user_id from header or token
    return await service.execute_agent_action(agent_id, request.prompt, "", request.session_id) 

@router.post("/", response_model=CreateAgentResponse)
async def create_agent(
    request: CreateAgentRequest,
    service: ManagerAgentsService = Depends(get_manage_agents_service)
):
    return await service.create_agent(request)