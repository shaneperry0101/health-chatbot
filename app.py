from langchain_core.messages import HumanMessage
from langchain.schema.runnable.config import RunnableConfig

from chainlit.types import ThreadDict
import chainlit as cl
from typing import Optional

from agents import healthAgent


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
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

    return [
        cl.ChatProfile(
            name="My Chat Profile",
            icon="https://picsum.photos/250",
            markdown_description="The underlying LLM model is **GPT-3.5**, a *175B parameter model* trained on 410GB of text data.",
            starters=[
                cl.Starter(
                    label="Morning routine ideation",
                    message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
                    icon="/public/idea.svg",
                ),
                cl.Starter(
                    label="Explain superconductors",
                    message="Explain superconductors like I'm five years old.",
                    icon="/public/learn.svg",
                ),
                cl.Starter(
                    label="Python script for daily email reports",
                    message="Write a script to automate sending daily email reports in Python, and walk me through how I would set it up.",
                    icon="/public/terminal.svg",
                ),
                cl.Starter(
                    label="Text inviting friend to wedding",
                    message="Write a text asking a friend to be my plus-one at a wedding next month. I want to keep it super short and casual, and offer an out.",
                    icon="/public/write.svg",
                )
            ],
        )
    ]


@cl.on_chat_start
async def on_chat_start():
    print("hello", cl.user_session.get(
        "user").identifier, cl.user_session.get("id"))
    # app_user = cl.user_session.get("user")
    # await cl.Message(f"Hello {app_user.identifier}").send()
    # res = await cl.AskUserMessage(
    #     content="""
    #         **What is your name?**
    #         \n(If you don't respond in 30 seconds, the default name 'User' is used.)
    #         """,
    #     timeout=30
    # ).send()

    # name = res['output'] if res else "User"
    # await cl.Message(
    #     content=f"""
    #         Your name is: {name}.
    #         \n# Welcome to our healthcare assistant!
    #         \nYou can now start chatting about what you concern!
    #         """,
    # ).send()


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
            and metadata["langgraph_node"] == "final"
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
