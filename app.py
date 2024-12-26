from langchain_core.messages import HumanMessage
from langchain.schema.runnable.config import RunnableConfig

from chainlit.types import ThreadDict
import chainlit as cl
from typing import Optional

from core import healthAgent
from utils import chatProfile


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin",
            metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    if current_user.metadata["role"] != "admin":
        return None
    else:
        return [chatProfile]


@cl.on_chat_start
async def on_chat_start():
    print("hello", cl.user_session.get(
        "user").identifier, cl.user_session.get("id"))


@cl.on_message
async def on_message(msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    cb = cl.LangchainCallbackHandler()
    final_answer = cl.Message(content="")

    for msg, metadata in healthAgent.graph.stream(
            {"messages": [HumanMessage(content=msg.content)]},
            stream_mode="messages",
            config=RunnableConfig(callbacks=[cb], **config)
    ):
        if (
            msg.content
            and not isinstance(msg, HumanMessage)
            and metadata["langgraph_node"] == "tools"
        ):
            await final_answer.stream_token(msg.content)

    await final_answer.send()


@cl.on_stop
async def on_stop():
    await cl.Message(
        content="The user wants to stop the task!",
    ).send()


@cl.on_chat_end
def on_chat_end():
    print("goodbye", cl.user_session.get(
        "user").identifier, cl.user_session.get("id"))


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print("The user resumed a previous chat session!")
