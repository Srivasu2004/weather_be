from fastapi import FastAPI
import requests
from langchain.tools import tool

app = FastAPI(title="AI Travel Planner")

# =========================
# CONFIG (ADD YOUR KEYS)
# =========================
OPENWEATHER_API_KEY = "open_weather_key"


# =========================
# 1. WEATHER TOOL
# =========================
def get_weather(city: str):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    response = requests.get(url)

    print("Status Code:", response.status_code)
    print("Response:", response.text)

    data = response.json()

    if response.status_code != 200:
        return {"error": data.get("message", "Weather API error")}

    return {
        "city": city,
        "temperature": data["main"]["temp"],
        "weather": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"]
    }


# =========================
# 2. WEB SEARCH TOOL (BASIC MOCK / API READY)
# =========================
def web_search(query: str):
    # You can replace this with SerpAPI / Tavily API later
    return {
        "query": query,
        "results": [
            f"Top attractions for {query}",
            f"Best time to visit {query}",
            f"Travel tips for {query}"
        ]
    }


# =========================
# 3. BUDGET CALCULATOR TOOL
# =========================
def budget_calculator(days: int, per_day_cost: float):
    total = days * per_day_cost

    return {
        "days": days,
        "per_day_cost": per_day_cost,
        "total_budget": total
    }


# =========================
# LANGCHAIN TOOLS (OPTIONAL AGENT LAYER)
# =========================
@tool
def weather_tool(city: str):
    """Get weather of a city"""
    return get_weather(city)


@tool
def search_tool(query: str):
    """Search travel information"""
    return web_search(query)


@tool
def budget_tool(days: int, cost: float):
    """Calculate travel budget"""
    return budget_calculator(days, cost)


tools = [weather_tool, search_tool, budget_tool]


# =========================
# 4. API ENDPOINTS
# =========================

@app.get("/")
def home():
    return {"message": "AI Travel Planner API Running 🚀"}


@app.get("/weather")
def weather(city: str):
    return get_weather(city)


@app.get("/search")
def search(query: str):
    return web_search(query)


@app.get("/budget")
def budget(days: int, cost: float):
    return budget_calculator(days, cost)


# =========================
# 5. TRAVEL PLANNER AGENT (SIMPLE LOGIC)
# =========================
@app.get("/plan-trip")
def plan_trip(city: str, days: int, budget_per_day: float):
    
    weather = get_weather(city)
    budget = budget_calculator(days, budget_per_day)
    search = web_search(city)

    return {
        "destination": city,
        "weather": weather,
        "budget": budget,
        "recommendations": search,
        "message": "Travel plan generated successfully ✈️"
    }
