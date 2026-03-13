"""
Trip Planner Agent
==================
Combining:
  - Google Gemini LLM (direct SDK)
  - OpenWeatherMap (live weather)
  - Google Places API (hotels)
  - Gemini-generated flight options + itinerary
"""

import re
import json
import requests
import google.generativeai as genai
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# Weather Tools
# ─────────────────────────────────────────────────────────────────────────────

def get_current_weather(city: str, api_key: str) -> dict:
    if not api_key:
        return _mock_weather(city)
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        resp = requests.get(url, params={
            "q": city, "appid": api_key, "units": "metric"
        }, timeout=8)
        if resp.status_code == 200:
            d = resp.json()
            return {
                "city": d["name"],
                "country": d["sys"]["country"],
                "temp": round(d["main"]["temp"], 1),
                "feels_like": round(d["main"]["feels_like"], 1),
                "description": d["weather"][0]["description"],
                "humidity": d["main"]["humidity"],
                "wind_speed": d["wind"]["speed"],
                "source": "live"
            }
    except Exception:
        pass
    return _mock_weather(city)


def get_weather_forecast(city: str, api_key: str) -> str:
    if not api_key:
        return _mock_forecast(city)
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        resp = requests.get(url, params={
            "q": city, "appid": api_key, "units": "metric", "cnt": 5
        }, timeout=8)
        if resp.status_code == 200:
            items = resp.json()["list"]
            lines = []
            for item in items[:5]:
                dt = item["dt_txt"][:10]
                temp = round(item["main"]["temp"])
                desc = item["weather"][0]["description"]
                lines.append(f"**{dt}**: {temp}°C, {desc}")
            return "\n".join(lines)
    except Exception:
        pass
    return _mock_forecast(city)


def _mock_weather(city: str) -> dict:
    city_weather = {
        "Tokyo": {"temp": 22, "feels_like": 21, "description": "partly cloudy", "humidity": 65, "wind_speed": 3.5},
        "Udaipur": {"temp": 35, "feels_like": 38, "description": "sunny and hot", "humidity": 30, "wind_speed": 2.1},
        "Paris": {"temp": 18, "feels_like": 17, "description": "mild and breezy", "humidity": 70, "wind_speed": 4.2},
        "New York": {"temp": 8, "feels_like": 5, "description": "cold and clear", "humidity": 55, "wind_speed": 5.0},
    }
    defaults = {"temp": 25, "feels_like": 24, "description": "clear sky", "humidity": 60, "wind_speed": 3.0}
    w = city_weather.get(city, defaults)
    return {"city": city, "country": "N/A", "source": "mock (no API key)", **w}


def _mock_forecast(city: str) -> str:
    return (
        f"**Forecast for {city} (estimated):**\n"
        "Day 1: Warm and sunny, ~25°C\n"
        "Day 2: Partly cloudy, ~23°C\n"
        "Day 3: Light breeze, ~24°C\n"
        "_Add OpenWeatherMap key for live forecasts._"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Google Places — Hotels
# ─────────────────────────────────────────────────────────────────────────────

def get_hotels_from_places(city: str, api_key: str) -> list:
    if not api_key:
        return _mock_hotels(city)
    try:
        search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        resp = requests.get(search_url, params={
            "query": f"best hotels in {city}",
            "type": "lodging",
            "key": api_key,
        }, timeout=8)
        if resp.status_code == 200:
            results = resp.json().get("results", [])[:5]
            hotels = []
            for r in results:
                hotels.append({
                    "name": r.get("name", "N/A"),
                    "area": r.get("formatted_address", "N/A").split(",")[0],
                    "stars": min(5, max(3, round(r.get("rating", 4)))),
                    "price_per_night": _estimate_price(r.get("price_level", 2)),
                    "highlights": f"Rating: {r.get('rating', 'N/A')} | {r.get('user_ratings_total', 0)} reviews",
                    "source": "Google Places"
                })
            if hotels:
                return hotels
    except Exception:
        pass
    return _mock_hotels(city)


def _estimate_price(price_level: int) -> str:
    mapping = {0: "Free", 1: "$30-60/night", 2: "$60-120/night", 3: "$120-250/night", 4: "$250+/night"}
    return mapping.get(price_level, "$80-150/night")


def _mock_hotels(city: str) -> list:
    mock = {
        "Tokyo": [
            {"name": "Park Hyatt Tokyo", "area": "Shinjuku", "stars": 5, "price_per_night": "$350/night", "highlights": "Iconic views, Lost in Translation hotel"},
            {"name": "Dormy Inn Asakusa", "area": "Asakusa", "stars": 3, "price_per_night": "$90/night", "highlights": "Near Senso-ji, great breakfast"},
            {"name": "Hotel Gracery Shinjuku", "area": "Shinjuku", "stars": 4, "price_per_night": "$180/night", "highlights": "Godzilla statue on roof"},
        ],
        "Udaipur": [
            {"name": "Taj Lake Palace", "area": "Lake Pichola", "stars": 5, "price_per_night": "$400/night", "highlights": "Floating palace on the lake"},
            {"name": "Raas Devigarh", "area": "Delwara", "stars": 5, "price_per_night": "$300/night", "highlights": "Heritage palace, stunning views"},
            {"name": "Hotel Boheda Palace", "area": "City Center", "stars": 3, "price_per_night": "$60/night", "highlights": "Budget-friendly, lake view"},
        ],
        "Paris": [
            {"name": "Le Bristol Paris", "area": "8th Arrondissement", "stars": 5, "price_per_night": "$900/night", "highlights": "Palace hotel near Élysée"},
            {"name": "Hotel des Grands Boulevards", "area": "2nd Arrondissement", "stars": 4, "price_per_night": "$220/night", "highlights": "Trendy design, rooftop bar"},
            {"name": "Hotel Perreyve", "area": "Saint-Germain", "stars": 3, "price_per_night": "$130/night", "highlights": "Quiet, near Luxembourg Gardens"},
        ],
        "New York": [
            {"name": "The Plaza Hotel", "area": "Midtown Manhattan", "stars": 5, "price_per_night": "$800/night", "highlights": "Iconic 5th Ave location"},
            {"name": "citizenM New York Times Square", "area": "Times Square", "stars": 4, "price_per_night": "$200/night", "highlights": "Modern, great location"},
            {"name": "Pod 39", "area": "Murray Hill", "stars": 3, "price_per_night": "$120/night", "highlights": "Hip budget hotel, rooftop bar"},
        ],
    }
    return mock.get(city, [
        {"name": f"Grand Hotel {city}", "area": "City Center", "stars": 4, "price_per_night": "$150/night", "highlights": "Central location, great amenities"},
        {"name": f"Budget Inn {city}", "area": "Old Town", "stars": 3, "price_per_night": "$70/night", "highlights": "Clean, affordable, well-located"},
    ])


# ─────────────────────────────────────────────────────────────────────────────
# LLM Helpers — all use Gemini SDK directly
# ─────────────────────────────────────────────────────────────────────────────

def llm_call(model, prompt: str) -> str:
    """Single helper to call Gemini and return text."""
    response = model.generate_content(prompt)
    return response.text.strip()


def parse_trip_query(query: str) -> dict:
    days_match = re.search(r'(\d+)\s*-?\s*day', query, re.I)
    days = int(days_match.group(1)) if days_match else 3

    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    month = "May"
    for m in months:
        if m.lower() in query.lower():
            month = m
            break

    dest_match = re.search(r'trip\s+to\s+([\w\s]+?)(?:\s+in\s|\s*$)', query, re.I)
    destination = dest_match.group(1).strip().title() if dest_match else "Tokyo"

    return {"destination": destination, "days": days, "month": month}


def generate_flights_with_llm(model, destination: str, origin: str, days: int, month: str, currency: str) -> list:
    prompt = f"""You are a travel expert. Generate 3 realistic flight options for a trip from {origin or 'major international hub'} to {destination} in {month}, for {days} days.

Return ONLY a valid JSON array (no markdown, no explanation) like:
[
  {{
    "airline": "Air India",
    "departure": "09:30",
    "arrival": "14:45",
    "duration": "5h 15m",
    "price": "{currency} 450",
    "class": "Economy",
    "stops": "Direct"
  }}
]
Make prices realistic for {currency}. Include 1 direct and 2 with 1 stop. Vary airlines."""
    try:
        text = llm_call(model, prompt)
        text = re.sub(r'```(?:json)?', '', text).strip('`').strip()
        return json.loads(text)
    except Exception:
        return [
            {"airline": "Major Carrier", "departure": "08:00", "arrival": "16:00",
             "duration": "8h", "price": f"{currency} 400", "class": "Economy", "stops": "Direct"},
            {"airline": "Budget Airline", "departure": "22:00", "arrival": "10:00+1",
             "duration": "12h", "price": f"{currency} 250", "class": "Economy", "stops": "1 Stop"},
        ]


def generate_city_overview(model, destination: str) -> str:
    prompt = f"""Write exactly ONE compelling paragraph (100-150 words) about {destination}'s cultural and historic significance.
Cover: history, famous landmarks, cultural heritage, why it's a must-visit.
Be vivid and engaging. No headers, just one paragraph."""
    try:
        return llm_call(model, prompt)
    except Exception:
        return f"{destination} is a fascinating destination rich in history and culture."


def generate_day_plan(model, destination: str, days: int, month: str) -> list:
    prompt = f"""Create a detailed {days}-day itinerary for {destination} in {month}.

Return ONLY a valid JSON array (no markdown, no backticks):
[
  {{
    "day": "Day 1 - Arrival & Exploration",
    "morning": "activity description",
    "afternoon": "activity description",
    "evening": "activity description",
    "food": "restaurant or dish recommendation"
  }}
]
Make it specific to {destination} with real places and experiences."""
    try:
        text = llm_call(model, prompt)
        text = re.sub(r'```(?:json)?', '', text).strip('`').strip()
        return json.loads(text)
    except Exception:
        return [{"day": f"Day {i+1}", "morning": "Sightseeing", "afternoon": "Local exploration",
                 "evening": "Dinner at local restaurant", "food": "Local specialty"} for i in range(days)]


def generate_travel_tips(model, destination: str, month: str) -> list:
    prompt = f"""Give 5 practical travel tips for visiting {destination} in {month}.
Return ONLY a JSON array of strings:
["tip 1", "tip 2", "tip 3", "tip 4", "tip 5"]
Be specific and useful."""
    try:
        text = llm_call(model, prompt)
        text = re.sub(r'```(?:json)?', '', text).strip('`').strip()
        return json.loads(text)
    except Exception:
        return [
            f"Book accommodations in advance for {month}",
            "Keep digital and physical copies of all travel documents",
            "Learn a few phrases in the local language",
            "Get travel insurance before departure",
            "Check visa requirements at least 2 weeks ahead"
        ]


def generate_forecast_summary(model, destination: str, month: str, weather_key: str) -> str:
    if weather_key:
        return get_weather_forecast(destination, weather_key)
    prompt = f"Describe typical weather in {destination} during {month} in 3-4 bullet points. Include temperature range, rainfall, and what to pack."
    try:
        return llm_call(model, prompt)
    except Exception:
        return f"Typical {month} weather in {destination}: pleasant conditions ideal for tourism."


# ─────────────────────────────────────────────────────────────────────────────
# Main Agent Class
# ─────────────────────────────────────────────────────────────────────────────

class TripPlannerAgent:
    def __init__(
        self,
        gemini_api_key: str,
        weather_api_key: str = "",
        places_api_key: str = "",
        model: str = "gemini-1.5-flash",
        currency: str = "USD",
    ):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model)
        self.weather_key = weather_api_key
        self.places_key = places_api_key
        self.currency = currency

    def plan_trip(self, query: str, origin: str = "") -> dict:
        info = parse_trip_query(query)
        dest = info["destination"]
        days = info["days"]
        month = info["month"]

        current_weather = get_current_weather(dest, self.weather_key)
        forecast = generate_forecast_summary(self.model, dest, month, self.weather_key)
        hotels = get_hotels_from_places(dest, self.places_key)
        flights = generate_flights_with_llm(self.model, dest, origin, days, month, self.currency)
        city_overview = generate_city_overview(self.model, dest)
        day_plan = generate_day_plan(self.model, dest, days, month)
        tips = generate_travel_tips(self.model, dest, month)

        return {
            "travel_info": {
                "destination": dest,
                "duration": f"{days} Days",
                "month": month,
                "origin": origin or "Your City",
            },
            "city_overview": city_overview,
            "current_weather": current_weather,
            "forecast_summary": forecast,
            "flights": flights,
            "hotels": hotels,
            "day_plan": day_plan,
            "travel_tips": tips,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
```

---

**requirements.txt** — replace entire file with this:
```
streamlit>=1.32.0
google-generativeai>=0.7.0
requests>=2.31.0
python-dotenv>=1.0.0