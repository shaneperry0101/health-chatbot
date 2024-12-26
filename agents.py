from langgraph.graph.message import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

from typing import Literal
from dotenv import load_dotenv

from tools import get_weather, tavily_search


class HealthAgent:
    def __init__(self, model: ChatGroq, tools, system=""):
        self.system = system
        self.model = model.bind_tools(tools)
        self.final_model = model.with_config(tags=["final_node"])

        builder = StateGraph(MessagesState)
        builder.add_node("llm", self.call_model)
        builder.add_node("tools", ToolNode(tools))
        builder.add_node("final", self.call_final_model)
        builder.add_edge(START, "llm")
        builder.add_conditional_edges("llm", self.should_continue)
        builder.add_edge("tools", "llm")
        builder.add_edge("final", END)
        self.graph = builder.compile()

    def should_continue(self, state: MessagesState) -> Literal["tools", "final"]:
        last_message = state["messages"][-1]
        # If the LLM makes a tool call, then we route to the "tools" node
        if last_message.tool_calls:
            return "tools"
        else:  # Otherwise, we stop (reply to the user)
            return "final"

    def call_model(self, state: MessagesState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        response = self.model.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}

    def call_final_model(self, state: MessagesState):
        last_ai_message = state["messages"][-1]
        response = self.final_model.invoke(
            [
                SystemMessage("Rewrite this in Markdown format"),
                HumanMessage(last_ai_message.content),
            ]
        )
        # overwrite the last AI message from the agent
        response.id = last_ai_message.id
        return {"messages": [response]}


_ = load_dotenv()

model = ChatGroq(
    model="llama3-70b-8192",
    temperature=1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

tools = [
    # get_weather,
    # tavily_search,
]

system_prompt = """You are a smart healthcare assistant. Use the search engine to look up information if needed. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
If you need to look up some information before asking a follow up question, you are allowed to do that!
"""

healthAgent = HealthAgent(model, tools, system=system_prompt)
