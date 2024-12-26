from dotenv import load_dotenv
from langchain_groq import ChatGroq

from .agents import HealthAgent
from .tools import youtube_search

load_dotenv()

model = ChatGroq(
    model="llama3-70b-8192",
    temperature=1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

tools = [
    youtube_search,
    # get_weather,
    # tavily_search,
]

system_prompt = """You are a smart healthcare assistant. Use the search engine to look up information if needed. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
If you need to look up some information before asking a follow up question, you are allowed to do that!
"""

healthAgent = HealthAgent(model, tools, system=system_prompt)
