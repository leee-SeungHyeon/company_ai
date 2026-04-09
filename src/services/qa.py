from functools import lru_cache
from langchain_core.messages import HumanMessage
from agent import create_agent
from agent.state import State
from agent.tools import InternalDocSearchTool
from config import QDRANT_URL, DENSE_MODEL, SPARSE_MODEL, MAX_EXECUTE_TOOL_COUNT


@lru_cache(maxsize=1)
def _get_agent():
    return create_agent(
        tools=[
            InternalDocSearchTool(
                qdrant_url=QDRANT_URL,
                dense_model_name=DENSE_MODEL,
                sparse_model_name=SPARSE_MODEL,
            )
        ]
    )


async def answer_question(query: str, user_roles: list[str] = None) -> str:
    agent = _get_agent()
    result = await agent.ainvoke(
        State(messages=[HumanMessage(content=query)], execute_tool_count=0),
        {"configurable": {
            "max_execute_tool_count": MAX_EXECUTE_TOOL_COUNT,
            "user_roles": user_roles or ["all"],
        }},
    )
    return result["messages"][-1].content
