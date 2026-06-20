from fastapi import FastAPI
from langchain.tools import tool
import requests
import os

app = FastAPI(title="AI Travel Planner")

# ==========================
# CONFIG
# ==========================

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ==========================
# WEATHER TOOL
# ==========================

@tool
def weather_tool(city: str):
    """Get current weather information for a city"""

    if not OPENWEATHER_API_KEY:
        return {
            "error": "OpenWeather API Key not configured"
        }

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        if response.status_code != 200:
            return {
                "error": data.get(
                    "message",
                    "Unable to fetch weather"
                )
            }

        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# ==========================
# RECOMMENDATION TOOL
# ==========================

@tool
def recommendation_tool(city: str):
    """Get travel recommendations for a city"""

    return {
        "results": [
            f"Visit famous attractions in {city}",
            f"Try local food in {city}",
            f"Explore cultural landmarks in {city}",
            f"Visit local markets in {city}",
            f"Take a sightseeing tour in {city}"
        ]
    }


# ==========================
# BUDGET TOOL
# ==========================

@tool
def budget_tool(
    days: int,
    budget_per_day: float
):
    """Calculate travel budget"""

    return {
        "days": days,
        "budget_per_day": budget_per_day,
        "total_budget": days * budget_per_day
    }


# ==========================
# ITINERARY TOOL
# ==========================

@tool
def itinerary_tool(
    city: str,
    days: int
):
    """Generate trip itinerary"""

    itinerary = []

    for day in range(1, days + 1):

        itinerary.append({
            "day": day,
            "plan": f"Explore attractions in {city}"
        })

    return itinerary


# ==========================
# REGISTER TOOLS
# ==========================

tools = [
    weather_tool,
    recommendation_tool,
    budget_tool,
    itinerary_tool
]

# ==========================
# HOME
# ==========================

@app.get("/")
def home():

    return {
        "message": "AI Travel Planner Running 🚀",
        "tools": [
            tool.name
            for tool in tools
        ]
    }


# ==========================
# WEATHER API
# ==========================

@app.get("/weather")
def weather(city: str):

    return weather_tool.invoke(
        {"city": city}
    )


# ==========================
# PLAN TRIP
# ==========================

@app.get("/plan-trip")
def plan_trip(
    city: str,
    days: int,
    budget_per_day: float
):

    weather_data = weather_tool.invoke(
        {"city": city}
    )

    recommendations = recommendation_tool.invoke(
        {"city": city}
    )

    budget_data = budget_tool.invoke(
        {
            "days": days,
            "budget_per_day": budget_per_day
        }
    )

    itinerary = itinerary_tool.invoke(
        {
            "city": city,
            "days": days
        }
    )

    return {

        "destination": city,

        "weather": weather_data,

        "budget": budget_data,

        "recommendations": recommendations,

        "itinerary": itinerary,

        "message":
        "Travel Plan Generated Successfully ✈️"
    }
