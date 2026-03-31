import json
import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END

from .state import Config, State
from .llm import get_llm
from .prompt import QA_SYSTEM_PROMPT


def create_agent(tools: list):
    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)
    tools_by_name = {tool.name: tool for tool in tools}

    async def llm_node(state, config):
        max_count = config["configurable"].get("max_execute_tool_count", 3)
        prompt = ChatPromptTemplate.from_messages(
            [SystemMessage(content=QA_SYSTEM_PROMPT.format(max_execute_tool_count=max_count))]
            + state.messages
        )
        response = await (prompt | llm_with_tools).ainvoke({})

        if response.tool_calls:
            if state.execute_tool_count >= max_count:
                return Command(
                    update={"messages": [AIMessage(content="검색 횟수 한도에 도달했습니다. 현재까지의 정보로 답변드리겠습니다.")]},
                    goto=END,
                )
            return Command(update={"messages": [response]}, goto="execute_tool")

        return Command(update={"messages": [AIMessage(content=response.content)]}, goto=END)

    async def execute_tool_node(state, config):
        tasks = [
            (tool_call, tools_by_name[tool_call["name"]].ainvoke(tool_call["args"]))
            for tool_call in state.messages[-1].tool_calls
        ]
        results = await asyncio.gather(*[task for _, task in tasks])

        outputs = [
            ToolMessage(
                name=tool_call["name"],
                content=json.dumps(result, indent=2, ensure_ascii=False),
                tool_call_id=tool_call["id"],
            )
            for (tool_call, _), result in zip(tasks, results)
        ]

        return Command(
            update={"messages": outputs, "execute_tool_count": state.execute_tool_count + 1},
            goto="llm",
        )

    workflow = StateGraph(State, Config)
    workflow.add_node("llm", llm_node)
    workflow.add_node("execute_tool", execute_tool_node)
    workflow.add_edge(START, "llm")
    return workflow.compile()
