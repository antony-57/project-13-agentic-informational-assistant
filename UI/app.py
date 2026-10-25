import sys
from pathlib import Path
from uuid import uuid4

import streamlit as st
from langgraph.types import Command

import traceback

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from graph import graph


st.set_page_config(
    page_title="Informational Assistant",
    page_icon="🌦️",
    layout="centered",
)

# -------------------------
# Session state
# -------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())

if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = False

if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = True

if "pending_config" not in st.session_state:
    st.session_state.pending_config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }


config = st.session_state.pending_config


# -------------------------
# Welcome message
# -------------------------

st.title("🌦️ Informational Assistant")

if st.session_state.welcome_shown:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hey! I'm your informational assistant. "
            "I can help with weather forecasts and news updates.\n\n"
            "Try asking:\n"
            "- What's the weather in Chennai?\n"
            "- What's the forecast for tomorrow in Tokyo?\n"
            "- Show me the latest AI news.\n"
            "- What are today's top headlines?"
        ),
    })
    st.session_state.welcome_shown = False


# -------------------------
# Display chat history
# -------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -------------------------
# Process user input
# -------------------------

def display_graph_result(result):
    """Display a final answer or pause for city clarification."""

    if "__interrupt__" in result:
        interrupt_value = result["__interrupt__"][0].value

        st.session_state.pending_interrupt = True
        st.session_state.messages.append({
            "role": "assistant",
            "content": str(interrupt_value),
        })
        st.rerun()

    else:
        final_response = result.get("final_response", "")

        if final_response:
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_response,
            })

            st.session_state.pending_interrupt = False
            st.rerun()

    response = result.get("final_response")

    if not response:
        response = (
            "Sorry, I couldn't generate a response. "
            "Please try again."
        )

    st.session_state.pending_interrupt = False
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
    })

placeholder = (
    "Enter the city name..."
    if st.session_state.pending_interrupt
    else "Ask about weather or news..."
)

user_input = st.chat_input(placeholder)

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.spinner("Thinking..."):
            if st.session_state.pending_interrupt:
                result = graph.invoke(
                    Command(resume=user_input),
                    config=config,
                )
            else:
                initial_state = {
                    "user_query": user_input,
                }

                result = graph.invoke(
                    initial_state,
                    config=config,
                )

        display_graph_result(result)

    except Exception as e:
        traceback.print_exc()
        st.session_state.pending_interrupt = False

        st.error(f"Debug error: {type(e).__name__}: {e}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                f"Debug error: {type(e).__name__}: {e}"
            ),
        })

