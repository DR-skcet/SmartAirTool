"""
🤖 Gemini AI Service for SmartAir Travel Intelligence
Real AI-powered travel recommendations and destination discovery
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import httpx
from app.config import settings

class GeminiAIService:
    """Gemini AI integration for intelligent travel responses"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', 'your_gemini_api_key_here')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        # Debug: print API key status (remove in production)
        if self.api_key == 'your_gemini_api_key_here':
            print("⚠️ Gemini API key not found - using fallback responses")
        else:
            print(f"✅ Gemini API key loaded: {self.api_key[:10]}...")
        
    async def generate_travel_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate intelligent travel response using Gemini AI"""
        
        if self.api_key == 'your_gemini_api_key_here':
            return self._get_fallback_response(prompt, context)
        
        try:
            # Enhanced prompt with travel expertise context
            travel_context = """
            You are SmartAir's expert AI travel assistant with deep knowledge of:
            - Global destinations, cultures, and travel experiences  
            - Flight routes, pricing patterns, and booking strategies
            - Budget optimization and travel cost management
            - Weather patterns, visa requirements, and safety considerations
            - Hidden gems and off-the-beaten-path destinations
            - Personalized recommendations based on traveler preferences
            
            Provide practical, specific, and actionable travel advice. Always include:
            - Concrete recommendations with specific destinations
            - Estimated costs when relevant
            - Practical tips and insider knowledge
            - Multiple options to suit different preferences
            
            Answer in a precise way, do not exceed 100 lines in your response.
            """
            
            enhanced_prompt = f"{travel_context}\n\nUser Query: {prompt}"
            
            if context:
                enhanced_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": enhanced_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}?key={self.api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        # Log the full candidate for debugging
                        print(f"Gemini candidate: {json.dumps(candidate, indent=2)}")
                        content = candidate.get('content', {})
                        parts = content.get('parts')
                        if parts and isinstance(parts, list) and len(parts) > 0 and 'text' in parts[0]:
                            return parts[0]['text']
                        else:
                            print(f"❌ Gemini candidate missing 'parts' or 'text'. Candidate: {json.dumps(candidate, indent=2)}")
                            return "Sorry, the AI could not generate a response. Please try rephrasing or add more details."
                else:
                    print(f"⚠️ Gemini API returned status {response.status_code}: {response.text}")
                    return "Sorry, the AI service is temporarily unavailable."
        except Exception as e:
            print(f"❌ Gemini AI error: {e}")
            print(f"📝 Gemini prompt: {prompt[:50]}...")
            return "Sorry, an error occurred while generating your travel response. Please try again later."
    
    async def generate_destination_recommendations(self, budget: int, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent destination recommendations using AI"""
        
        # Include destination region in prompt
        region_text = ""
        if preferences.get('destination_region'):
            region_text = f"- Focus on destinations in/around: {preferences.get('destination_region')}"
        
        prompt = f"""
        As a travel expert, recommend destinations for a traveler with:
        - Budget: ${budget} USD (total trip cost including flights and 3-7 days)
        {region_text}
        - Climate preference: {preferences.get('climate', 'Any')}
        - Visa requirements: {'Visa-free only' if preferences.get('visa_free', False) else 'Any'}
        - Safety priority: {preferences.get('safety_importance', 5)}/10
        - Cost preference: {preferences.get('cost_preference', 'Medium')} cost destinations
        - Interests: {', '.join(preferences.get('interests', []))}
        
        Provide 6-8 specific destination recommendations in this JSON format:
        {{
            "destinations": [
                {{
                    "city": "City Name",
                    "country": "Country",
                    "estimated_flight_cost": 500,
                    "daily_budget": 80,
                    "total_estimated_cost": 740,
                    "climate": "Mediterranean",
                    "visa_free": true,
                    "safety_score": 85,
                    "match_score": 92,
                    "highlights": ["Culture", "Food", "History"],
                    "why_recommended": "Brief explanation of why this matches their preferences",
                    "best_time": "October-March",
                    "insider_tip": "Local secret or money-saving tip"
                }}
            ]
        }}
        
        Focus on realistic, achievable destinations that truly match their preferences and budget.
        """
        
        try:
            response = await self.generate_travel_response(prompt, preferences)
            # Try to extract JSON from response
            if "destinations" in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response[start:end]
                    try:
                        data = json.loads(json_str)
                        destinations = data.get('destinations', [])
                        if destinations:
                            return destinations
                    except Exception as parse_err:
                        print(f"Error parsing Gemini destinations JSON: {parse_err}")
            # Fallback: return mock destinations if Gemini response is empty or invalid
            print("No valid Gemini destinations found, returning mock data.")
            return self._get_mock_destinations(budget, preferences)
        except Exception as e:
            print(f"Error generating destinations: {e}")
            print("Returning mock destinations due to error.")
            return self._get_mock_destinations(budget, preferences)
    
    async def chat_with_ai(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """Interactive chat with AI travel assistant"""
        
        context = {
            "conversation_history": conversation_history or [],
            "user_query": user_message
        }
        
        prompt = f"""
        Continue this travel consultation conversation. The user just said: "{user_message}"
        
        Previous conversation context: {json.dumps(conversation_history or [], indent=2)}
        
        Provide helpful, specific travel advice. If they're asking about:
        - Destinations: Suggest specific places with reasons
        - Budgets: Give realistic cost breakdowns  
        - Activities: Recommend specific experiences
        - Logistics: Provide actionable booking advice
        - Alternatives: Offer multiple options
        
        Keep responses conversational but informative. Include specific details like costs, timeframes, and practical tips.
        """
        
        return await self.generate_travel_response(prompt, context)
    
    def _get_fallback_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """No fallback: always return empty string so only Gemini AI responses are used"""
        return ""

    def _get_mock_destinations(self, budget: int, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced mock destinations based on preferences"""
        
        base_destinations = [
            # Budget (<$800 total)
            {
                "city": "Prague", "country": "Czech Republic", "estimated_flight_cost": 450,
                "daily_budget": 70, "climate": "Temperate", "visa_free": True,
                "safety_score": 92, "highlights": ["Architecture", "History", "Beer Culture"],
                "why_recommended": "Perfect blend of culture and affordability with stunning medieval architecture",
                "best_time": "April-October", "insider_tip": "Visit during shoulder season for fewer crowds and better prices"
            },
            {
                "city": "Krakow", "country": "Poland", "estimated_flight_cost": 400,
                "daily_budget": 55, "climate": "Temperate", "visa_free": True,
                "safety_score": 91, "highlights": ["History", "Architecture", "Food"],
                "why_recommended": "Medieval charm with rich history and excellent Polish cuisine",
                "best_time": "May-September", "insider_tip": "Take a day trip to Auschwitz-Birkenau for historical context"
            },
            {
                "city": "Budapest", "country": "Hungary", "estimated_flight_cost": 420,
                "daily_budget": 60, "climate": "Temperate", "visa_free": True,
                "safety_score": 90, "highlights": ["Architecture", "Thermal Baths", "History"],
                "why_recommended": "Stunning architecture and unique thermal bath culture",
                "best_time": "April-October", "insider_tip": "Visit Széchenyi Baths early morning to avoid crowds"
            },
            # Mid-range ($800-$1500)
            {
                "city": "Lisbon", "country": "Portugal", "estimated_flight_cost": 380,
                "daily_budget": 65, "climate": "Mediterranean", "visa_free": True,
                "safety_score": 88, "highlights": ["Coastline", "Culture", "Food"],
                "why_recommended": "Coastal charm with excellent food scene and great value for money",
                "best_time": "March-May, Sept-Nov", "insider_tip": "Get a Lisboa Card for free public transport and museum access"
            },
            {
                "city": "Istanbul", "country": "Turkey", "estimated_flight_cost": 420,
                "daily_budget": 50, "climate": "Mediterranean", "visa_free": False,
                "safety_score": 75, "highlights": ["History", "Culture", "Food"],
                "why_recommended": "Bridge between Europe and Asia with incredible history and food",
                "best_time": "April-May, Sept-Nov", "insider_tip": "Stay in Sultanahmet area to walk to major attractions"
            },
            {
                "city": "Bangkok", "country": "Thailand", "estimated_flight_cost": 650,
                "daily_budget": 45, "climate": "Tropical", "visa_free": True,
                "safety_score": 85, "highlights": ["Street Food", "Temples", "Culture"],
                "why_recommended": "Incredible street food and cultural experiences at unbeatable prices",
                "best_time": "Nov-March", "insider_tip": "Stay near BTS Skytrain stations for easy transportation"
            },
            # Premium ($1500+)
            {
                "city": "Tokyo", "country": "Japan", "estimated_flight_cost": 1200,
                "daily_budget": 110, "climate": "Temperate", "visa_free": True,
                "safety_score": 95, "highlights": ["Technology", "Culture", "Cuisine"],
                "why_recommended": "World-class city for tech, food, and culture lovers",
                "best_time": "March-May, Oct-Nov", "insider_tip": "Get a Suica card for easy transit and try Tsukiji Outer Market for street food"
            },
            {
                "city": "Sydney", "country": "Australia", "estimated_flight_cost": 1400,
                "daily_budget": 120, "climate": "Temperate", "visa_free": True,
                "safety_score": 93, "highlights": ["Beaches", "Nature", "City Life"],
                "why_recommended": "Iconic beaches and vibrant city life with great weather",
                "best_time": "Sept-Nov, March-May", "insider_tip": "Use Opal card for public transport and visit Bondi Beach early morning"
            },
            # Adventure/Exotic
            {
                "city": "Cusco", "country": "Peru", "estimated_flight_cost": 900,
                "daily_budget": 60, "climate": "Mountain", "visa_free": True,
                "safety_score": 80, "highlights": ["Ruins", "Culture", "Trekking"],
                "why_recommended": "Gateway to Machu Picchu and rich Andean culture",
                "best_time": "May-Sept", "insider_tip": "Acclimatize for altitude and try local Peruvian cuisine"
            },
            {
                "city": "Cape Town", "country": "South Africa", "estimated_flight_cost": 1100,
                "daily_budget": 80, "climate": "Mediterranean", "visa_free": True,
                "safety_score": 78, "highlights": ["Nature", "Wine", "Adventure"],
                "why_recommended": "Stunning landscapes, adventure sports, and world-class wine",
                "best_time": "Oct-April", "insider_tip": "Take the cable car up Table Mountain and visit the V&A Waterfront"
            },
            # Family/Relaxation
            {
                "city": "Bali", "country": "Indonesia", "estimated_flight_cost": 800,
                "daily_budget": 50, "climate": "Tropical", "visa_free": True,
                "safety_score": 82, "highlights": ["Beaches", "Culture", "Wellness"],
                "why_recommended": "Relaxing beaches, yoga retreats, and vibrant local culture",
                "best_time": "April-Oct", "insider_tip": "Stay in Ubud for wellness and culture, Seminyak for beaches"
            },
            {
                "city": "Vancouver", "country": "Canada", "estimated_flight_cost": 950,
                "daily_budget": 100, "climate": "Temperate", "visa_free": True,
                "safety_score": 94, "highlights": ["Nature", "City Life", "Food"],
                "why_recommended": "Beautiful city with access to mountains, ocean, and multicultural food",
                "best_time": "May-Sept", "insider_tip": "Rent a bike and explore Stanley Park, try sushi downtown"
            }
        ]
        
        # Filter and score based on preferences
        suitable_destinations = []
        
        for dest in base_destinations:
            # Calculate total cost
            days = 4  # Default trip length
            total_cost = dest["estimated_flight_cost"] + (dest["daily_budget"] * days)
            
            # Check if within budget
            if total_cost <= budget:
                # Calculate match score based on preferences
                match_score = self._calculate_match_score(dest, preferences)
                
                dest.update({
                    "total_estimated_cost": total_cost,
                    "match_score": match_score
                })
                
                suitable_destinations.append(dest)
        
        # Sort by match score and return top 6
        suitable_destinations.sort(key=lambda x: x["match_score"], reverse=True)
        return suitable_destinations[:6]
    
    def _calculate_match_score(self, destination: Dict[str, Any], preferences: Dict[str, Any]) -> int:
        """Calculate how well destination matches preferences"""
        score = 50  # Base score
        
        # Climate match
        if preferences.get("climate") and destination["climate"] == preferences["climate"]:
            score += 25
        
        # Visa preference
        if preferences.get("visa_free", False) and destination["visa_free"]:
            score += 20
        
        # Safety importance
        safety_weight = preferences.get("safety_importance", 5) / 10
        score += int((destination["safety_score"] / 100) * 25 * safety_weight)
        
        # Interest matching
        user_interests = set(preferences.get("interests", []))
        dest_highlights = set(destination["highlights"])
        interest_match = len(user_interests.intersection(dest_highlights))
        score += interest_match * 10
        
        return min(score, 100)

# Global instance
gemini_service = GeminiAIService()