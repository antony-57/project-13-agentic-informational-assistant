from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from schema import AgentState
from nodes import choose_tool_node, weather_node, news_node, final_response_node, clarification_node, fallback_node
from tools.weather import fetch_weather
from tools.news import get_top_headlines, search_news
from routes import route_tool, route_weather, route_news

builder = StateGraph(AgentState)

# ============ ADD NODES ==========================
builder.add_node("choose_tool", choose_tool_node)
builder.add_node("weather_node", weather_node)
builder.add_node("news_node", news_node)
builder.add_node("final_response", final_response_node)
builder.add_node("fallback", fallback_node)
builder.add_node("get_top_headlines", get_top_headlines)
builder.add_node("search_news", search_news)
builder.add_node("fetch_weather", fetch_weather)
builder.add_node("clarification_node", clarification_node)
# ==================================================



# ============ ADD EDGES ==========================
builder.add_edge(START, "choose_tool")
builder.add_conditional_edges(
    "choose_tool",
    route_tool,{
        "weather": "weather_node",
        "news": "news_node",
        "none": "fallback"
    }
)

# ============ Weather ==========================
builder.add_conditional_edges(
    "weather_node",
     route_weather,{
         "clarification": "clarification_node",
         "fetch_weather": "fetch_weather"
    }
)

builder.add_edge("clarification_node", "fetch_weather")
builder.add_edge("fetch_weather", "final_response")
# ================================================



# ============ News ==========================
builder.add_conditional_edges(
    "news_node",
    route_news,{
        "headlines": "get_top_headlines",
        "search": "search_news",
        "none": "fallback"
    }
)

builder.add_edge("get_top_headlines", "final_response")
builder.add_edge("search_news", "final_response")
# ============================================

builder.add_edge("final_response", END)

# ============ Fallback ==========================
builder.add_edge("fallback", END)
# =================================================



checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    config = {
        "configurable": {"thread_id": "001"}
    }

    initial_state: AgentState = {
        "user_query": ""
    }

    result = graph.invoke(initial_state, config=config)

    if "__interrupt__" in result:
        question = result["__interrupt__"][0].value
        print(question)

        answer = input("Enter your answer: ")

        result = graph.invoke(
            Command(resume=answer),
            config=config
        )

    # print(
    #     result.get(
    #         "final_response",
    #         "Sorry, I couldn't generate a response. Please try again."
    #     )
    # )
    









        