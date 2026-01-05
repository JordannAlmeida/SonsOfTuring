from agno.agent.agent import Agent
from agno.models.base import Model
from agno.models.google import Gemini
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.models.xai import xAI
from agno.models.deepseek import DeepSeek
from agno.models.groq import Groq
from agno.models.ollama import Ollama
from agno.tools.toolkit import Toolkit
from agno.tools.function import Function
from agno.db.redis import RedisDb
from config.database.qdrant_manager import qdrant_manager
from agno.knowledge.knowledge import Knowledge
from agno.guardrails import PIIDetectionGuardrail
from agno.guardrails import PromptInjectionGuardrail
import logging

from models.dto.agents.agentLLM import AgentFactoryInput, ModelLLM
from typing import Optional, Union, Dict, List, Callable

logger = logging.getLogger("FactoryAgent")

class FactoryAgent:

    @staticmethod
    def build_agent(agent_factory_input: AgentFactoryInput) -> Agent:
        model: Model
        if agent_factory_input.modelLLM == ModelLLM.GEMINI:
            model = Gemini(agent_factory_input.typeModel)
        elif agent_factory_input.modelLLM == ModelLLM.CLAUDE:
            model = Claude(agent_factory_input.typeModel)
        elif agent_factory_input.modelLLM == ModelLLM.OPEANAI:
            model = OpenAIChat(agent_factory_input.typeModel)
        elif agent_factory_input.modelLLM == ModelLLM.XAI:
            model = xAI(agent_factory_input.typeModel)
        elif agent_factory_input.modelLLM == ModelLLM.OLLAMA:
            model = Ollama(agent_factory_input.typeModel)
        elif agent_factory_input.modelLLM == ModelLLM.GROQ:
            model = Groq(agent_factory_input.typeModel)
        elif agent_factory_input.modelLLM == ModelLLM.DEEPSEEK:
            model = DeepSeek(agent_factory_input.typeModel)
        else:
            raise ValueError("Model LLM wasn't defined")
        
        agent = Agent(
            model=model,
            name=agent_factory_input.name,
            tools=FactoryAgent._build_tools(agent_factory_input.tools),
            reasoning=agent_factory_input.reasoning,
            description=agent_factory_input.description,
            instructions=agent_factory_input.instructions,
            tool_call_limit=5,
        )

        agent = FactoryAgent._build_db_storage(agent, agent_factory_input)
        agent = FactoryAgent._build_guard_rails(agent)
        return agent
    
    @staticmethod
    def _build_knowledge(agent: Agent, agent_factory_input: AgentFactoryInput) -> Agent:
        if not agent_factory_input.knowledge_collection_name:
            return agent
        vector_db = qdrant_manager.get_vector_db()
        vector_db.collection = agent_factory_input.knowledge_collection_name
        knowledge = Knowledge(
            vector_db=vector_db,
            description=agent_factory_input.knowledge_description or "",
            max_results=agent_factory_input.knowledge_top_k or 5,
            name=f"{agent.name}_knowledge",
        )
        agent.knowledge = knowledge
        return agent
    
    @staticmethod
    def _build_guard_rails(agent: Agent) -> Agent:
        agent.pre_hooks = [PromptInjectionGuardrail(), PIIDetectionGuardrail()]
        return agent

    @staticmethod
    def _build_db_storage(agent: Agent, agent_factory_input: AgentFactoryInput) -> Agent:
        if agent_factory_input.has_storage:
            try:
                from config.database.redis_manager import redis_manager
                db = RedisDb(
                    agent_name=agent.name,
                    redis_client=redis_manager.get_redis_client()
                )
                agent.db = db
                agent.enable_agentic_memory = True
                agent.add_history_to_context = True
                agent.num_history_sessions = 5
            except Exception as e:
                logger.error(f"Error initializing Redis DB for agent {agent.name}: {e}")
        return agent

    @staticmethod
    def _build_tools(tools: Optional[list[int]]) -> Optional[List[Union[Toolkit, Callable, Function, Dict]]]:
        if not tools:
            return None
        
        #TODO: Add logic recovery tools
        return []