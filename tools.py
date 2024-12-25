from langchain_community.tools.tavily_search import TavilySearchResults

from typing import Literal
from langchain_core.tools import tool


tavily_search = TavilySearchResults(max_results=5)


@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        raise AssertionError("Unknown city")
