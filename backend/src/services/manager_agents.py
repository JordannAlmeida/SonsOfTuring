from ..repository.agents_repository import IAgentsRepository
from ..models.ui.agents.manage_agents import GetAgentByIdResponse, GetAllAgentsResponse
from ..models.dto.agents.agentLLM import AgentFactoryInput, ModelLLM
import abc
from ..config.database.cache_manager import cache_manager
from ..core.agets.execute_agent import ExecuteAgent
from typing import Optional


class IManagerAgentsService(abc.ABC):
    @abc.abstractmethod
    async def get_all_agents(self, name_part: str, skip: int, limit: int):
        pass

class ManagerAgentsService(IManagerAgentsService):

    def __init__(self, agents_repository: IAgentsRepository):
        self.agents_repository = agents_repository
        self.cache = cache_manager

    async def get_all_agents(self, name_part: str, skip: int, limit: int):
        if (name_part is None):
            name_part = ""
        if (skip is None):
            skip = 0
        if (limit is None):
            limit = 100
        agents_resume_entity_list = await self.agents_repository.get_all_agents(name_part, skip, limit)
        agents_response: list[GetAllAgentsResponse] = list(map(lambda agent_resume_entity: GetAllAgentsResponse(name=agent_resume_entity.name), agents_resume_entity_list))
        return agents_response
    
    async def get_agent_by_id(self, agent_id: int):
        if self.cache.exists(f"get_agent_by_id:{agent_id}"):
            json_data = self.cache.get(f"get_agent_by_id:{agent_id}")
            return GetAgentByIdResponse(**json_data)

        agent_entity = await self.agents_repository.get_agent_by_id(agent_id)
        if agent_entity is None:
            return None
        tools_list = []
        for tool in agent_entity.tools:
            tools_list.append({
                "id": tool.id,
                "name": tool.name,
                "description": tool.description
            })
        agent_response = GetAgentByIdResponse(
            id=agent_entity.id,
            name=agent_entity.name,
            description=agent_entity.description,
            model=agent_entity.model,
            tools=tools_list,
            reasoning=agent_entity.reasoning,
            type_model=agent_entity.type_model
        )
        await self.cache.set(f"get_agent_by_id:{agent_id}", agent_response.model_dump(), ttl=300)
        return agent_response

    async def execute_agent_action(self, agent_id: int, prompt: str) -> Optional[str]:
        agent_factory_input = await self._recover_agent_factory_input(agent_id)
        if agent_factory_input is None:
            return None
        
        result = await ExecuteAgent.run_agent(agent_factory_input, prompt)
        return result

    async def _recover_agent_factory_input(self, agent_id: int) -> AgentFactoryInput | None:
        cached_data = self.cache.get(f"get_agent_by_id:{agent_id}")
        if cached_data:
            return AgentFactoryInput(**cached_data)

        agent_entity = await self.agents_repository.get_agent_by_id(agent_id)
        if agent_entity is None:
            return None
        agent_factory_input = AgentFactoryInput(
            modelLLM=ModelLLM.get_from_int(agent_entity.model),
            typeModel=agent_entity.type_model,
            name=agent_entity.name,
            tools=[tool.id for tool in agent_entity.tools],
            reasoning=agent_entity.reasoning,
            description=agent_entity.description
        )
        self.cache.set(f"get_agent_by_id:{agent_id}", agent_factory_input.model_dump(), ttl=300)
        return agent_factory_input