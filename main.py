from fastapi import FastAPI, Query, HTTPException
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent

import requests
import os

# Load .env file
load_dotenv()

app = FastAPI(
    title="Weather Agent API",
    version="1.0"
)

# Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in .env file"
    )

if not OPENWEATHER_API_KEY:
    raise ValueError(
        "OPENWEATHER_API_KEY not found in .env file"
    )

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)


@tool
def get_temp_details(city: str):
    """
    Get weather details of a city.
    """

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}"
        f"&appid={OPENWEATHER_API_KEY}"
        f"&units=metric"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return {
            "error": "Unable to fetch weather"
        }

    return response.json()


# Create Agent
agent = create_agent(
    model=llm,
    tools=[get_temp_details]
)


@app.get("/")
def home():
    return {
        "message": "Weather Agent Running Successfully"
    }


@app.post("/get_weather")
def incoming_weather_params(
    city: str = Query(...),
    question: str = Query(...)
):
    try:

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"City: {city}. "
                            f"Question: {question}"
                        )
                    }
                ]
            }
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )