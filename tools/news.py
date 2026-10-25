import os
from dotenv import load_dotenv
from schema import AgentState
import requests

load_dotenv()

API_KEY = os.getenv("GNEWS_API_KEY")

if not API_KEY:
    raise ValueError("GNEWS_API_KEY is missing from the .env file.")


def get_top_headlines(state):
    url = "https://gnews.io/api/v4/top-headlines"

    params = {
        "category": "general",
        "lang": "en",
        "max": 5,
        "apikey": API_KEY
    }

    try: 
        response = requests.get(url, params= params, timeout=10)
        response.raise_for_status()

        data = response.json()

    except requests.exceptions.HTTPError as e:
        return {"error": f"API returned an HTTP error: {e}"}

    except requests.exceptions.Timeout:
        return {"error": "The weather service took too long to respond."}
    
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to the weather service."}

    articles = data["articles"]

    return clean_articles(articles)

def search_news(state: AgentState):
    url = "https://gnews.io/api/v4/search"

    params = {
        "q": state["user_query"], 
        "lang": "en", 
        "max": 10, 
        "apikey": API_KEY
    }

    try:
        response = requests.get(url, params= params, timeout=10)
        response.raise_for_status()

        data = response.json()

    except requests.exceptions.HTTPError as e:
        return {"error": f"API returned an HTTP error: {e}"}
    
    except requests.exceptions.Timeout:
        return {"error": "The weather service took too long to respond."}
    
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to the weather service."}

    articles = data["articles"]
    
    return clean_articles(articles)

def clean_articles(articles):
    articles_list = []

    for article in articles:
        articles_list.append({
            "title": article["title"],
            "description": article["description"],
            "source": article["source"]["name"],
            "published_at": article["publishedAt"],
            "url": article["url"]
        })

    return {"tool_result": articles_list}


