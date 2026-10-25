from schema import AgentState

def route_tool(state: AgentState):
    selected_tool = state["selected_tool"]

    if selected_tool == "weather":
        return "weather"

    elif selected_tool == "news":
        return "news"

    return "none"

def route_weather(state: AgentState):
    if state["city_name"] is None:
        return "clarification"

    return "fetch_weather"

def route_news(state: AgentState):
    news_tool = state["selected_news_tool"]

    if news_tool == "get_top_headlines":
        return "headlines"

    elif news_tool == "search_news":
        return "search"

    return "none"
