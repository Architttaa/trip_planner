# ✈️ AI Trip Planner — Setup Guide

## Tech Stack
| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| LLM | Google Gemini (gemini-1.5-flash / pro) |
| Agent Framework | LangChain |
| Weather | OpenWeatherMap API |
| Hotels | Google Places API |
| Flights | LLM-generated (realistic) |

---

## 🚀 Quick Start (5 minutes)

### Step 1 — Clone & install
```bash
cd trip_planner
pip install -r requirements.txt
```

### Step 2 — Set up API keys
```bash
cp .env.example .env
# Edit .env with your keys (see below)
```

### Step 3 — Run
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

---

## 🔑 API Keys (all free tiers available)

### 1. Gemini API Key (REQUIRED)
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy key → paste in `.env` as `GEMINI_API_KEY`

### 2. OpenWeatherMap (OPTIONAL — enables live weather)
1. Register at https://openweathermap.org/api
2. Go to "My API Keys" → copy default key
3. Paste in `.env` as `OPENWEATHER_API_KEY`
4. Free tier: 1,000 calls/day

### 3. Google Places API (OPTIONAL — enables real hotel search)
1. Go to https://console.cloud.google.com
2. Create a project → Enable "Places API"
3. Create credentials → API Key
4. Paste in `.env` as `GOOGLE_PLACES_API_KEY`
5. Free: $200/month credit (plenty for personal use)

> **Note**: Without optional keys, the app uses realistic mock data and Gemini-generated content — still very useful!

---

## 💬 Sample Prompts
- `Plan a 3-day trip to Tokyo in May`
- `Plan a 2-day trip to Udaipur in May`
- `Plan a 5-day trip to Paris in July`
- `Plan a 4-day trip to New York in December`
- `Plan a 7-day trip to Bali in August`

---

## 📁 File Structure
```
trip_planner/
├── app.py           # Streamlit UI
├── agent.py         # LangChain agent + API integrations
├── requirements.txt # Python dependencies
├── .env.example     # Template for environment variables
└── README.md        # This file
```

---

## 🛠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Gemini auth error | Check your `GEMINI_API_KEY` in `.env` |
| Weather shows "mock" | Add `OPENWEATHER_API_KEY` to `.env` |
| Hotels show "mock" | Add `GOOGLE_PLACES_API_KEY` to `.env` |
| Slow response | Switch to `gemini-1.5-flash` in sidebar |
