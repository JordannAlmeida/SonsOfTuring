from models.entity.tools_entity import ToolsEntity
from config.database.postgres_manager import postgres_manager
from models.entity.agent_entity import AgentEntity, AgentResumeEntity

from abc import ABC, abstractmethod


class IAgentsRepository(ABC):
    @abstractmethod
    async def get_all_agents(self, name_part: str, skip: int, limit: int) -> list[AgentResumeEntity]:
        pass
    @abstractmethod
    async def get_agent_by_id(self, agent_id: int) -> AgentEntity | None:
        pass
    @abstractmethod
    async def create_agent(self, name: str, description: str, model: int, tools: list[int], reasoning: bool, type_model: str, output_parser: str | None) -> AgentEntity:
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
            a.id, a.name, a.description, a.llm as model, a.reasoning, a.type_model, a.output_parser,
            t.id AS tool_id, t.name AS tool_name, t.description AS tool_description, t.function_caller,
            a.created_at, a.updated_at
            FROM agents a
            LEFT JOIN agents_tools at ON a.id = at.agent_id
            LEFT JOIN tools t ON at.tool_id = t.id
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
                        type_model=first_row['type_model'],
                        output_parser=first_row['output_parser'],
                        created_at=first_row['created_at'],
                        updated_at=first_row['updated_at']
                    )
        return None

    async def create_agent(self, name: str, description: str, model: int, tools: list[int], reasoning: bool, type_model: str, output_parser: str | None) -> AgentEntity:
        insert_agent_query = """
            INSERT INTO agents (name, description, llm, reasoning, type_model, output_parser)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, name, description, llm as model, reasoning, type_model, output_parser, created_at, updated_at
        """
        agent_params = [name, description, model, reasoning, type_model, output_parser]

        async with postgres_manager.get_connection() as connection:
            async with connection.transaction():
                agent_row = await connection.fetchrow(insert_agent_query, *agent_params)
                
                agent_id = agent_row['id']
                
                if tools:
                    insert_tools_query = """
                        INSERT INTO agents_tools (agent_id, tool_id)
                        VALUES ($1, $2)
                    """
                    for tool_id in tools:
                        await connection.execute(insert_tools_query, agent_id, tool_id)
                
                tools_query = """
                    SELECT t.id, t.name, t.description, t.function_caller
                    FROM tools t
                    INNER JOIN agents_tools at ON at.tool_id = t.id
                    WHERE at.agent_id = $1
                """
                tools_rows = await connection.fetch(tools_query, agent_id)
                
                tools_entities = [
                    ToolsEntity(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        function_caller=row['function_caller']
                    )
                    for row in tools_rows
                ]
                
                return AgentEntity(
                    id=agent_row['id'],
                    name=agent_row['name'],
                    description=agent_row['description'],
                    model=agent_row['model'],
                    tools=tools_entities,
                    reasoning=agent_row['reasoning'],
                    type_model=agent_row['type_model'],
                    output_parser=agent_row['output_parser'],
                    created_at=agent_row['created_at'],
                    updated_at=agent_row['updated_at']
                )