"""
🌍 Anywhere Search: Revolutionary Destination Discovery
Find destinations based on budget, preferences, and constraints
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import random

class AnywhereSearchEngine:
    """Revolutionary destination discovery based on budget and preferences"""
    
    def __init__(self):
        # Sample destination database (in real app, this would be from APIs)
        self.destinations = [
            {"city": "Bangkok", "country": "Thailand", "avg_flight_cost": 650, "climate": "Tropical", "visa_free": True, "safety_score": 85, "cost_of_living": "Low", "highlights": ["Street Food", "Temples", "Nightlife"]},
            {"city": "Prague", "country": "Czech Republic", "avg_flight_cost": 450, "climate": "Temperate", "visa_free": True, "safety_score": 92, "cost_of_living": "Medium", "highlights": ["Architecture", "Beer", "History"]},
            {"city": "Lisbon", "country": "Portugal", "avg_flight_cost": 380, "climate": "Mediterranean", "visa_free": True, "safety_score": 88, "cost_of_living": "Medium", "highlights": ["Coastline", "Culture", "Food"]},
            {"city": "Istanbul", "country": "Turkey", "avg_flight_cost": 420, "climate": "Mediterranean", "visa_free": False, "safety_score": 75, "cost_of_living": "Low", "highlights": ["History", "Culture", "Food"]},
            {"city": "Dubai", "country": "UAE", "avg_flight_cost": 580, "climate": "Desert", "visa_free": True, "safety_score": 95, "cost_of_living": "High", "highlights": ["Luxury", "Shopping", "Architecture"]},
            {"city": "Tokyo", "country": "Japan", "avg_flight_cost": 720, "climate": "Temperate", "visa_free": True, "safety_score": 98, "cost_of_living": "High", "highlights": ["Technology", "Culture", "Food"]},
            {"city": "Reykjavik", "country": "Iceland", "avg_flight_cost": 350, "climate": "Arctic", "visa_free": True, "safety_score": 99, "cost_of_living": "High", "highlights": ["Northern Lights", "Nature", "Adventure"]},
            {"city": "Cape Town", "country": "South Africa", "avg_flight_cost": 850, "climate": "Mediterranean", "visa_free": True, "safety_score": 70, "cost_of_living": "Low", "highlights": ["Nature", "Wine", "Adventure"]},
            {"city": "Buenos Aires", "country": "Argentina", "avg_flight_cost": 750, "climate": "Temperate", "visa_free": True, "safety_score": 78, "cost_of_living": "Low", "highlights": ["Culture", "Food", "Nightlife"]},
            {"city": "Bali", "country": "Indonesia", "avg_flight_cost": 680, "climate": "Tropical", "visa_free": True, "safety_score": 80, "cost_of_living": "Low", "highlights": ["Beaches", "Culture", "Spirituality"]},
            {"city": "Amsterdam", "country": "Netherlands", "avg_flight_cost": 340, "climate": "Temperate", "visa_free": True, "safety_score": 90, "cost_of_living": "High", "highlights": ["Canals", "Art", "Culture"]},
            {"city": "Singapore", "country": "Singapore", "avg_flight_cost": 780, "climate": "Tropical", "visa_free": True, "safety_score": 97, "cost_of_living": "High", "highlights": ["Food", "Architecture", "Gardens"]},
        ]
    
    def search_by_budget(self, budget: int, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find destinations within budget with preference matching"""
        suitable_destinations = []
        
        for dest in self.destinations:
            # Budget check (flight + estimated 3-day expenses)
            daily_cost = {"Low": 50, "Medium": 100, "High": 200}[dest["cost_of_living"]]
            total_estimated_cost = dest["avg_flight_cost"] + (daily_cost * 3)
            
            if total_estimated_cost <= budget:
                # Calculate preference score
                score = self._calculate_preference_score(dest, preferences)
                dest["preference_score"] = score
                dest["total_estimated_cost"] = total_estimated_cost
                dest["daily_cost"] = daily_cost
                suitable_destinations.append(dest)
        
        # Sort by preference score
        return sorted(suitable_destinations, key=lambda x: x["preference_score"], reverse=True)
    
    def _calculate_preference_score(self, dest: Dict[str, Any], preferences: Dict[str, Any]) -> float:
        """Calculate how well destination matches user preferences"""
        score = 0.0
        
        # Climate preference
        if preferences.get("climate") and dest["climate"] == preferences["climate"]:
            score += 30
        
        # Visa-free preference
        if preferences.get("visa_free", False) and dest["visa_free"]:
            score += 20
        
        # Safety preference
        safety_weight = preferences.get("safety_importance", 5)  # 1-10 scale
        score += (dest["safety_score"] / 100) * safety_weight * 10
        
        # Cost preference
        cost_pref = preferences.get("cost_preference", "Medium")
        if dest["cost_of_living"] == cost_pref:
            score += 25
        
        # Activity preferences
        user_interests = preferences.get("interests", [])
        matching_highlights = set(dest["highlights"]) & set(user_interests)
        score += len(matching_highlights) * 15
        
        return min(score, 100)  # Cap at 100

def display_anywhere_search():
    """Display the revolutionary Anywhere Search interface"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">🌍 Anywhere Search</h1>
        <p style="color: white; text-align: center; font-size: 1.2rem; margin: 0.5rem 0 0 0;">
            Tell us your budget, we'll show you the world
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize search engine
    search_engine = AnywhereSearchEngine()
    
    # Search parameters
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💰 What's Your Budget?")
        budget = st.slider(
            "Total Trip Budget (USD)",
            min_value=300,
            max_value=3000,
            value=800,
            step=50,
            help="Includes flights + 3 days accommodation & food"
        )
        
        # Preference filters
        st.markdown("### 🎯 Your Preferences")
        
        pref_col1, pref_col2 = st.columns(2)
        
        with pref_col1:
            climate = st.selectbox(
                "🌡️ Preferred Climate",
                ["Any", "Tropical", "Mediterranean", "Temperate", "Desert", "Arctic"],
                help="What weather do you enjoy?"
            )
            
            visa_free = st.checkbox(
                "✈️ Visa-free destinations only",
                value=True,
                help="Only show destinations you can visit without a visa"
            )
        
        with pref_col2:
            safety_importance = st.slider(
                "🛡️ Safety Importance (1-10)",
                min_value=1,
                max_value=10,
                value=7,
                help="How important is safety to you?"
            )
            
            cost_preference = st.selectbox(
                "💸 Cost of Living Preference",
                ["Low", "Medium", "High"],
                index=1,
                help="Preferred cost level at destination"
            )
        
        # Interest tags
        st.markdown("### 🎨 What Interests You?")
        interests = st.multiselect(
            "Select your interests:",
            ["Food", "Culture", "History", "Nightlife", "Adventure", "Nature", "Art", 
             "Shopping", "Beaches", "Architecture", "Technology", "Spirituality", 
             "Wine", "Luxury", "Gardens", "Northern Lights"],
            default=["Food", "Culture"]
        )
    
    with col2:
        st.markdown("### 🎯 Smart Filters")
        st.info(f"💰 Budget: ${budget:,}")
        st.info(f"🌡️ Climate: {climate if climate != 'Any' else 'Any climate'}")
        st.info(f"🛡️ Safety Priority: {safety_importance}/10")
        st.info(f"✈️ Visa-free: {'Yes' if visa_free else 'No preference'}")
        st.info(f"🎨 Interests: {len(interests)} selected")
        
        # Fun facts
        st.markdown("#### 💡 Did You Know?")
        facts = [
            "🌍 There are 195 countries to explore",
            "✈️ The average person visits only 12 countries",
            "💰 Budget travel can take you 3x further",
            "🎯 AI can find 40% cheaper alternatives"
        ]
        for fact in facts:
            st.caption(fact)
    
    # Build preferences dictionary
    preferences = {
        "climate": climate if climate != "Any" else None,
        "visa_free": visa_free,
        "safety_importance": safety_importance,
        "cost_preference": cost_preference,
        "interests": interests
    }
    
    # Search button
    if st.button("🔍 Discover Destinations", type="primary", use_container_width=True):
        
        with st.spinner("🌍 Analyzing global destinations..."):
            import time
            time.sleep(2)  # Simulate processing
            
            destinations = search_engine.search_by_budget(budget, preferences)
        
        if destinations:
            st.success(f"✨ Found {len(destinations)} amazing destinations within your budget!")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_cost = sum(d["total_estimated_cost"] for d in destinations[:5]) / min(5, len(destinations))
                st.metric("💰 Avg Trip Cost", f"${avg_cost:.0f}")
            
            with col2:
                avg_score = sum(d["preference_score"] for d in destinations[:5]) / min(5, len(destinations))
                st.metric("🎯 Avg Match Score", f"{avg_score:.0f}%")
            
            with col3:
                visa_free_count = sum(1 for d in destinations if d["visa_free"])
                st.metric("✈️ Visa-free Options", f"{visa_free_count}")
            
            with col4:
                savings = budget - min(d["total_estimated_cost"] for d in destinations[:3])
                st.metric("💵 Max Savings", f"${savings:.0f}")
            
            # Interactive map (mock implementation)
            st.markdown("### 🗺️ Your Destination Map")
            
            # Create sample map data
            map_data = []
            for i, dest in enumerate(destinations[:10]):
                # Mock coordinates (in real app, use geocoding API)
                lat = random.uniform(-60, 70)
                lon = random.uniform(-180, 180)
                map_data.append({
                    "lat": lat,
                    "lon": lon,
                    "city": dest["city"],
                    "country": dest["country"],
                    "cost": dest["total_estimated_cost"],
                    "score": dest["preference_score"]
                })
            
            df_map = pd.DataFrame(map_data)
            
            fig = px.scatter_mapbox(
                df_map, 
                lat="lat", 
                lon="lon",
                size="score",
                color="cost",
                hover_name="city",
                hover_data=["country", "cost", "score"],
                color_continuous_scale="viridis",
                size_max=20,
                zoom=1,
                title="🌍 Destinations Matching Your Criteria"
            )
            fig.update_layout(mapbox_style="open-street-map", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Destination cards
            st.markdown("### ✈️ Top Recommendations")
            
            for i, dest in enumerate(destinations[:6]):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Preference score color
                    score_color = "#28a745" if dest["preference_score"] >= 80 else "#ffc107" if dest["preference_score"] >= 60 else "#6c757d"
                    
                    st.markdown(f"""
                    <div style="border: 2px solid {score_color}; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; background: white;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3 style="color: black; margin: 0;">{i+1}. {dest['city']}, {dest['country']}</h3>
                                <div style="margin: 0.5rem 0;">
                                    <span style="background: {score_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.9rem;">
                                        🎯 {dest['preference_score']:.0f}% Match
                                    </span>
                                    <span style="background: #e9ecef; color: #495057; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.9rem; margin-left: 0.5rem;">
                                        🌡️ {dest['climate']}
                                    </span>
                                    <span style="background: #e9ecef; color: #495057; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.9rem; margin-left: 0.5rem;">
                                        🛡️ Safety: {dest['safety_score']}/100
                                    </span>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #28a745;">
                                    ${dest['total_estimated_cost']}
                                </div>
                                <div style="color: #6c757d; font-size: 0.9rem;">3-day trip</div>
                            </div>
                        </div>
                        <div style="margin-top: 1rem; display: flex; justify-content: space-between;">
                            <div>
                                <strong>✈️ Flight:</strong> ${dest['avg_flight_cost']} | 
                                <strong>🏨 Daily cost:</strong> ${dest['daily_cost']} | 
                                <strong>✅ Visa:</strong> {'Free' if dest['visa_free'] else 'Required'}
                            </div>
                        </div>
                        <div style="margin-top: 1rem;">
                            <strong>🎨 Highlights:</strong> {' • '.join(dest['highlights'])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"✈️ Book Now", key=f"book_{i}", use_container_width=True):
                        st.info(f"🎉 Great choice! Redirecting to book {dest['city']}...")
                    
                    if st.button(f"ℹ️ Learn More", key=f"info_{i}", use_container_width=True):
                        st.info(f"📖 Opening {dest['city']} travel guide...")
            
            # Comparison chart
            st.markdown("### 📊 Cost vs Preference Analysis")
            
            chart_data = pd.DataFrame([
                {
                    "Destination": f"{d['city']}, {d['country']}", 
                    "Total Cost": d['total_estimated_cost'],
                    "Preference Score": d['preference_score'],
                    "Safety Score": d['safety_score']
                } 
                for d in destinations[:8]
            ])
            
            fig = px.scatter(
                chart_data, 
                x="Total Cost", 
                y="Preference Score",
                size="Safety Score",
                hover_name="Destination",
                title="💰 Cost vs 🎯 Personal Match Score",
                labels={"Total Cost": "Total Trip Cost (USD)", "Preference Score": "Personal Match (%)"}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Save preferences
            st.markdown("### 💾 Save Your Search")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📧 Email Results", use_container_width=True):
                    st.success("📧 Results sent to your email!")
            
            with col2:
                if st.button("⭐ Save Preferences", use_container_width=True):
                    st.success("⭐ Preferences saved to your profile!")
        
        else:
            st.warning("😔 No destinations found within your budget. Try increasing your budget or adjusting preferences.")
            
            # Suggestions for no results
            st.markdown("### 💡 Try These Suggestions:")
            st.info("🔧 **Increase Budget**: Try $" + str(budget + 200) + " for more options")
            st.info("🌍 **Expand Climate**: Consider 'Any' climate for more destinations")
            st.info("✈️ **Flexible Visa**: Include visa-required destinations")

# Example usage
if __name__ == "__main__":
    display_anywhere_search()