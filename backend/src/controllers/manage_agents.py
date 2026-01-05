from fastapi import APIRouter, Depends
from models.dto.agents.agentLLM import AgentExecuteOutput
from services.manager_agents import IManagerAgentsService, ManagerAgentsService
from repository.agents_repository import AgentsRepository, IAgentsRepository
from typing import List, Optional
from models.ui.agents.manage_agents import GetAllAgentsResponse, GetAgentByIdResponse, CreateAgentRequest, CreateAgentResponse, ExecuteAgentRequest, UpdateAgentRequest, UpdateAgentResponse
from models.ui.auth.auth_schemas import UserResponse
from dependencies.auth_dependency import get_current_user

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

async def get_manage_agents_service() -> IManagerAgentsService:
    repository: IAgentsRepository = AgentsRepository()
    return ManagerAgentsService(repository)

@router.get("/", response_model=List[GetAllAgentsResponse])
async def get_all_agents(
    name_part: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    service: IManagerAgentsService = Depends(get_manage_agents_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.get_all_agents(name_part, skip, limit)

@router.get("/{agent_id}", response_model=GetAgentByIdResponse)
async def get_agent_by_id(
    agent_id: int,
    service: IManagerAgentsService = Depends(get_manage_agents_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.get_agent_by_id(agent_id)



@router.post("/{agent_id}/execute", response_model=Optional[AgentExecuteOutput])
async def execute_agent_action(
    agent_id: int,
    request: ExecuteAgentRequest,
    service: IManagerAgentsService = Depends(get_manage_agents_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.execute_agent_action(agent_id, request.prompt, str(current_user.email), request.session_id) 

@router.post("/", response_model=CreateAgentResponse)
async def create_agent(
    request: CreateAgentRequest,
    service: IManagerAgentsService = Depends(get_manage_agents_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.create_agent(request)

@router.put("/{agent_id}", response_model=Optional[UpdateAgentResponse])
async def update_agent(
    agent_id: int,
    request: UpdateAgentRequest,
    service: IManagerAgentsService = Depends(get_manage_agents_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.update_agent(agent_id, request)