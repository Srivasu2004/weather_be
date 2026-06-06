from fastapi import FastAPI, Query, HTTPException
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent

import requests
import os

load_dotenv()

app = FastAPI(
    title="Weather Agent API",
    version="1.0"
)

# Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Validate Groq Key
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY environment variable is missing"
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

    if not OPENWEATHER_API_KEY:
        return {
            "error": "OPENWEATHER_API_KEY is not configured"
        }

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}"
        f"&appid={OPENWEATHER_API_KEY}"
        "&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {
                "error": response.json()
            }

        return response.json()

    except Exception as e:
        return {
            "error": str(e)
        }


agent = create_agent(
    model=llm,
    tools=[get_temp_details]
)


@app.get("/")
def home():
    return {
        "message": "Weather Agent Running Successfully",
        "weather_api_configured": bool(
            OPENWEATHER_API_KEY
        )
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
                        "content": f"City: {city}. Question: {question}"
                    }
                ]
            }
        )

        # Extract final AI response
        answer = result["messages"][-1].content

        return {
            "city": city,
            "question": question,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
