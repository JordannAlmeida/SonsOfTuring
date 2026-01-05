from models.entity.tools_entity import ToolsEntity
from config.database.postgres_manager import postgres_manager
from models.entity.agent_entity import AgentEntity, AgentResumeEntity
from typing import Optional

from abc import ABC, abstractmethod

class IAgentsRepository(ABC):
    @abstractmethod
    async def get_all_agents(self, name_part: str, skip: int, limit: int) -> list[AgentResumeEntity]:
        pass
    @abstractmethod
    async def get_agent_by_id(self, agent_id: int) -> AgentEntity | None:
        pass
    @abstractmethod
    async def create_agent(
        self,
        name: str,
        description: str,
        model: int,
        tools: list[int],
        reasoning: bool,
        type_model: str,
        output_parser: Optional[str] = None,
        instructions: Optional[str] = None,
        has_storage: bool = False,
        knowledge_collection_name: Optional[str] = None,
        knowledge_description: Optional[str] = None,
        knowledge_top_k: Optional[int] = 5
    ) -> AgentEntity:
        pass
    @abstractmethod
    async def update_agent(
        self,
        agent_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        model: Optional[int] = None,
        tools: Optional[list[int]] = None,
        reasoning: Optional[bool] = None,
        type_model: Optional[str] = None,
        output_parser: Optional[str] = None,
        instructions: Optional[str] = None,
        has_storage: Optional[bool] = None,
        knowledge_collection_name: Optional[str] = None,
        knowledge_description: Optional[str] = None,
        knowledge_top_k: Optional[int] = None
    ) -> AgentEntity | None:
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
            a.instructions, a.has_storage, a.knowledge_collection_name, a.knowledge_description, a.knowledge_top_k,
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
                        instructions=first_row['instructions'],
                        has_storage=first_row['has_storage'],
                        knowledge_collection_name=first_row['knowledge_collection_name'],
                        knowledge_description=first_row['knowledge_description'],
                        knowledge_top_k=first_row['knowledge_top_k'],
                        created_at=first_row['created_at'],
                        updated_at=first_row['updated_at']
                    )
        return None

    async def create_agent(
        self,
        name: str,
        description: str,
        model: int,
        tools: list[int],
        reasoning: bool,
        type_model: str,
        output_parser: Optional[str] = None,
        instructions: Optional[str] = None,
        has_storage: bool = False,
        knowledge_collection_name: Optional[str] = None,
        knowledge_description: Optional[str] = None,
        knowledge_top_k: Optional[int] = 5
    ) -> AgentEntity:
        insert_agent_query = """
            INSERT INTO agents (name, description, llm, reasoning, type_model, output_parser, instructions, has_storage, knowledge_collection_name, knowledge_description, knowledge_top_k)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING id, name, description, llm as model, reasoning, type_model, output_parser, instructions, has_storage, knowledge_collection_name, knowledge_description, knowledge_top_k, created_at, updated_at
        """
        agent_params = [name, description, model, reasoning, type_model, output_parser, instructions, has_storage, knowledge_collection_name, knowledge_description, knowledge_top_k]

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
                    instructions=agent_row['instructions'],
                    has_storage=agent_row['has_storage'],
                    knowledge_collection_name=agent_row['knowledge_collection_name'],
                    knowledge_description=agent_row['knowledge_description'],
                    knowledge_top_k=agent_row['knowledge_top_k'],
                    created_at=agent_row['created_at'],
                    updated_at=agent_row['updated_at']
                )

    async def update_agent(
        self,
        agent_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        model: Optional[int] = None,
        tools: Optional[list[int]] = None,
        reasoning: Optional[bool] = None,
        type_model: Optional[str] = None,
        output_parser: Optional[str] = None,
        instructions: Optional[str] = None,
        has_storage: Optional[bool] = None,
        knowledge_collection_name: Optional[str] = None,
        knowledge_description: Optional[str] = None,
        knowledge_top_k: Optional[int] = None
    ) -> AgentEntity | None:
        agent_entity = await self.get_agent_by_id(agent_id)
        if agent_entity is None:
            return None

        updates = {}
        params = []
        param_index = 1

        if name is not None:
            updates['name'] = f"${param_index}"
            params.append(name)
            param_index += 1
        if description is not None:
            updates['description'] = f"${param_index}"
            params.append(description)
            param_index += 1
        if model is not None:
            updates['llm'] = f"${param_index}"
            params.append(model)
            param_index += 1
        if reasoning is not None:
            updates['reasoning'] = f"${param_index}"
            params.append(reasoning)
            param_index += 1
        if type_model is not None:
            updates['type_model'] = f"${param_index}"
            params.append(type_model)
            param_index += 1
        if output_parser is not None:
            updates['output_parser'] = f"${param_index}"
            params.append(output_parser)
            param_index += 1
        if instructions is not None:
            updates['instructions'] = f"${param_index}"
            params.append(instructions)
            param_index += 1
        if has_storage is not None:
            updates['has_storage'] = f"${param_index}"
            params.append(has_storage)
            param_index += 1
        if knowledge_collection_name is not None:
            updates['knowledge_collection_name'] = f"${param_index}"
            params.append(knowledge_collection_name)
            param_index += 1
        if knowledge_description is not None:
            updates['knowledge_description'] = f"${param_index}"
            params.append(knowledge_description)
            param_index += 1
        if knowledge_top_k is not None:
            updates['knowledge_top_k'] = f"${param_index}"
            params.append(knowledge_top_k)
            param_index += 1

        if not updates and tools is None:
            return agent_entity

        async with postgres_manager.get_connection() as connection:
            async with connection.transaction():
                if updates:
                    set_clause = ", ".join([f"{key} = {value}" for key, value in updates.items()])
                    params.append(agent_id)
                    update_query = f"""
                        UPDATE agents
                        SET {set_clause}
                        WHERE id = ${param_index}
                        RETURNING id, name, description, llm as model, reasoning, type_model, output_parser, instructions, has_storage, knowledge_collection_name, knowledge_description, knowledge_top_k, created_at, updated_at
                    """
                    agent_row = await connection.fetchrow(update_query, *params)
                else:
                    agent_row = await connection.fetchrow(
                        "SELECT id, name, description, llm as model, reasoning, type_model, output_parser, instructions, has_storage, knowledge_collection_name, knowledge_description, knowledge_top_k, created_at, updated_at FROM agents WHERE id = $1",
                        agent_id
                    )

                if tools is not None:
                    await connection.execute("DELETE FROM agents_tools WHERE agent_id = $1", agent_id)
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
                    instructions=agent_row['instructions'],
                    has_storage=agent_row['has_storage'],
                    knowledge_collection_name=agent_row['knowledge_collection_name'],
                    knowledge_description=agent_row['knowledge_description'],
                    knowledge_top_k=agent_row['knowledge_top_k'],
                    created_at=agent_row['created_at'],
                    updated_at=agent_row['updated_at']
                )