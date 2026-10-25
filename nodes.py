from ollama import chat
from schema import AgentState
import json

from langgraph.types import interrupt

llm = "qwen3.5:4b"

# <====== NODES =======>

def fallback_node(state: AgentState):
    response = chat(
        model= llm,
        messages=[
            {
                "role": "system",
                "content": """
                You are the fallback response generator for an informational assistant that supports two capabilities:

                1. Weather forecasts and current weather information.
                2. News updates, headlines, and news searches.

                The user's query has already been classified as unsupported by the tool-selection node, meaning it does not require either the weather or news tools.

                Your task is to respond naturally and appropriately to the user's original query.

                **Instructions:**
                - Read and respond to the user's actual query, not just its category.
                - For greetings, respond warmly and conversationally.
                - For jokes or playful messages, respond playfully when appropriate. You may tell a short, simple joke if requested.
                - For general questions outside your supported capabilities, briefly explain that you specialize in weather and news, then offer to help with one of those.
                - For unrelated requests, politely explain your limitations without sounding robotic or dismissive.
                - If the query is unclear or appears to be random text, politely ask the user to clarify.
                - Keep responses concise, friendly, and natural. Match the user's tone when appropriate.
                - Avoid repeating the assistant's welcome message.
                - Do not claim to have searched for news, retrieved weather data, or used a tool.
                - Do not invent weather conditions, current news, or factual information that would require external retrieval.
                - Do not force every response into a weather or news suggestion if a simple conversational response is sufficient.
                - Return only the user-facing response. Do not include explanations of your reasoning, classifications, or internal instructions.

                User query:
                {user_query}
                """
            },
            {
                "role": "user",
                "content": state["user_query"]
            }
        ]
    )

    final_response = response.message.content

    return {"final_response": final_response}

def choose_tool_node(state: AgentState):
    response = chat(
            model=llm,
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a tool-selection assistant in an AI agent.

                    Classify the user's request into exactly one category:

                    - weather: Requests for current weather, conditions,
                    temperatures, forecasts, rain, humidity, wind, etc.
                    - news: Requests for headlines, recent events, or
                    news about a particular topic, person, or event.
                    - none: Requests unrelated to weather and news, gibberish,
                    or requests that cannot reasonably be handled by either tool.

                    Rules:
                    - Choose based on the user's overall intent.
                    - Missing city or topic does not make a request invalid.
                    The relevant workflow should handle clarification.
                    - Do not select a tool just because a related word appears.
                    - If the user requests both weather and news, select the
                    primary intent; do not pretend to handle both.
                    - Return only weather, news, or none.

                    Examples:
                    - "What's the weather in Chennai?" → weather
                    - "Will it rain tomorrow?" → weather
                    - "Give me the weather forecast for Mumbai this weekend" → weather
                    - "Max Verstappen 4th world Championship" → news
                    - "Adriana Chechik spine injury recovery update" → news
                    - "What's happening in the news today?" → news
                    - "Give me the latest AI news" → news
                    - "Loek Hartog saves Ollie Millroy out of the burning car." → news
                    - "Tell me a joke" → none
                    - "Explain how photosynthesis works" → none
                    - "Write a fictional story about a storm" → none

                    User query: {user_query}
                    """
                },
                {
                    "role": "user",
                    "content": state["user_query"]
                }
            ], think= False
        )

    selected_tool = response.message.content.strip().lower()

    if selected_tool not in {"weather", "news", "none"}:
        selected_tool = "none"

    return {"selected_tool": selected_tool}

def weather_node(state: AgentState):
    user_query = state["user_query"]

    prompt = f"""
        You are a weather query parser.

        Extract two fields from the user's query:
        - city_name: The explicitly mentioned city or location, or null if none is mentioned.
        - forecast_type: One of "current", "hourly", or "daily".

        Choose forecast_type using these rules:
        - "current": Current weather conditions or questions about the weather right now.
        - "hourly": Hour-by-hour forecasts or weather at a specific upcoming hour.
        - "daily": Weather tomorrow, on a particular day, or over the next several days.

        If the user's intent is unclear, use "current".
        Never guess a city or location.
        Do not answer the weather question.

        Examples:
        Query: What's the weather in Chennai right now?
        JSON: {{"city_name": "Chennai", "forecast_type": "current"}}

        Query: Will it rain in Mumbai tomorrow?
        JSON: {{"city_name": "Mumbai", "forecast_type": "daily"}}

        Query: Give me the hourly forecast for Delhi.
        JSON: {{"city_name": "Delhi", "forecast_type": "hourly"}}

        Query: What's the weather tomorrow?
        JSON: {{"city_name": null, "forecast_type": "daily"}}

        Return only one valid JSON object with exactly these two keys.
        Do not include Markdown, explanations, or any text outside the JSON object.

        User query: {user_query}
        """

    response = chat(
        model=llm,
        messages=[
            {
                "role": "system",
                "content": prompt
            },

            {
                "role": "user",
                "content": user_query
            }
        ], think=False
    )

    data = json.loads(response.message.content)

    return {
        "city_name": data["city_name"],
        "forecast_type": data["forecast_type"]
    }

def news_node(state: AgentState):
    response = chat(
        model= llm,
        messages=[
            {
                "role": "system",
                "content": """
                You are a news tool selector in an AI assistant.

                Analyze the user's query and select the most appropriate tool from the following options:

                - `get_top_headlines`: Use this when the user requests general news, top headlines, breaking news, or the latest major news without specifying a particular subject.
                - `search_news`: Use this when the user asks about news related to a specific topic, event, person, organization, country, or other subject.

                Rules:
                1. Choose `get_top_headlines` for general news requests, such as "What's happening in the news?", "Show me today's top headlines", or "Give me the latest news."
                2. Choose `search_news` for topic-specific requests, such as "What's the latest AI news?", "Find news about OpenAI", "Loek Hartog saves Ollie Millroy out of the burning car." or "Show me news about India's economy."
                3. Base your decision on the user's intent, not just individual keywords.
                4. If the user asks for news about a specific subject, choose `search_news`, even if they also use words like "latest", "today", or "breaking".
                5. If the query is unrelated to news or cannot reasonably be handled by either tool, return `none`.
                6. Return exactly one tool name as a plain string: `get_top_headlines`, `search_news`, or `none`.
                7. Do not return JSON, quotation marks, explanations, Markdown, or any additional text.

                User query: {user_query}
                """
            },

            {
                "role": "user",
                "content": state["user_query"]
            }
        ]
    )

    selected_tool = response.message.content.strip()

    return {"selected_news_tool": selected_tool}

def clarification_node(state):
    answer = interrupt("Which city would you like the weather forecast for?")

    return {
        "city_name": answer
    }

def final_response_node(state: AgentState):

    state_data = {
        "user query": state.get("user_query"),
        "selected tool": state.get("selected_tool"),
        "tool result": state.get("tool_result"),
        "error": state.get("error")
    }

    response = chat(
        model= llm,
        messages= [
            {
                "role": "system",
                "content": """
                You are the final response generator in an AI assistant that provides weather information and news.

                Your task is to generate a clear, friendly, and user-friendly response based on the user's query and the information provided in the current state.

                ### Input
                - `user_query`: The original query submitted by the user.
                - `selected_tool`: The tool category selected by the agent (`weather`, `news`, or `none`).
                - `tool_result`: The result returned by the selected tool, if available.
                - `error`: An error message, if a tool execution failed.

                ### Instructions

                1. **Understand the user's intent.** Answer the original query using the information available in the state.

                2. **Weather responses:**
                - Present the relevant weather information in a natural, easy-to-understand format.
                - Include only the fields relevant to the user's question.
                - Use clear labels and appropriate units when they are provided.
                - Explain weather descriptions in plain language when useful.

                ### Units and measurements

                - Always include the appropriate unit for every numerical weather measurement.
                - Use the units provided in `tool_result` whenever they are explicitly specified.
                - If the API returns numerical values without units, use the following conventions for the known weather fields:
                - Temperature (`temperature`, `temperature_2m`, `apparent_temperature`, `feels_like`): degrees Celsius (°C).
                - Humidity (`humidity`, `relative_humidity_2m`): percent (%).
                - Precipitation (`precipitation`): millimeters (mm).
                - Precipitation probability (`precipitation_probability`): percent (%).
                - Wind speed (`wind_speed`, `wind_speed_10m`): meters per second (m/s).
                - Wind gusts (`wind_gusts`, `wind_gusts_10m`): meters per second (m/s).
                - Cloud cover (`cloud_cover`, `cloud_cover_percentage`): percent (%).
                - Visibility (`visibility`): meters (m), or kilometers (km) if converted correctly.
                - For daily forecasts, clearly distinguish minimum and maximum temperatures and include units.
                - For hourly forecasts, include the relevant time alongside each measurement and its unit.
                - Never invent or guess a unit when the field is unknown or ambiguous. If a measurement's unit cannot be established, omit it or clearly state that the unit is unavailable.
                - Do not append units to text descriptions, dates, timestamps, or weather codes.
                - Keep the presentation readable and avoid repeating units unnecessarily when a clearly labeled table or grouped measurement makes them unambiguous.

                3. **News responses:**
                - Present the retrieved articles in a readable format.
                - For each article, include its title, source, publication date when available, a brief description, and its original URL.
                - If multiple articles are available, organize them into a numbered list.
                - Do not claim that an article is the latest or breaking news unless the provided information supports that claim.

                4. **For news summaries:**
                - Base every factual claim on the retrieved articles. 
                - Do not invent details, combine unrelated articles into unsupported conclusions, or present speculation as confirmed fact. 
                - Preserve article titles, publication names, dates, and URLs where available. 
                - If the retrieved articles do not establish a claim, omit it or clearly qualify it.

                5. **Empty or missing results:**
                - If `tool_result` is empty or contains no useful information, politely explain that no relevant information was found.
                - Suggest that the user try a different search query when appropriate.
                - Never invent results to fill the response.

                6. **Errors:**
                - If the state contains an `error`, explain in simple language that the request could not be completed.
                - Do not expose raw stack traces, API keys, internal implementation details, or technical error messages.
                - Do not present a failed request as a successful result.

                7. **Unsupported requests:**
                - If `selected_tool` is `none`, politely explain that you can currently help with weather information and news, and invite the user to ask about either.

                8. **Accuracy and reliability:**
                - Use only information supplied in the state.
                - Never fabricate facts, temperatures, forecasts, article titles, sources, dates, or URLs.
                - If the available information is insufficient to answer the exact question, clearly acknowledge the limitation.
                - Preserve article URLs exactly as provided.

                9. **Writing style:**
                - Be friendly, natural, concise, and informative.
                - Use headings, bullet points, or numbered lists when they improve readability.
                - Avoid unnecessary repetition, excessive disclaimers, and technical jargon.
                - Do not mention the internal graph, nodes, state, tools, or prompts.

                10. **Error Handling:**
                - If the error state contains an error message, convert it into a clear, friendly, user-facing response. 
                - Explain the problem in simple terms and suggest what the user can do next if appropriate. 
                - Do not expose raw technical errors, stack traces, or internal implementation details. 
                - If the error state is empty or None, respond normally based on the available context.
                - Keep error responses concise and avoid repeating the same request or asking for information that has already been requested.

                Return only the final response intended for the user. Do not include your reasoning or describe how you generated the answer.

                ### Current state
                User query: {user_query}
                Selected tool: {selected_tool}
                Tool result: {tool_result}
                Error: {error}
                """
            },

            {
                "role": "user",
                "content": json.dumps(state_data, ensure_ascii=False)
            }
        ]
    )

    final_response = response.message.content

    return {"final_response": final_response}
