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

from ...models.dto.agents.agentLLM import AgentFactoryInput, ModelLLM
from typing import Optional, Union, Dict, List, Callable

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
        
        return Agent(
            model=model,
            name=agent_factory_input.name,
            tools=FactoryAgent._build_tools(agent_factory_input.tools),
            reasoning=agent_factory_input.reasoning,
            description=agent_factory_input.description,
        )

    @staticmethod
    def _build_tools(tools: Optional[list[int]]) -> Optional[List[Union[Toolkit, Callable, Function, Dict]]]:
        if not tools:
            return None
        
        #TODO: Add logic recovery tools
        return []