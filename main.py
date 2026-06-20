from fastapi import FastAPI
from langchain.tools import tool
import requests
import os

app = FastAPI(title="AI Travel Planner")

# ==================================
# CONFIG
# ==================================

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ==================================
# WEATHER AGENT
# ==================================

def get_weather(city: str):

    if not OPENWEATHER_API_KEY:
        return {"error": "OpenWeather API Key not configured"}

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {
                "error": response.json().get(
                    "message",
                    "Unable to fetch weather"
                )
            }

        data = response.json()

        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }

    except Exception as e:
        return {"error": str(e)}


# ==================================
# DESTINATION AGENT
# ==================================

def destination_recommendation(city: str):

    return {
        "city": city,
        "recommendations": [
            f"Visit famous attractions in {city}",
            f"Try local food in {city}",
            f"Explore cultural landmarks in {city}"
        ]
    }


# ==================================
# BUDGET AGENT
# ==================================

def calculate_budget(days: int, cost_per_day: float):

    total = days * cost_per_day

    return {
        "days": days,
        "cost_per_day": cost_per_day,
        "total_budget": total
    }


# ==================================
# ITINERARY AGENT
# ==================================

def generate_itinerary(city: str, days: int):

    itinerary = []

    for day in range(1, days + 1):
        itinerary.append(
            {
                "day": day,
                "plan": f"Explore top attractions in {city}"
            }
        )

    return itinerary


# ==================================
# LANGCHAIN TOOLS
# ==================================

@tool
def weather_tool(city: str):
    """Get weather information for a city"""
    return get_weather(city)


@tool
def destination_tool(city: str):
    """Get destination recommendations"""
    return destination_recommendation(city)


@tool
def budget_tool(days: int, cost_per_day: float):
    """Calculate travel budget"""
    return calculate_budget(days, cost_per_day)


tools = [
    weather_tool,
    destination_tool,
    budget_tool
]

# ==================================
# API ROUTES
# ==================================

@app.get("/")
def home():
    return {
        "message": "AI Travel Planner Running Successfully 🚀"
    }


@app.get("/weather")
def weather(city: str):
    return get_weather(city)


@app.get("/destination")
def destination(city: str):
    return destination_recommendation(city)


@app.get("/budget")
def budget(days: int, cost_per_day: float):
    return calculate_budget(days, cost_per_day)


# ==================================
# MAIN TRAVEL PLANNER
# ==================================

@app.get("/plan-trip")
def plan_trip(
    city: str,
    days: int,
    budget_per_day: float
):

    weather_data = get_weather(city)

    budget_data = calculate_budget(
        days,
        budget_per_day
    )

    recommendations = destination_recommendation(city)

    itinerary = generate_itinerary(
        city,
        days
    )

    return {
        "destination": city,
        "weather": weather_data,
        "budget": budget_data,
        "recommendations": recommendations,
        "itinerary": itinerary,
        "message": "Trip Planned Successfully ✈️"
    }
