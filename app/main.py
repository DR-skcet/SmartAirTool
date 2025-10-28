from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from app.services.flight_search import search_flights
from app.services.gemini_ai import gemini_service

app = FastAPI(title="SmartAir API - AI-Powered Travel Intelligence", version="2.0.0")

# Request models for new AI features
class AnywhereSearchRequest(BaseModel):
    destination: Optional[str] = None  # Destination region (e.g., "America", "Europe", "Asia")
    preferences: Optional[str] = None  # User preferences as text
    budget: int
    climate: Optional[str] = "Any"
    visa_free: bool = True
    safety_importance: int = 7
    cost_preference: str = "Medium"
    interests: List[str] = []

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []

@app.get("/")
async def root():
    return {
        "message": "SmartAir Flight Search API - Powered by AI",
        "features": [
            "Flight Search",
            "AI Destination Discovery", 
            "AI Travel Assistant",
            "Travel Insights"
        ],
        "version": "2.0.0"
    }

@app.get("/search")
async def search(
    origin: str = Query(..., min_length=3, max_length=3),
    destination: str = Query(..., min_length=3, max_length=3),
    months: int = Query(3, ge=1, le=6)
):
    """Enhanced flight search with intelligent insights"""
    try:
        return await search_flights(origin, destination, months)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/anywhere-search")
async def anywhere_search(request: AnywhereSearchRequest):
    """🌍 AI-powered destination discovery based on budget and preferences"""
    try:
        # Parse preferences text into interests list
        interests = request.interests
        if request.preferences:
            # Convert preferences string to list
            pref_items = [p.strip() for p in request.preferences.split(",")]
            interests.extend(pref_items)
        
        preferences = {
            "destination_region": request.destination,
            "climate": request.climate,
            "visa_free": request.visa_free,
            "safety_importance": request.safety_importance,
            "cost_preference": request.cost_preference,
            "interests": interests
        }
        
        destinations = await gemini_service.generate_destination_recommendations(
            request.budget, preferences
        )
        
        return {
            "total_destinations": len(destinations),
            "budget_used": request.budget,
            "destinations": destinations,
            "ai_powered": True,
            "search_type": "AI Destination Discovery"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """🤖 Chat with AI travel assistant for personalized recommendations"""
    try:
        response = await gemini_service.chat_with_ai(
            request.message, 
            request.conversation_history
        )
        
        return {
            "response": response,
            "ai_powered": True,
            "timestamp": "2025-10-10",
            "assistant": "SmartAir AI Travel Expert"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat error: {str(e)}")

@app.get("/travel-insights")
async def get_travel_insights(route: str = "global"):
    """📊 Get AI-generated travel insights and market trends"""
    try:
        prompt = f"""
        Provide 4-5 current travel insights and trends for {route} routes. 
        Focus on practical, actionable advice about:
        - Price patterns and booking strategies
        - Seasonal recommendations and weather
        - Hidden costs and money-saving tips
        - Current market conditions
        """
        
        insights_text = await gemini_service.generate_travel_response(prompt)
        
        # Parse insights into structured format
        insights_list = [insight.strip() for insight in insights_text.split('\n') if insight.strip() and ('•' in insight or '-' in insight)]
        
        return {
            "insights": insights_list,
            "route": route,
            "ai_powered": True,
            "generated_at": "2025-10-10"
        }
    except Exception as e:
        # Fallback insights if AI fails
        return {
            "insights": [
                "✈️ This route is typically 23% cheaper on Tuesdays and Wednesdays",
                "🌤️ Weather delays more likely during monsoon season - book morning flights",
                "💰 Prices usually drop 18-25 days before departure for this route",
                "🏨 Hotel prices can be 40% higher during festival periods",
                "📱 Use incognito mode when searching - prices may increase with repeated searches"
            ],
            "route": route,
            "ai_powered": False
        }
