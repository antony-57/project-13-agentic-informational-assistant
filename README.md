# Project 13 — Agentic Informational Assistant

An interactive AI assistant built with Python, LangGraph, Ollama, and Streamlit that can retrieve weather information and news updates through tool-based routing.

This project explores how an agentic application can interpret a user's request, choose an appropriate tool, execute the required operation, and generate a conversational response. It also includes a fallback path for requests outside its supported capabilities.

**Completed:** October 25, 2026

## Features

- **Weather information:** Retrieve current weather conditions and forecasts for a specified location using the Open-Meteo API.
- **News retrieval:** Fetch top headlines or search for news articles using the GNews API.
- **LLM-based tool selection:** Use a locally running Qwen model to determine whether a request requires the weather tool, news tool, or fallback response.
- **Conditional workflow routing:** Direct execution through different nodes based on the selected tool and request type.
- **Conversational fallback:** Respond to greetings, jokes, unsupported requests, and unclear messages without unnecessarily invoking weather or news tools.
- **Interactive chat interface:** Use a Streamlit interface to submit queries and view responses in a conversational format.
- **Local LLM inference:** Run the language model locally through Ollama, avoiding the need for a paid hosted LLM API.
- **Environment-based API configuration:** Store the news API key in a `.env` file rather than hardcoding it in the source code.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| LangGraph | State management, nodes, edges, and conditional routing |
| Ollama | Local LLM inference |
| Qwen3.5:4B | Query interpretation and response generation |
| Streamlit | Interactive chat interface |
| Open-Meteo | Weather data and geocoding |
| GNews | News headlines and article search |
| Requests | HTTP requests to external APIs |
| python-dotenv | Loading environment variables |

## How It Works

The application uses a graph-based workflow in which each node performs a specific task and updates the shared application state.

1. **User input:** The user submits a query through the Streamlit interface.
2. **Tool selection:** The LLM-based routing node determines whether the request concerns weather, news, or neither.
3. **Conditional routing:** LangGraph directs execution to the appropriate workflow.
4. **Tool execution:**
   - The weather workflow interprets the requested location and forecast type, retrieves the relevant data, and processes the result.
   - The news workflow selects the appropriate operation, such as retrieving headlines or searching for articles.
5. **Fallback handling:** Unsupported requests are handled by a separate fallback node.
6. **Response generation:** The application produces a user-facing response and displays it in the chat interface.

### Architecture Overview

```text
User Query
    |
    v
Choose Tool (LLM)
    |
    +------ Weather ------> Weather Workflow
    |                           |
    |                           v
    |                      Open-Meteo API
    |                           |
    |                           v
    |                     Process Results
    |
    +------ News ---------> News Workflow
    |                           |
    |                           v
    |                        GNews API
    |                           |
    |                           v
    |                     Process Results
    |
    +------ None ---------> Fallback Node
                                |
                                v
                         Final Response
                                |
                                v
                         Streamlit Chat UI
```

The diagram represents the main workflow at a high level. The actual graph includes additional routing decisions within the weather and news workflows.

## Project Structure

```text
project-13/
├── tools/
│   ├── weather.py
│   └── news.py
├── UI/
│   └── app.py
├── schema.py
├── routes.py
├── graph.py
├── nodes.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

- `modules/weather.py` — Weather retrieval and processing logic.
- `modules/news.py` — News API integration and article retrieval.
- `UI/app.py` — Streamlit chat interface and conversation handling.
- `schema.py` — Defines the shared state structure used by the graph.
- `routes.py` — Contains routing logic for conditional graph transitions.
- `graph.py` — Defines the LangGraph workflow and connects its nodes.
- `nodes.py` — Contains all the nodes of the graph.
- `.env` — Stores local environment variables and API credentials.
- `.env.example` — Example environment file to add your own API key.
- `.gitignore` — Excludes sensitive files and other files that should not be tracked.
- `requirements.txt` — Lists the Python dependencies.

## Setup and Installation

### Prerequisites

- Python installed on your system.
- [Ollama](https://ollama.com/) installed and running.
- The `qwen3.5:4b` model available locally.
- A GNews API key for news functionality.

### 1. Clone the repository

```bash
git clone <repository-url>
cd project-13
```

Replace `<repository-url>` with the URL of your repository.

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Ollama

Download the model if it is not already available:

```bash
ollama pull qwen3.5:4b
```

Make sure Ollama is running before launching the application.

### 5. Configure the API key

Create a `.env` file in the project root:

```dotenv
GNEWS_API_KEY=your_actual_api_key_here
```

Replace the placeholder with your GNews API key.

**Security note:** Do not commit `.env` to GitHub. Ensure it is listed in `.gitignore`. If a key has already been exposed, revoke or rotate it.

### 6. Run the application

Launch the Streamlit interface from the project root:

```bash
streamlit run UI/app.py
```

## Example Queries

**Weather**
- What's the weather in Chennai?
- What's the forecast for tomorrow in Tokyo?
- What is the temperature and humidity in Singapore?

**News**
- What are today's top headlines?
- Show me the latest AI news.
- Search for news about the 2026 United States Grand Prix.

**General conversation**
- Hey buddy!
- Tell me a joke.
- Ask an unrelated or unsupported question to see how the fallback responds.

The exact results depend on API availability, provider limitations, and the information returned by the selected service.

## Current Limitations

- The assistant supports weather and news as its primary information-retrieval capabilities; it is not a general-purpose research agent.
- Tool selection and query interpretation depend on the local LLM's output, so ambiguous requests may occasionally be routed incorrectly.
- The fallback node handles unsupported requests but does not provide unrestricted general-purpose knowledge or external research.
- Error handling and recovery are basic. Invalid locations, API failures, and network problems may not always receive specialized recovery flows.
- Automatic retries and a complete invalid-city correction loop are not implemented as dedicated, fully tested workflows.
- News availability, freshness, and search results depend on the GNews API plan and its restrictions.
- The application has not been extensively tested for concurrent users, long-running sessions, or production deployment.
- No automated test suite or comprehensive evaluation of routing accuracy has been established.

## Future Improvements

- **Improve error handling:** Distinguish invalid locations, API errors, network failures, and unexpected responses.
- **Add retry and clarification workflows:** Allow users to correct invalid city names and resolve ambiguous requests through additional interaction.
- **Improve tool selection:** Evaluate routing accuracy on a wider range of queries and reduce incorrect tool selection.
- **Add conversation memory:** Preserve relevant conversational context so follow-up questions can refer to earlier weather locations or news searches.
- **Improve response grounding:** Ensure generated responses accurately reflect retrieved API data and communicate when information is unavailable.
- **Expand weather and news capabilities:** Add more forecast options, date-specific weather queries, richer news filtering, and improved article summaries.
- **Add automated testing:** Test individual tools, routing decisions, error cases, and end-to-end graph execution.
- **Improve observability:** Add structured logging and clearer debugging information for node execution and API failures.
- **Improve deployment readiness:** Add configuration validation, dependency management, and more robust handling of secrets and application errors.

## Learning Outcomes

This project provided hands-on experience with:

- Building stateful AI workflows using LangGraph.
- Understanding nodes, edges, conditional edges, and shared state.
- Using an LLM to select tools based on user intent.
- Integrating external APIs into an agentic workflow.
- Separating routing, tool execution, state definitions, and UI logic into distinct modules.
- Connecting a Python backend to an interactive Streamlit interface.
- Managing API credentials through environment variables.
- Understanding the difference between a working prototype and a production-ready application.

## Conclusion

Project 13 is a learning-focused agentic application that combines LLM-based routing, external information-retrieval tools, graph-based orchestration, and a conversational interface.

The goal was to understand how these components work together in a functional application—not to build a fully autonomous or production-ready agent. Future improvements will focus on reliability, testing, better error recovery, and more robust conversational workflows.
