import streamlit as st
import os
from dotenv import load_dotenv
from agent import TripPlannerAgent

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main-header {
    text-align: center;
    padding: 2rem 0 1rem;
}

.main-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460, #e94560);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}

.main-header p {
    color: #6b7280;
    font-size: 1.1rem;
    font-weight: 300;
}

.section-card {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}

.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: #1a1a2e;
    border-bottom: 2px solid #e94560;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
    display: inline-block;
}

.weather-badge {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    margin: 0.2rem;
}

.info-pill {
    display: inline-block;
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    color: #0369a1;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    margin: 0.2rem;
}

.stButton > button {
    background: linear-gradient(135deg, #e94560, #0f3460) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    font-size: 1rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(233,69,96,0.35) !important;
}

.sample-prompt-btn > button {
    background: #f8fafc !important;
    color: #1a1a2e !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.8rem !important;
    width: auto !important;
}

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

div[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

div[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
}

.sidebar-label {
    color: #94a3b8 !important;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.result-container {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.flight-card {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border-left: 4px solid #0284c7;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
}

.hotel-card {
    background: linear-gradient(135deg, #fdf4ff, #fae8ff);
    border-left: 4px solid #9333ea;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
}

.day-plan-card {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border-left: 4px solid #16a34a;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>✈️ AI Trip Planner</h1>
    <p>Intelligent travel planning powered by Gemini AI · Real-time weather · Live hotel & flight data</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 API Configuration")
    st.markdown('<p class="sidebar-label">Required Keys</p>', unsafe_allow_html=True)

    gemini_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        placeholder="AIza...",
        help="Get free key at: aistudio.google.com"
    )

    weather_key = st.text_input(
        "OpenWeatherMap API Key",
        value=os.getenv("OPENWEATHER_API_KEY", ""),
        type="password",
        placeholder="abc123...",
        help="Free at: openweathermap.org/api"
    )

    google_places_key = st.text_input(
        "Google Places API Key",
        value=os.getenv("GOOGLE_PLACES_API_KEY", ""),
        type="password",
        placeholder="AIza...",
        help="console.cloud.google.com"
    )

    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    model_choice = st.selectbox(
    "Gemini Model",
    ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
    index=0,
)

    currency = st.selectbox("Currency", ["USD", "INR", "EUR", "GBP"], index=0)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.78rem; color:#94a3b8; line-height:1.6">
    <b>📖 How to get free API keys:</b><br>
    • <b>Gemini:</b> aistudio.google.com<br>
    • <b>Weather:</b> openweathermap.org<br>
    • <b>Places:</b> console.cloud.google.com<br><br>
    All have generous free tiers.
    </div>
    """, unsafe_allow_html=True)

# ─── Sample Prompts ──────────────────────────────────────────────────────────
st.markdown("#### 💡 Sample Prompts — click to try:")
col1, col2, col3, col4 = st.columns(4)

sample_prompts = [
    "Plan a 3-day trip to Tokyo in May",
    "Plan a 2-day trip to Udaipur in May",
    "Plan a 5-day trip to Paris in July",
    "Plan a 4-day trip to New York in December",
]

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

with col1:
    st.markdown('<div class="sample-prompt-btn">', unsafe_allow_html=True)
    if st.button("🗼 Tokyo 3-day"):
        st.session_state.user_input = sample_prompts[0]
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.button("🏯 Udaipur 2-day"):
        st.session_state.user_input = sample_prompts[1]

with col3:
    if st.button("🗽 Paris 5-day"):
        st.session_state.user_input = sample_prompts[2]

with col4:
    if st.button("🌆 New York 4-day"):
        st.session_state.user_input = sample_prompts[3]

# ─── Input ───────────────────────────────────────────────────────────────────
st.markdown("")
user_query = st.text_input(
    "📝 Describe your trip:",
    value=st.session_state.user_input,
    placeholder="e.g. Plan a 3-day trip to Tokyo in May",
    label_visibility="visible"
)

origin_city = st.text_input(
    "🛫 Your departure city (for flight search):",
    placeholder="e.g. Mumbai, Delhi, New York",
    value=os.getenv("DEFAULT_ORIGIN", "")
)

plan_btn = st.button("🚀 Plan My Trip!", use_container_width=True)

# ─── Planning Logic ───────────────────────────────────────────────────────────
if plan_btn:
    if not gemini_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
    elif not user_query:
        st.error("⚠️ Please enter a trip description.")
    else:
        with st.spinner("🤖 AI agent is researching your perfect trip..."):
            agent = TripPlannerAgent(
                gemini_api_key=gemini_key,
                weather_api_key=weather_key,
                places_api_key=google_places_key,
                model=model_choice,
                currency=currency,
            )

            try:
                result = agent.plan_trip(user_query, origin_city)
                st.session_state.last_result = result
                st.session_state.last_query = user_query
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Tip: Check your API keys and try again.")
                st.stop()

# ─── Display Results ──────────────────────────────────────────────────────────
if "last_result" in st.session_state:
    result = st.session_state.last_result
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.markdown("---")

    # City Overview
    if result.get("city_overview"):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-title">🏛️ Cultural & Historic Significance</span>', unsafe_allow_html=True)
        st.markdown(result["city_overview"])
        st.markdown('</div>', unsafe_allow_html=True)

    # Weather
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        if result.get("current_weather"):
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<span class="section-title">🌤️ Current Weather</span>', unsafe_allow_html=True)
            w = result["current_weather"]
            st.markdown(f"""
            **{w.get('city', 'N/A')}** — {w.get('description', 'N/A').title()}

            🌡️ **Temp:** {w.get('temp', 'N/A')}°C (Feels {w.get('feels_like', 'N/A')}°C)
            💧 **Humidity:** {w.get('humidity', 'N/A')}%
            🌬️ **Wind:** {w.get('wind_speed', 'N/A')} m/s
            """)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_w2:
        if result.get("forecast_summary"):
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<span class="section-title">📅 Trip Period Forecast</span>', unsafe_allow_html=True)
            st.markdown(result["forecast_summary"])
            st.markdown('</div>', unsafe_allow_html=True)

    # Travel Info
    if result.get("travel_info"):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-title">📋 Trip Details</span>', unsafe_allow_html=True)
        info = result["travel_info"]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📍 Destination", info.get("destination", "N/A"))
        with c2:
            st.metric("📆 Duration", info.get("duration", "N/A"))
        with c3:
            st.metric("🗓️ Travel Month", info.get("month", "N/A"))
        st.markdown('</div>', unsafe_allow_html=True)

    # Flights
    if result.get("flights"):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-title">✈️ Flight Options</span>', unsafe_allow_html=True)
        for f in result["flights"]:
            st.markdown(f"""
            <div class="flight-card">
            ✈️ <b>{f.get('airline', 'N/A')}</b> &nbsp;|&nbsp;
            🛫 {f.get('departure', 'N/A')} → 🛬 {f.get('arrival', 'N/A')} &nbsp;|&nbsp;
            ⏱️ {f.get('duration', 'N/A')} &nbsp;|&nbsp;
            💰 <b>{f.get('price', 'N/A')}</b> &nbsp;|&nbsp;
            🪑 {f.get('class', 'Economy')}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Hotels
    if result.get("hotels"):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-title">🏨 Hotel Options</span>', unsafe_allow_html=True)
        for h in result["hotels"]:
            stars = "⭐" * int(h.get('stars', 3))
            st.markdown(f"""
            <div class="hotel-card">
            🏨 <b>{h.get('name', 'N/A')}</b> {stars}<br>
            📍 {h.get('area', 'N/A')} &nbsp;|&nbsp;
            💰 {h.get('price_per_night', 'N/A')}/night &nbsp;|&nbsp;
            ✅ {h.get('highlights', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Day-by-Day Plan
    if result.get("day_plan"):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-title">🗺️ Day-by-Day Itinerary</span>', unsafe_allow_html=True)
        for day in result["day_plan"]:
            st.markdown(f"""
            <div class="day-plan-card">
            <b>📅 {day.get('day', 'Day')}</b><br>
            🌅 <b>Morning:</b> {day.get('morning', '')}<br>
            ☀️ <b>Afternoon:</b> {day.get('afternoon', '')}<br>
            🌙 <b>Evening:</b> {day.get('evening', '')}<br>
            🍽️ <b>Food Tip:</b> {day.get('food', '')}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tips
    if result.get("travel_tips"):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-title">💡 Travel Tips</span>', unsafe_allow_html=True)
        for tip in result["travel_tips"]:
            st.markdown(f"• {tip}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Download
    import json
    st.download_button(
        "⬇️ Download Trip Plan (JSON)",
        data=json.dumps(result, indent=2),
        file_name=f"trip_plan_{result.get('travel_info', {}).get('destination', 'trip').replace(' ', '_')}.json",
        mime="application/json"
    )
