from backend.src.models.entity.tools_entity import ToolsEntity
from ..config.database.postgres_manager import postgres_manager
from ..models.entity.agent_entity import AgentEntity, AgentResumeEntity

from abc import ABC, abstractmethod


class IAgentsRepository(ABC):
    @abstractmethod
    async def get_all_agents(self, name_part: str, skip: int, limit: int) -> list[AgentResumeEntity]:
        pass
    @abstractmethod
    async def get_agent_by_id(self, agent_id: int) -> AgentEntity | None:
        pass


class AgentsRepository(IAgentsRepository):
    
    def __init__(self):
        pass

    async def get_all_agents(self, name_part: str, skip: int, limit: int) -> list[AgentResumeEntity]:
        query = "SELECT id, name FROM agents"
        params = []

        if name_part:
            query += " WHERE name ILIKE $1 OFFSET $2 LIMIT $3"
            params = [f"%{name_part}%", skip, limit]
        else:
            query += " OFFSET $1 LIMIT $2"
            params = [skip, limit]

        agents: list[AgentResumeEntity] = []
        async with postgres_manager.get_connection() as connection:
            async with connection.transaction():
                async for row in connection.cursor(query, *params):
                    agents.append(AgentResumeEntity(id=row['id'], name=row['name']))
        return agents
    
    async def get_agent_by_id(self, agent_id: int) -> AgentEntity | None:
        query = """
            SELECT 
            a.id, a.name, a.description, a.model, a.reasoning, a.type_model,
            t.id AS tool_id, t.name AS tool_name, t.description AS tool_description
            FROM agents a
            LEFT JOIN unnest(a.tools) AS tool_id ON TRUE
            LEFT JOIN tools t ON t.id = tool_id
            WHERE a.id = $1
        """
        params = [agent_id]
        async with postgres_manager.get_connection() as connection:
            async with connection.transaction():
                rows = await connection.fetch(query, *params)
                if rows:
                    first_row = rows[0]
                    tools_entities = []
                    for row in rows:
                        if row['tool_id'] is not None:
                            tools_entities.append(
                                ToolsEntity(
                                    id=row['tool_id'],
                                    name=row['tool_name'],
                                    description=row['tool_description'],
                                    function_caller=row['function_caller']
                                )
                            )
                        return AgentEntity(
                            id=first_row['id'],
                            name=first_row['name'],
                            description=first_row['description'],
                            model=first_row['model'],
                            tools=tools_entities,
                            reasoning=first_row['reasoning'],
                            type_model=first_row['type_model']
                        )
        return None