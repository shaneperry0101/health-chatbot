from langgraph.graph.message import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

from typing import Literal


class HealthAgent:
    def __init__(self, model: ChatGroq, tools, system=""):
        self.system = system
        self.model = model
        self.model_with_tools = model.bind_tools(tools)
        self.final_model = model.with_config(tags=["final_node"])

        builder = StateGraph(MessagesState)
        # builder.add_node("llm", self.call_model)
        builder.add_node("llm_tools", self.call_model_with_tools)
        builder.add_node("tools", ToolNode(tools))
        # builder.add_node("final", self.call_final_model)
        # builder.add_edge(START, "llm")
        builder.add_edge(START, "llm_tools")
        # builder.add_edge("llm", "final")
        builder.add_edge("llm_tools", "tools")
        builder.add_edge("tools", END)
        # builder.add_edge("final", END)
        self.graph = builder.compile()

    def should_continue(self, state: MessagesState) -> Literal["tools", "final"]:
        last_message = state["messages"][-1]
        
        if last_message.tool_calls:
            return "tools"
        else:
            return "final"

    def call_model(self, state: MessagesState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        response = self.model.invoke(messages)
        
        return {"messages": [response]}
    
    def call_model_with_tools(self, state: MessagesState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        response = self.model_with_tools.invoke(messages)
        
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
