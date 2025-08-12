# 🏗️ SmartAir - System Architecture

## **System Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│                        SmartAir Flight Search                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   USER BROWSER  │    │   STREAMLIT UI  │    │  FASTAPI BACKEND│
│                 │    │   (Port 8501)   │    │   (Port 8001)   │
│  - Search Form  │◄──►│  - Flight Cards │◄──►│  - Search Logic │
│  - View Results │    │  - Charts/Viz   │    │  - Data Process │
│  - Download     │    │  - Export Tools │    │  - Error Handle │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                 │                       │
                                 │                       │
                       ┌─────────▼───────────┐          │
                       │    CUSTOM CSS       │          │
                       │   - Flight Cards    │          │
                       │   - Hover Effects   │          │
                       │   - Responsive      │          │
                       └─────────────────────┘          │
                                                        │
                              ┌─────────────────────────▼─────────────────────────┐
                              │                AMADEUS API                        │
                              │  - Flight Search (GET /v2/shopping/flight-offers) │
                              │  - OAuth2 Auth (POST /v1/security/oauth2/token)   │
                              │  - Real-time Data                                 │
                              └───────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      DATA FLOW                                  │
└─────────────────────────────────────────────────────────────────┘

1. User enters search criteria (Origin, Destination, Months)
2. Streamlit sends request to FastAPI backend
3. FastAPI authenticates with Amadeus API
4. FastAPI searches flights across multiple dates
5. Data processed to find cheapest & shortest options
6. Results returned to Streamlit UI
7. Interactive visualizations and cards displayed
8. User can export data or view detailed information

┌─────────────────────────────────────────────────────────────────┐
│                    COMPONENT BREAKDOWN                          │
└─────────────────────────────────────────────────────────────────┘

FRONTEND (Streamlit)
├── streamlit_app.py
├── Custom CSS Styling
├── Interactive Elements
│   ├── Search Form
│   ├── Progress Bars
│   ├── Flight Cards
│   ├── Comparison Charts
│   └── Export Buttons
└── Error Handling UI

BACKEND (FastAPI)
├── app/main.py (API Router)
├── services/
│   ├── amadeus_auth.py (Authentication)
│   └── flight_search.py (Search Logic)
├── utils/
│   ├── date_utils.py (Date Generation)
│   └── cache.py (Token Caching)
├── models/flight_model.py (Data Models)
└── config.py (Settings)

EXTERNAL SERVICES
└── Amadeus API
    ├── Flight Search API
    ├── OAuth2 Authentication
    └── Real-time Flight Data

┌─────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT SETUP                           │
└─────────────────────────────────────────────────────────────────┘

Development Environment:
├── Python Virtual Environment (.venv)
├── Environment Variables (.env)
├── Startup Script (start_app.sh)
└── Requirements Management (requirements.txt)

Production Ready:
├── Uvicorn ASGI Server (Backend)
├── Streamlit Server (Frontend)
├── Process Management
└── Port Configuration

┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY FEATURES                           │
└─────────────────────────────────────────────────────────────────┘

✅ Environment-based API key management
✅ OAuth2 token authentication with Amadeus
✅ Input validation (IATA codes, parameters)
✅ Error handling without exposing sensitive data
✅ Secure HTTP connections
✅ No hardcoded credentials in source code
```

## **Performance Characteristics**

- **Concurrent Users**: Supports multiple simultaneous searches
- **Search Efficiency**: Async processing for optimal speed
- **Memory Usage**: ~50MB for typical operations
- **API Rate Limits**: Intelligent handling of Amadeus limits
- **Timeout Management**: Dynamic timeouts based on search complexity

## **Scalability Considerations**

- **Horizontal Scaling**: Stateless design allows multiple instances
- **Database Ready**: Architecture supports database integration
- **Caching Layer**: Token caching reduces API calls
- **Load Balancing**: FastAPI supports load balancer deployment
- **Microservices**: Modular design for service separation
