import streamlit as st
import httpx
import requests
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from typing import Dict, Any

# AI-powered functions for real backend integration
async def call_anywhere_search_api(budget: int, preferences: Dict[str, Any], api_url: str) -> Dict[str, Any]:
    """Call the AI-powered anywhere search API"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_url}/anywhere-search",
                json={
                    "budget": budget,
                    "climate": preferences.get("climate"),
                    "visa_free": preferences.get("visa_free", True),
                    "safety_importance": preferences.get("safety_importance", 7),
                    "cost_preference": preferences.get("cost_preference", "Medium"),
                    "interests": preferences.get("interests", [])
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"AI service error: {e}")
        return None

async def call_ai_chat_api(message: str, conversation_history: list, api_url: str) -> str:
    """Call the AI chat assistant API"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_url}/chat",
                json={
                    "message": message,
                    "conversation_history": conversation_history
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "Sorry, I couldn't process that request.")
    except Exception as e:
        st.error(f"AI chat error: {e}")
        return "I'm having trouble connecting to my AI brain right now. Please try again!"

async def get_travel_insights_api(api_url: str, route: str = "global") -> list:
    """Get AI-generated travel insights"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{api_url}/travel-insights?route={route}")
            response.raise_for_status()
            result = response.json()
            return result.get("insights", [])
    except Exception as e:
        return [
            "✈️ Flight prices typically vary by 20-40% based on booking timing",
            "🌤️ Weather patterns can significantly impact flight schedules",
            "💰 Tuesday and Wednesday flights are often 15-25% cheaper",
            "📱 Clear browser cookies between searches to avoid price tracking"
        ]

# Configure the page
st.set_page_config(
    page_title="✈️ SmartAir - Smart Flight Search",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .flight-card {
        border: 2px solid #e1e5e9;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .cheapest-flight-card {
        border: 2px solid #28a745;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 6px 12px rgba(40, 167, 69, 0.2);
        transition: transform 0.2s ease;
    }
    .cheapest-flight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(40, 167, 69, 0.3);
    }
    .shortest-flight-card {
        border: 2px solid #007bff;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 6px 12px rgba(0, 123, 255, 0.2);
        transition: transform 0.2s ease;
    }
    .shortest-flight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 123, 255, 0.3);
    }
    .price-tag {
        font-size: 2rem;
        font-weight: bold;
        color: #28a745;
    }
    .price-tag-shortest {
        font-size: 2rem;
        font-weight: bold;
        color: #0056b3;
    }
    .duration-tag {
        font-size: 1.5rem;
        color: #007bff;
        font-weight: bold;
    }
    .duration-tag-cheapest {
        font-size: 1.5rem;
        color: #1e7e34;
        font-weight: bold;
    }
    .airline-tag {
        background: #6c757d;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    .stProgress .st-bo {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown(
        """
        <div style="padding-left: 85px;">
            <img src="https://www.freeiconspng.com/uploads/plane-travel-flight-tourism-travel-icon-png-10.png" width="100">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h1 style='padding-left: 40px;'>🛫 Flight Search</h1>", unsafe_allow_html=True)
    # st.title("🛫 Flight Search")
    st.markdown("---")
    
    # Search parameters
    st.subheader("✈️ Search Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("🛫 Origin (IATA)", value="DEL", max_chars=3, help="3-letter airport code (e.g., DEL, BOM)")
    with col2:
        destination = st.text_input("🛬 Destination (IATA)", value="HYD", max_chars=3, help="3-letter airport code (e.g., HYD, BLR)")
    
    months = st.slider("📅 Search Period (months)", min_value=1, max_value=6, value=3, help="Number of months to search for flights")
    
    # Add quick search option
    quick_search = st.checkbox("⚡ Quick Search (1 month only)", help="For faster results, search only 1 month")
    if quick_search:
        months = 1
        st.info("⚡ Quick search enabled - searching 1 month for faster results")
    
    st.markdown("---")
    
    # API Configuration
    st.subheader("⚙️ API Settings")
    api_base_url = st.text_input("🌐 API Base URL", value="http://127.0.0.1:8001", help="Your FastAPI server URL")
    
    # Search button
    search_button = st.button("🔍 Search Flights", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")

# Main content area
st.markdown('<h1 class="main-header">✈️ SmartAir - Next-Gen Travel Intelligence</h1>', unsafe_allow_html=True)

# Revolutionary feature tabs
tab1, tab2, tab3 = st.tabs(["✈️ Flight Search", "🌍 Anywhere Search", "🤖 AI Travel Assistant"])

with tab1:
    # Traditional flight search
    st.markdown("### 🌟 Popular Routes")
    popular_routes = [
        {"route": "DEL → HYD", "origin": "DEL", "destination": "HYD"},
        {"route": "BOM → BLR", "origin": "BOM", "destination": "BLR"},
        {"route": "DEL → BOM", "origin": "DEL", "destination": "BOM"},
        {"route": "CCU → DEL", "origin": "CCU", "destination": "DEL"},
    ]

    cols = st.columns(4)
    for i, route in enumerate(popular_routes):
        with cols[i]:
            if st.button(route["route"], key=f"route_{i}", use_container_width=True):
                origin = route["origin"]
                destination = route["destination"]
                st.rerun()

with tab2:
    # Revolutionary Anywhere Search
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; text-align: center; margin: 0;">🌍 Anywhere Search</h2>
        <p style="color: white; text-align: center; font-size: 1.1rem; margin: 0.5rem 0 0 0;">
            Revolutionary AI-powered destination discovery
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💡 What Makes This Revolutionary?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; border-radius: 10px; background: #f8f9fa;">
            <h4>🧠 AI-Powered Matching</h4>
            <p>Our AI analyzes your preferences and finds destinations you'll love</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; border-radius: 10px; background: #f8f9fa;">
            <h4>💰 Budget Optimization</h4>
            <p>Maximize your travel experience within any budget</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; border-radius: 10px; background: #f8f9fa;">
            <h4>🌍 Global Discovery</h4>
            <p>Discover hidden gems you never knew existed</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Anywhere Search Interface
    st.markdown("### 🎯 Tell Us Your Preferences")
    
    anywhere_col1, anywhere_col2 = st.columns([2, 1])
    
    with anywhere_col1:
        budget = st.slider("💰 Your Total Budget (USD)", 300, 3000, 800, 50)
        
        pref_col1, pref_col2 = st.columns(2)
        with pref_col1:
            climate = st.selectbox("🌡️ Preferred Climate", 
                                 ["Any", "Tropical", "Mediterranean", "Temperate", "Desert"])
            visa_free = st.checkbox("✈️ Visa-free only", True)
        
        with pref_col2:
            safety_score = st.slider("🛡️ Safety Priority (1-10)", 1, 10, 7)
            cost_living = st.selectbox("💸 Cost Preference", ["Low", "Medium", "High"], 1)
        
        interests = st.multiselect("🎨 Your Interests", 
                                 ["Food", "Culture", "History", "Adventure", "Nature", "Art", 
                                  "Nightlife", "Beaches", "Architecture"], 
                                 ["Food", "Culture"])
    
    with anywhere_col2:
        st.markdown("#### 🎯 Your Profile")
        st.info(f"💰 Budget: ${budget:,}")
        st.info(f"🌡️ Climate: {climate}")
        st.info(f"🛡️ Safety: {safety_score}/10")
        st.info(f"✈️ Visa-free: {'Yes' if visa_free else 'Any'}")
        st.info(f"🎨 {len(interests)} interests selected")
    
    if st.button("🔍 Discover Amazing Destinations", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is analyzing global destinations..."):
            try:
                # Prepare preferences for AI
                preferences = {
                    "climate": climate if climate != "Any" else None,
                    "visa_free": visa_free,
                    "safety_importance": safety_score,
                    "cost_preference": cost_living,
                    "interests": interests
                }
                
                # Call real AI backend
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                ai_result = loop.run_until_complete(
                    call_anywhere_search_api(budget, preferences, api_base_url)
                )
                loop.close()
                
                if ai_result and ai_result.get("destinations"):
                    destinations_data = ai_result["destinations"]
                    
                    # Convert to expected format
                    destinations = []
                    for dest in destinations_data:
                        destinations.append({
                            "city": dest.get("city", "Unknown"),
                            "country": dest.get("country", "Unknown"),
                            "cost": dest.get("total_estimated_cost", budget),
                            "match": dest.get("match_score", 75),
                            "highlights": dest.get("highlights", []),
                            "why_recommended": dest.get("why_recommended", ""),
                            "insider_tip": dest.get("insider_tip", ""),
                            "best_time": dest.get("best_time", "Year-round")
                        })
                else:
                    # Fallback destinations if AI fails
                    destinations = [
                        {"city": "Prague", "country": "Czech Republic", "cost": 650, "match": 92, 
                         "highlights": ["Architecture", "History", "Culture"],
                         "why_recommended": "Perfect blend of culture and affordability",
                         "insider_tip": "Visit during shoulder season for better prices",
                         "best_time": "April-October"},
                        {"city": "Lisbon", "country": "Portugal", "cost": 580, "match": 88, 
                         "highlights": ["Food", "Culture", "Coastline"],
                         "why_recommended": "Coastal charm with excellent value",
                         "insider_tip": "Get Lisboa Card for free transport",
                         "best_time": "March-May, Sept-Nov"},
                    ]
                    st.warning("🤖 AI service temporarily unavailable - showing curated recommendations")
                
            except Exception as e:
                st.error(f"Error getting AI recommendations: {e}")
                destinations = []
            
            st.success(f"✨ Found {len(destinations)} perfect matches!")
            
            # Results metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Best Deal", f"${min(d['cost'] for d in destinations)}")
            with col2:
                st.metric("🎯 Top Match", f"{max(d['match'] for d in destinations)}%")
            with col3:
                st.metric("💵 Avg Savings", "$200")
            with col4:
                st.metric("🌍 Countries", f"{len(set(d['country'] for d in destinations))}")
            
            # Display AI-enhanced results
            for i, dest in enumerate(destinations):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="border: 2px solid #28a745; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; background: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        <h4 style="color: black;">{i+1}. {dest['city']}, {dest['country']}</h4>
                        
                        <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                            <div>
                                <span style="background: #28a745; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;">
                                    🎯 {dest['match']}% AI Match
                                </span>
                                <span style="background: #007bff; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; margin-left: 0.5rem; font-size: 0.9rem;">
                                    💰 ${dest['cost']} Total
                                </span>
                                <span style="background: #6f42c1; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; margin-left: 0.5rem; font-size: 0.9rem;">
                                    📅 {dest.get('best_time', 'Year-round')}
                                </span>
                            </div>
                        </div>
                        
                        <div style="margin: 1rem 0; padding: 0.8rem; background: #f8f9fa; border-radius: 8px;">
                            <p style="color: #495057; margin: 0; font-weight: 500;">
                                <strong>🎨 Highlights:</strong> {' • '.join(dest['highlights'])}
                            </p>
                        </div>
                        
                        {f'''<div style="margin: 1rem 0; padding: 0.8rem; background: #e8f5e8; border-radius: 8px; border-left: 4px solid #28a745;">
                            <p style="color: #155724; margin: 0; font-style: italic;">
                                <strong>🤖 AI Insight:</strong> {dest.get('why_recommended', 'Great choice for your preferences!')}
                            </p>
                        </div>''' if dest.get('why_recommended') else ''}
                        
                        {f'''<div style="margin: 1rem 0; padding: 0.8rem; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
                            <p style="color: #856404; margin: 0;">
                                <strong>💡 Insider Tip:</strong> {dest.get('insider_tip', 'Book 4-6 weeks in advance for best prices!')}
                            </p>
                        </div>''' if dest.get('insider_tip') else ''}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"✈️ Book {dest['city']}", key=f"book_{i}", use_container_width=True):
                        st.success(f"🎉 Redirecting to book {dest['city']}...")
                    
                    if st.button(f"ℹ️ More Info", key=f"info_{i}", use_container_width=True):
                        with st.expander(f"📖 {dest['city']} Details", expanded=True):
                            st.markdown(f"""
                            **🌍 Destination:** {dest['city']}, {dest['country']}
                            **💰 Estimated Cost:** ${dest['cost']}
                            **🎯 Match Score:** {dest['match']}%
                            **📅 Best Time:** {dest.get('best_time', 'Year-round')}
                            **🎨 Main Attractions:** {', '.join(dest['highlights'])}
                            
                            {f"**🤖 Why AI Recommends:** {dest.get('why_recommended', 'Perfect for your travel style!')}" if dest.get('why_recommended') else ''}
                            
                            {f"**💡 Pro Tip:** {dest.get('insider_tip', 'Book early for best deals!')}" if dest.get('insider_tip') else ''}
                            """)

with tab3:
    # AI Travel Assistant

    # --- Modern AI Travel Assistant Redesign ---
    st.markdown("""
    <style>
    .ai-header {
        background: linear-gradient(135deg, #4f8cff 0%, #6edfff 100%);
        padding: 2rem 1rem 1rem 1rem;
        border-radius: 18px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 24px rgba(80,140,255,0.12);
    }
    .ai-title {
        color: white;
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        letter-spacing: 1px;
    }
    .ai-subtitle {
        color: #eaf6ff;
        text-align: center;
        font-size: 1.15rem;
        margin-bottom: 0.5rem;
    }
    .chat-bubble {
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(80,140,255,0.07);
        position: relative;
        animation: fadeIn 0.7s;
    }
    .chat-bubble.ai {
        background: linear-gradient(135deg, #3578e5 0%, #4f8cff 100%);
        border-left: 6px solid #3578e5;
        color: #fff;
    }
    .chat-bubble.user {
        background: linear-gradient(135deg, #ffe082 0%, #ffd54f 100%);
        border-right: 6px solid #ffb300;
        color: #222;
    }
    .avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 0.7rem;
        vertical-align: middle;
        box-shadow: 0 2px 8px rgba(80,140,255,0.10);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .sidebar-tip {
        background: #eaf6ff;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #4f8cff;
        font-size: 1rem;
        box-shadow: 0 2px 8px rgba(80,140,255,0.07);
    }
    </style>
    <div class="ai-header">
        <div class="ai-title">🤖 AI Travel Assistant</div>
        <div class="ai-subtitle">Your personal travel expert powered by advanced AI</div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-tip">
        <b>💡 Pro Tips:</b><br>
        • Ask about destinations, budgets, or travel hacks<br>
        • Try "Show me hidden gems in Japan"<br>
        • Use the quick actions below for inspiration!
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

    st.markdown("#### ✨ Quick Actions")
    quick_queries = [
        "Best solo travel spots for 2025",
        "Luxury escapes under $3000",
        "Family-friendly beach destinations",
        "Adventure trips for foodies"
    ]
    quick_cols = st.columns(len(quick_queries))
    for i, query in enumerate(quick_queries):
        with quick_cols[i]:
            if st.button(f"💡 {query}", key=f"quick_{i}", use_container_width=True):
                with st.spinner(f"🤖 AI is analyzing: '{query}'..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    ai_response = loop.run_until_complete(
                        call_ai_chat_api(query, [], api_base_url)
                    )
                    loop.close()
                    st.markdown(f"<div class='chat-bubble ai'><img src='https://cdn-icons-png.flaticon.com/512/4712/4712027.png' class='avatar'/> <b>AI:</b> {ai_response}</div>", unsafe_allow_html=True)

    st.markdown("#### �️ Conversation")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show chat bubbles for last 5 messages
    for chat in st.session_state.chat_history[-5:]:
        st.markdown(f"<div class='chat-bubble user'><img src='https://cdn-icons-png.flaticon.com/512/1946/1946429.png' class='avatar'/> <b>You:</b> {chat['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-bubble ai'><img src='https://cdn-icons-png.flaticon.com/512/4712/4712027.png' class='avatar'/> <b>AI:</b> {chat['assistant']}</div>", unsafe_allow_html=True)

    # Chat input

    # Use a clear flag to reset input after send
    if "clear_chat_input" not in st.session_state:
        st.session_state.clear_chat_input = False

    chat_input_value = "" if st.session_state.clear_chat_input else st.session_state.get("chat_input_modern", "")
    user_input = st.text_area(
        "✍️ Type your travel question:", 
        value=chat_input_value,
        placeholder="e.g., 'Find me a beach destination for Christmas under $1200'",
        height=80,
        key="chat_input_modern"
    )
    if st.session_state.clear_chat_input:
        st.session_state.clear_chat_input = False

    chat_cols = st.columns([4,1])
    with chat_cols[0]:
        if st.button("🚀 Send to AI", type="primary", use_container_width=True):
            if user_input.strip():
                with st.spinner("🤖 AI Travel Expert is thinking..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    ai_response = loop.run_until_complete(
                        call_ai_chat_api(user_input, st.session_state.chat_history[-5:], api_base_url)
                    )
                    loop.close()
                    st.session_state.chat_history.append({
                        "user": user_input,
                        "assistant": ai_response
                    })
                    st.session_state.clear_chat_input = True  # Set flag to clear input
                    st.rerun()
            else:
                st.warning("Please enter a question for the AI assistant!")
    with chat_cols[1]:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

async def fetch_flights(origin: str, destination: str, months: int, api_url: str) -> Dict[str, Any]:
    """Fetch flight data from the FastAPI backend"""
    # Increase timeout based on number of months (more months = more time needed)
    timeout_seconds = 60 + (months * 30)  # Base 60s + 30s per month
    
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.get(
            f"{api_url}/search",
            params={"origin": origin, "destination": destination, "months": months}
        )
        response.raise_for_status()
        return response.json()

def format_duration(duration_str: str) -> str:
    """Format duration string for display"""
    duration_str = duration_str.replace("PT", "")
    if "H" in duration_str and "M" in duration_str:
        parts = duration_str.split("H")
        hours = parts[0]
        minutes = parts[1].replace("M", "")
        return f"{hours}h {minutes}m"
    elif "H" in duration_str:
        return duration_str.replace("H", "h")
    elif "M" in duration_str:
        return duration_str.replace("M", "m")
    return duration_str

def display_flight_card(flight_data: Dict[str, Any], title: str, icon: str, card_type: str = "default"):
    """Display a beautiful flight card with different background colors"""
    
    # Choose CSS class based on card type
    if card_type == "cheapest":
        css_class = "cheapest-flight-card"
    elif card_type == "shortest":
        css_class = "shortest-flight-card"
    else:
        css_class = "flight-card"
    
    # Extract detailed flight information
    full_details = flight_data.get('full_details', {})
    itinerary = full_details.get('itineraries', [{}])[0] if full_details.get('itineraries') else {}
    segments = itinerary.get('segments', [])
    
    # Build route information
    route_info = ""
    if segments:
        route_parts = []
        for i, segment in enumerate(segments):
            departure = segment.get('departure', {})
            arrival = segment.get('arrival', {})
            dept_time = departure.get('at', '').split('T')[1][:5] if departure.get('at') else 'N/A'
            arr_time = arrival.get('at', '').split('T')[1][:5] if arrival.get('at') else 'N/A'
            route_parts.append(f"{departure.get('iataCode', 'N/A')} {dept_time} → {arrival.get('iataCode', 'N/A')} {arr_time}")
        route_info = " | ".join(route_parts)
    
    st.markdown(f"""
    <div class="{css_class}">
        <h3 style="color: black;">{icon} {title}</h3>
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;">
            <div>
                <div class="price-tag">${flight_data['price']} {flight_data['currency']}</div>
                <div style="color: #6c757d;">💰 Best Price</div>
            </div>
            <div style="text-align: center;">
                <div class="duration-tag">{format_duration(flight_data['duration'])}</div>
                <div style="color: #6c757d;">⏱️ Flight Time</div>
            </div>
            <div style="text-align: right;">
                <span class="airline-tag">✈️ {flight_data['airline']}</span>
                <div style="color: #6c757d; margin-top: 0.5rem;">🗓️ {flight_data['departure_date']}</div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 1rem; color: black;">
            <div><strong>🔄 Segments:</strong> {flight_data['segments']}</div>
            <div><strong>🎯 Stops:</strong> {flight_data['segments'] - 1} stop(s)</div>
        </div>
        <div style="margin-top: 1rem; padding: 0.5rem; background: #f8f9fa; border-radius: 5px; font-size: 0.9rem; color: black;">
            <strong>🛫 Route:</strong> {route_info if route_info else 'Route details not available'}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main search functionality
if search_button and origin and destination:
    if len(origin) != 3 or len(destination) != 3:
        st.error("❌ Please enter valid 3-letter IATA airport codes")
    else:
        with st.spinner("🔍 Searching for the best flights..."):
            try:
                # Calculate expected time and show to user
                expected_time = 10 + (months * 20)  # Rough estimate: 10s base + 20s per month
                st.info(f"⏱️ Expected search time: ~{expected_time} seconds for {months} month(s) of data")
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Show more realistic progress based on expected time
                import time
                progress_steps = 50  # Number of progress updates
                step_time = expected_time / progress_steps / 2  # Divide by 2 to make it faster than actual
                
                for i in range(progress_steps):
                    progress_bar.progress((i + 1) / progress_steps)
                    if i < progress_steps * 0.1:
                        status_text.text("🔑 Authenticating with Amadeus API...")
                    elif i < progress_steps * 0.8:
                        status_text.text(f"🌐 Searching flights across {months} month(s)...")
                    else:
                        status_text.text("🧮 Analyzing best options...")
                    time.sleep(step_time)
                
                status_text.text("✅ Finalizing results...")
                
                # Fetch actual data
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                flight_data = loop.run_until_complete(
                    fetch_flights(origin, destination, months, api_base_url)
                )
                loop.close()
                
                progress_bar.empty()
                status_text.empty()
                
                # Display results
                st.success(f"✅ Found {flight_data['total_flights_found']} flights for {origin} → {destination}")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3>🔍 Total Flights</h3>
                        <h2>{flight_data['total_flights_found']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3>💰 Best Price</h3>
                        <h2>${flight_data['cheapest_flight']['price']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3>⚡ Shortest</h3>
                        <h2>{format_duration(flight_data['shortest_flight']['duration'])}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3>📅 Search Period</h3>
                        <h2>{flight_data['search_period']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Flight comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    display_flight_card(flight_data['cheapest_flight'], "💰 Cheapest Flight", "💸", "cheapest")
                
                with col2:
                    display_flight_card(flight_data['shortest_flight'], "⚡ Shortest Flight", "🚀", "shortest")
                
                # Detailed Flight Information Summary
                st.markdown("### ✈️ Flight Details Summary")
                
                def display_detailed_flight_info(flight_info, title, icon):
                    with st.expander(f"{icon} {title} - Click to expand details"):
                        full_details = flight_info.get('full_details', {})
                        
                        # Basic Information
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("💰 Price", f"${flight_info['price']} {flight_info['currency']}")
                            st.metric("📅 Date", flight_info['departure_date'])
                        with col2:
                            st.metric("⏱️ Duration", format_duration(flight_info['duration']))
                            st.metric("✈️ Airline", flight_info['airline'])
                        with col3:
                            st.metric("🔄 Segments", flight_info['segments'])
                            st.metric("🎯 Stops", f"{flight_info['segments'] - 1}")
                        
                        # Flight segments details
                        if full_details.get('itineraries'):
                            itinerary = full_details['itineraries'][0]
                            segments = itinerary.get('segments', [])
                            
                            st.markdown("#### 🛫 Flight Segments")
                            for i, segment in enumerate(segments, 1):
                                departure = segment.get('departure', {})
                                arrival = segment.get('arrival', {})
                                
                                dept_time = departure.get('at', '').replace('T', ' ').split('.')[0] if departure.get('at') else 'N/A'
                                arr_time = arrival.get('at', '').replace('T', ' ').split('.')[0] if arrival.get('at') else 'N/A'
                                
                                st.markdown(f"""
                                **Segment {i}:**
                                - **Route**: {departure.get('iataCode', 'N/A')} → {arrival.get('iataCode', 'N/A')}
                                - **Departure**: {dept_time} (Terminal {departure.get('terminal', 'N/A')})
                                - **Arrival**: {arr_time}
                                - **Flight**: {segment.get('carrierCode', 'N/A')}-{segment.get('number', 'N/A')}
                                - **Aircraft**: {segment.get('aircraft', {}).get('code', 'N/A')}
                                - **Duration**: {format_duration(segment.get('duration', 'N/A'))}
                                """)
                        
                        # Price breakdown
                        if full_details.get('price'):
                            price_info = full_details['price']
                            st.markdown("#### 💳 Price Breakdown")
                            price_col1, price_col2 = st.columns(2)
                            with price_col1:
                                st.write(f"**Base Price**: ${price_info.get('base', 'N/A')}")
                                st.write(f"**Total**: ${price_info.get('total', 'N/A')}")
                            with price_col2:
                                st.write(f"**Currency**: {price_info.get('currency', 'N/A')}")
                                st.write(f"**Grand Total**: ${price_info.get('grandTotal', price_info.get('total', 'N/A'))}")
                        
                        # Baggage and amenities
                        if full_details.get('travelerPricings'):
                            traveler = full_details['travelerPricings'][0]
                            if traveler.get('fareDetailsBySegment'):
                                st.markdown("#### 🎒 Baggage & Amenities")
                                for segment_detail in traveler['fareDetailsBySegment']:
                                    if segment_detail.get('includedCheckedBags'):
                                        baggage = segment_detail['includedCheckedBags']
                                        st.write(f"**Checked Baggage**: {baggage.get('weight', 'N/A')} {baggage.get('weightUnit', 'KG')}")
                                    
                                    if segment_detail.get('cabin'):
                                        st.write(f"**Cabin Class**: {segment_detail['cabin']}")
                                    
                                    if segment_detail.get('amenities'):
                                        amenities = [amenity['description'] for amenity in segment_detail['amenities'][:3]]
                                        st.write(f"**Amenities**: {', '.join(amenities)}")
                
                # Display detailed info for both flights
                col1, col2 = st.columns(2)
                with col1:
                    display_detailed_flight_info(flight_data['cheapest_flight'], "💰 Cheapest Flight Details", "💸")
                with col2:
                    display_detailed_flight_info(flight_data['shortest_flight'], "⚡ Shortest Flight Details", "🚀")
                
                # Quick Comparison Table
                st.markdown("### 📋 Quick Comparison Table")
                comparison_df = pd.DataFrame({
                    'Flight Type': ['💰 Cheapest', '⚡ Shortest'],
                    'Price (USD)': [f"${flight_data['cheapest_flight']['price']}", f"${flight_data['shortest_flight']['price']}"],
                    'Duration': [format_duration(flight_data['cheapest_flight']['duration']), format_duration(flight_data['shortest_flight']['duration'])],
                    'Date': [flight_data['cheapest_flight']['departure_date'], flight_data['shortest_flight']['departure_date']],
                    'Airline': [flight_data['cheapest_flight']['airline'], flight_data['shortest_flight']['airline']],
                    'Segments': [flight_data['cheapest_flight']['segments'], flight_data['shortest_flight']['segments']],
                    'Stops': [f"{flight_data['cheapest_flight']['segments'] - 1}", f"{flight_data['shortest_flight']['segments'] - 1}"]
                })
                
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                
                # Comparison chart
                st.markdown("### 📊 Price vs Duration Comparison")
                
                def parse_duration_to_minutes(duration_str):
                    """Convert duration string like 'PT2H10M' to total minutes"""
                    duration_str = duration_str.replace("PT", "")
                    total_minutes = 0
                    
                    if "H" in duration_str and "M" in duration_str:
                        parts = duration_str.split("H")
                        hours = int(parts[0])
                        minutes = int(parts[1].replace("M", ""))
                        total_minutes = hours * 60 + minutes
                    elif "H" in duration_str:
                        hours = int(duration_str.replace("H", ""))
                        total_minutes = hours * 60
                    elif "M" in duration_str:
                        minutes = int(duration_str.replace("M", ""))
                        total_minutes = minutes
                    
                    return total_minutes
                
                comparison_data = {
                    'Flight Type': ['Cheapest', 'Shortest'],
                    'Price (USD)': [
                        float(flight_data['cheapest_flight']['price']),
                        float(flight_data['shortest_flight']['price'])
                    ],
                    'Duration (minutes)': [
                        parse_duration_to_minutes(flight_data['cheapest_flight']['duration']),
                        parse_duration_to_minutes(flight_data['shortest_flight']['duration'])
                    ]
                }
                
                df = pd.DataFrame(comparison_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_price = px.bar(df, x='Flight Type', y='Price (USD)', 
                                     title='💰 Price Comparison',
                                     color='Price (USD)',
                                     color_continuous_scale='viridis')
                    fig_price.update_layout(showlegend=False)
                    st.plotly_chart(fig_price, use_container_width=True)
                
                with col2:
                    fig_duration = px.bar(df, x='Flight Type', y='Duration (minutes)', 
                                        title='⏱️ Duration Comparison',
                                        color='Duration (minutes)',
                                        color_continuous_scale='plasma')
                    fig_duration.update_layout(showlegend=False)
                    st.plotly_chart(fig_duration, use_container_width=True)
                
                # Detailed flight information
                st.markdown("### 📋 Detailed Flight Information")
                
                tab1, tab2 = st.tabs(["💰 Cheapest Flight Details", "⚡ Shortest Flight Details"])
                
                with tab1:
                    st.json(flight_data['cheapest_flight']['full_details'])
                
                with tab2:
                    st.json(flight_data['shortest_flight']['full_details'])
                
                # Save results option
                st.markdown("### 💾 Export Results")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📊 Download as JSON", use_container_width=True):
                        st.download_button(
                            label="⬇️ Download JSON",
                            data=json.dumps(flight_data, indent=2),
                            file_name=f"flight_search_{origin}_{destination}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
                with col2:
                    if st.button("📈 Download as CSV", use_container_width=True):
                        csv_data = pd.DataFrame([
                            {
                                'Type': 'Cheapest',
                                'Price': flight_data['cheapest_flight']['price'],
                                'Currency': flight_data['cheapest_flight']['currency'],
                                'Duration': flight_data['cheapest_flight']['duration'],
                                'Date': flight_data['cheapest_flight']['departure_date'],
                                'Airline': flight_data['cheapest_flight']['airline'],
                                'Segments': flight_data['cheapest_flight']['segments']
                            },
                            {
                                'Type': 'Shortest',
                                'Price': flight_data['shortest_flight']['price'],
                                'Currency': flight_data['shortest_flight']['currency'],
                                'Duration': flight_data['shortest_flight']['duration'],
                                'Date': flight_data['shortest_flight']['departure_date'],
                                'Airline': flight_data['shortest_flight']['airline'],
                                'Segments': flight_data['shortest_flight']['segments']
                            }
                        ])
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=csv_data.to_csv(index=False),
                            file_name=f"flight_search_{origin}_{destination}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
            except httpx.ReadTimeout:
                st.error("⏰ **Search Timeout**")
                st.warning(f"""
                The search took longer than expected for {months} month(s) of data. This can happen when:
                - Searching many months of flight data
                - High API response times
                - Network connectivity issues
                
                **Try these solutions:**
                - Reduce the search period (try 1-2 months instead of {months})
                - Try a different route
                - Try again in a few moments
                """)
                
            except httpx.HTTPStatusError as e:
                st.error(f"❌ **API Error**: {e.response.status_code}")
                if e.response.status_code == 429:
                    st.warning("🚫 Rate limit exceeded. Please wait a moment and try again.")
                elif e.response.status_code == 401:
                    st.warning("🔑 Authentication failed. Please check your Amadeus API credentials.")
                else:
                    st.warning(f"Server returned error: {e.response.status_code}")
                    
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                
                st.error(f"❌ Error searching flights: {str(e)}")
                
                # Show detailed error in an expander for debugging
                with st.expander("🔍 Show detailed error information"):
                    st.code(error_details)
                
                # Provide helpful troubleshooting information
                st.info("💡 **Troubleshooting Tips:**")
                st.markdown("""
                - **Check API URL**: Make sure your FastAPI server is running
                - **Verify Airport Codes**: Use valid 3-letter IATA codes (DEL, HYD, BOM, etc.)
                - **Check Credentials**: Ensure your .env file has valid Amadeus API credentials
                - **Try Different Route**: Some routes might not have available flights
                
                **Current API URL**: `{}`
                """.format(api_base_url))
                
                # Add API status check
                st.markdown("### 🔧 API Status Check")
                try:
                    import requests
                    response = requests.get(f"{api_base_url}/docs", timeout=5)
                    if response.status_code == 200:
                        st.success("✅ FastAPI backend is reachable")
                    else:
                        st.error(f"❌ FastAPI backend returned status: {response.status_code}")
                except Exception as api_error:
                    st.error(f"❌ Cannot reach FastAPI backend: {str(api_error)}")
                    st.markdown("""
                    **To fix this:**
                    1. Start your FastAPI server: `uvicorn app.main:app --reload --port 8001`
                    2. Or use the correct API URL in the sidebar
                    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; margin-top: 2rem;">
    <p>✈️ <strong>SmartAir Flight Search Engine</strong> | Powered by Amadeus API & Streamlit</p>
    <p>🚀 Built with FastAPI backend | 💻 Created with ❤️</p>
</div>
""", unsafe_allow_html=True)

# Sidebar stats
with st.sidebar:
    if 'flight_data' in locals():
        st.markdown("### 📈 Current Search")
        st.metric("Route", f"{origin} → {destination}")
        st.metric("Total Flights", flight_data['total_flights_found'])
        st.metric("Best Price", f"${flight_data['cheapest_flight']['price']}")
        st.metric("Shortest Time", format_duration(flight_data['shortest_flight']['duration']))
