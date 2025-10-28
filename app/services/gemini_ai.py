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
                    "maxOutputTokens": 1024,
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
                        return result['candidates'][0]['content']['parts'][0]['text']
                
                print(f"⚠️ Gemini API returned no content or unexpected format")
                return self._get_fallback_response(prompt, context)
                
        except Exception as e:
            print(f"❌ Gemini AI error: {e}")
            print(f"📝 Falling back to curated response for: {prompt[:50]}...")
            return self._get_fallback_response(prompt, context)
    
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
                # Find JSON in response
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response[start:end]
                    data = json.loads(json_str)
                    return data.get('destinations', [])
            
            # Fallback to mock data if JSON parsing fails
            return self._get_mock_destinations(budget, preferences)
            
        except Exception as e:
            print(f"Error generating destinations: {e}")
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
        """Fallback responses when Gemini API is not available"""
        
        # Analyze prompt keywords for better responses
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['america', 'usa', 'united states', 'american']):
            return """🇺🇸 **Amazing America tour options:**

**East Coast Classic** - $2,200-2,800 total
• New York → Washington DC → Boston (7-10 days)
• Iconic landmarks: Statue of Liberty, White House, Freedom Trail
• Best time: April-June, September-November

**West Coast Adventure** - $2,500-3,200 total  
• Los Angeles → San Francisco → Las Vegas (8-12 days)
• Hollywood, Golden Gate Bridge, Grand Canyon tours
• Perfect weather: March-May, September-October

**National Parks Circuit** - $1,800-2,400 total
• Yellowstone → Grand Canyon → Zion (10-14 days)
• Epic landscapes and outdoor adventures
• Ideal season: May-September

**Southern Charm** - $1,600-2,200 total
• New Orleans → Nashville → Charleston (7-10 days)
• Music, food culture, and historic architecture
• Great year-round, avoid summer humidity

💡 **Pro tips for America:**
• Book domestic flights 6-8 weeks ahead
• Consider rental car for flexibility
• Many attractions offer city passes for savings
• Tipping 18-20% is standard at restaurants"""

        elif any(word in prompt_lower for word in ['romantic', 'couple', 'honeymoon']):
            return """🌹 **Perfect romantic destinations for you:**

**Santorini, Greece** - $950 total
• Stunning sunsets and white-washed architecture
• Perfect for couples with amazing cuisine
• Best time: April-October

**Prague, Czech Republic** - $780 total  
• Fairy-tale medieval charm with riverside walks
• Excellent value with world-class beer culture
• Castle views and romantic boat trips

**Lisbon, Portugal** - $820 total
• Coastal charm with tram rides and fado music
• Amazing seafood and historic neighborhoods
• Affordable luxury with great weather

💡 **Pro tip**: Book 6-8 weeks in advance for best romantic accommodation deals!"""

        elif any(word in prompt_lower for word in ['northern lights', 'aurora', 'iceland']):
            return """🌌 **Amazing Northern Lights destinations:**

**Reykjavik, Iceland** - $1,100 total
• 85% visibility chance in March
• Add Blue Lagoon and Golden Circle tours  
• Direct flights from most major cities

**Tromsø, Norway** - $1,300 total
• 90% aurora visibility - best in the world
• Husky sledding and Sami culture experiences
• Peak season: September-March

**Lapland, Finland** - $1,200 total
• Glass igloo hotels for aurora viewing
• Reindeer farms and snow activities
• Less crowded than Iceland

🔥 **Insider tip**: Download aurora forecast apps and stay 4+ nights for best chances!"""

        elif any(word in prompt_lower for word in ['adventure', 'southeast asia', 'backpacking']):
            return """🏝️ **Epic Southeast Asia adventures:**

**Thailand Circuit** - $1,400 (7 days)
• Bangkok → Chiang Mai → Phuket
• Street food, temples, and beaches
• Budget: $60-80/day

**Vietnam Explorer** - $1,350 (7 days) 
• Ho Chi Minh → Hanoi → Ha Long Bay
• Incredible food scene and history
• Budget: $50-70/day

**Indonesia Island Hopping** - $1,450 (6 days)
• Bali → Lombok → Gili Islands  
• Surfing, diving, and volcano hikes
• Budget: $70-90/day

⚡ **Pro tip**: Get travel insurance and book internal flights locally for better deals!"""

        elif any(word in prompt_lower for word in ['food', 'street food', 'cuisine']):
            return """🍜 **World's best street food destinations:**

**Bangkok, Thailand** - $650 total
• Pad Thai capital with endless street markets
• Chatuchak Weekend Market - food paradise
• $2-5 meals that rival fancy restaurants

**Mumbai, India** - $520 total
• Spice markets and incredible chaats
• Vada pav, dosa, and curry adventures  
• $1-3 meals with explosive flavors

**Hanoi, Vietnam** - $580 total
• Pho and banh mi heaven
• Morning coffee culture and night markets
• $2-4 meals with fresh ingredients

🌶️ **Foodie tip**: Follow locals to the busiest stalls - high turnover means freshest ingredients!"""

        else:
            # Minimal fallback response
            return "Sorry, I couldn't find a specific recommendation for your query. Please try rephrasing or ask about a destination, budget, or travel style!"

    def _get_mock_destinations(self, budget: int, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced mock destinations based on preferences"""
        
        base_destinations = [
            {
                "city": "Prague", "country": "Czech Republic", "estimated_flight_cost": 450,
                "daily_budget": 70, "climate": "Temperate", "visa_free": True,
                "safety_score": 92, "highlights": ["Architecture", "History", "Beer Culture"],
                "why_recommended": "Perfect blend of culture and affordability with stunning medieval architecture",
                "best_time": "April-October", "insider_tip": "Visit during shoulder season for fewer crowds and better prices"
            },
            {
                "city": "Lisbon", "country": "Portugal", "estimated_flight_cost": 380,
                "daily_budget": 65, "climate": "Mediterranean", "visa_free": True,
                "safety_score": 88, "highlights": ["Coastline", "Culture", "Food"],
                "why_recommended": "Coastal charm with excellent food scene and great value for money",
                "best_time": "March-May, Sept-Nov", "insider_tip": "Get a Lisboa Card for free public transport and museum access"
            },
            {
                "city": "Bangkok", "country": "Thailand", "estimated_flight_cost": 650,
                "daily_budget": 45, "climate": "Tropical", "visa_free": True,
                "safety_score": 85, "highlights": ["Street Food", "Temples", "Culture"],
                "why_recommended": "Incredible street food and cultural experiences at unbeatable prices",
                "best_time": "Nov-March", "insider_tip": "Stay near BTS Skytrain stations for easy transportation"
            },
            {
                "city": "Budapest", "country": "Hungary", "estimated_flight_cost": 420,
                "daily_budget": 60, "climate": "Temperate", "visa_free": True,
                "safety_score": 90, "highlights": ["Architecture", "Thermal Baths", "History"],
                "why_recommended": "Stunning architecture and unique thermal bath culture",
                "best_time": "April-October", "insider_tip": "Visit Széchenyi Baths early morning to avoid crowds"
            },
            {
                "city": "Krakow", "country": "Poland", "estimated_flight_cost": 400,
                "daily_budget": 55, "climate": "Temperate", "visa_free": True,
                "safety_score": 91, "highlights": ["History", "Architecture", "Food"],
                "why_recommended": "Medieval charm with rich history and excellent Polish cuisine",
                "best_time": "May-September", "insider_tip": "Take a day trip to Auschwitz-Birkenau for historical context"
            },
            {
                "city": "Istanbul", "country": "Turkey", "estimated_flight_cost": 420,
                "daily_budget": 50, "climate": "Mediterranean", "visa_free": False,
                "safety_score": 75, "highlights": ["History", "Culture", "Food"],
                "why_recommended": "Bridge between Europe and Asia with incredible history and food",
                "best_time": "April-May, Sept-Nov", "insider_tip": "Stay in Sultanahmet area to walk to major attractions"
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