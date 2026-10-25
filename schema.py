from typing import TypedDict

class AgentState(TypedDict):
    user_query: str
    selected_tool: str
    city_name: str | None
    forecast_type: str | None
    selected_news_tool: str
    tool_result: dict | list 
    error: str
    final_response: str
