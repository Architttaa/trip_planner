import re
import json
import requests
from google import genai
from datetime import datetime


def llm_call(client, model_name: str, prompt: str) -> str:
    response = client.models.generate_content(model=model_name, contents=prompt)
    return response.text.strip()


def get_current_weather(city: str, api_key: str) -> dict:
    if not api_key:
        return _mock_weather(city)
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        resp = requests.get(url, params={"q": city, "appid": api_key, "units": "metric"}, timeout=8)
        if resp.status_code == 200:
            d = resp.json()
            return {
                "city": d["name"], "country": d["sys"]["country"],
                "temp": round(d["main"]["temp"], 1), "feels_like": round(d["main"]["feels_like"], 1),
                "description": d["weather"][0]["description"], "humidity": d["main"]["humidity"],
                "wind_speed": d["wind"]["speed"], "source": "live"
            }
    except Exception:
        pass
    return _mock_weather(city)


def get_weather_forecast(city: str, api_key: str) -> str:
    if not api_key:
        return _mock_forecast(city)
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        resp = requests.get(url, params={"q": city, "appid": api_key, "units": "metric", "cnt": 5}, timeout=8)
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


def get_hotels_from_places(city: str, api_key: str) -> list:
    if not api_key:
        return _mock_hotels(city)
    try:
        search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        resp = requests.get(search_url, params={
            "query": f"best hotels in {city}", "type": "lodging", "key": api_key,
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


def generate_flights_with_llm(client, model_name, destination, origin, days, month, currency) -> list:
    prompt = f"""You are a travel expert. Generate 3 realistic flight options from {origin or 'major hub'} to {destination} in {month} for {days} days.
Return ONLY a valid JSON array (no markdown):
[{{"airline":"Air India","departure":"09:30","arrival":"14:45","duration":"5h 15m","price":"{currency} 450","class":"Economy","stops":"Direct"}}]
Make prices realistic for {currency}. Include 1 direct and 2 with 1 stop."""
    try:
        text = llm_call(client, model_name, prompt)
        text = re.sub(r'```(?:json)?', '', text).strip('`').strip()
        return json.loads(text)
    except Exception:
        return [
            {"airline": "Major Carrier", "departure": "08:00", "arrival": "16:00", "duration": "8h", "price": f"{currency} 400", "class": "Economy", "stops": "Direct"},
            {"airline": "Budget Airline", "departure": "22:00", "arrival": "10:00+1", "duration": "12h", "price": f"{currency} 250", "class": "Economy", "stops": "1 Stop"},
        ]


def generate_city_overview(client, model_name, destination) -> str:
    prompt = f"Write ONE compelling paragraph (100-150 words) about {destination}'s cultural and historic significance. Cover history, landmarks, heritage. Be vivid. No headers."
    try:
        return llm_call(client, model_name, prompt)
    except Exception:
        return f"{destination} is a fascinating destination rich in history and culture."


def generate_day_plan(client, model_name, destination, days, month) -> list:
    prompt = f"""Create a {days}-day itinerary for {destination} in {month}.
Return ONLY a valid JSON array (no markdown):
[{{"day":"Day 1 - Arrival","morning":"activity","afternoon":"activity","evening":"activity","food":"recommendation"}}]
Use real places specific to {destination}."""
    try:
        text = llm_call(client, model_name, prompt)
        text = re.sub(r'```(?:json)?', '', text).strip('`').strip()
        return json.loads(text)
    except Exception:
        return [{"day": f"Day {i+1}", "morning": "Sightseeing", "afternoon": "Local exploration", "evening": "Dinner", "food": "Local specialty"} for i in range(days)]


def generate_travel_tips(client, model_name, destination, month) -> list:
    prompt = f"""Give 5 practical travel tips for {destination} in {month}.
Return ONLY a JSON array: ["tip 1", "tip 2", "tip 3", "tip 4", "tip 5"]"""
    try:
        text = llm_call(client, model_name, prompt)
        text = re.sub(r'```(?:json)?', '', text).strip('`').strip()
        return json.loads(text)
    except Exception:
        return ["Book in advance", "Carry travel insurance", "Learn basic local phrases", "Keep document copies", "Check visa requirements"]


def generate_forecast_summary(client, model_name, destination, month, weather_key) -> str:
    if weather_key:
        return get_weather_forecast(destination, weather_key)
    prompt = f"Describe typical weather in {destination} during {month} in 3-4 bullet points. Include temperature range, rainfall, what to pack."
    try:
        return llm_call(client, model_name, prompt)
    except Exception:
        return f"Typical {month} weather in {destination}: pleasant conditions ideal for tourism."


class TripPlannerAgent:
    def __init__(self, gemini_api_key, weather_api_key="", places_api_key="", model="gemini-2.0-flash", currency="USD"):
        self.client = genai.Client(api_key=gemini_api_key)
        self.model_name = model
        self.weather_key = weather_api_key
        self.places_key = places_api_key
        self.currency = currency

    def plan_trip(self, query: str, origin: str = "") -> dict:
        info = parse_trip_query(query)
        dest, days, month = info["destination"], info["days"], info["month"]
        c, m = self.client, self.model_name

        return {
            "travel_info": {"destination": dest, "duration": f"{days} Days", "month": month, "origin": origin or "Your City"},
            "city_overview": generate_city_overview(c, m, dest),
            "current_weather": get_current_weather(dest, self.weather_key),
            "forecast_summary": generate_forecast_summary(c, m, dest, month, self.weather_key),
            "flights": generate_flights_with_llm(c, m, dest, origin, days, month, self.currency),
            "hotels": get_hotels_from_places(dest, self.places_key),
            "day_plan": generate_day_plan(c, m, dest, days, month),
            "travel_tips": generate_travel_tips(c, m, dest, month),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }