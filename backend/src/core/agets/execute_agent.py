from datetime import datetime, timedelta
from .factory_agent import FactoryAgent
from agno.agent import Agent, RunOutput
from models.dto.agents.agentLLM import AgentFactoryInput, AgentExecuteOutput
from uuid import uuid4
from typing import Optional

class ExecuteAgent:

    #TODO: verify content type case is not a string
    @staticmethod
    async def run_agent(agent: AgentFactoryInput, user_input: str, session_id: Optional[str], user_id: str, prune_memory: bool = True) -> AgentExecuteOutput:
        if session_id is None:
            session_id = str(uuid4())
        agent_instance: Agent = FactoryAgent.build_agent(agent)
        if prune_memory:
            ExecuteAgent._prune_old_memories(agent_instance.db, user_id)

        response: RunOutput = await agent_instance.arun(
            user_input,
            session_id=session_id,
            user_id=user_id
        )
        agentExecuteOutput = AgentExecuteOutput(
            response=response.content,
            session_id=session_id,
            content_type=response.content_type
        )
        return agentExecuteOutput
    
    @staticmethod
    def _prune_old_memories(db, user_id, days=30):
        """Remove memories older than 30 days"""
        cutoff_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        memories = db.get_user_memories(user_id=user_id)
        for memory in memories:
            if memory.updated_at and memory.updated_at < cutoff_timestamp:
                db.delete_user_memory(memory_id=memory.memory_id)