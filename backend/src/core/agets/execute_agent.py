from .factory_agent import FactoryAgent
from agno.agent import Agent, RunOutput
from ...models.dto.agents.agentLLM import AgentFactoryInput

class ExecuteAgent:

    #TODO: verify content type case is not a string
    @staticmethod
    async def run_agent(agent: AgentFactoryInput, user_input: str) -> str:
        agent_instance: Agent = FactoryAgent.build_agent(agent)
        response: RunOutput = await agent_instance.arun(user_input)
        return response.content