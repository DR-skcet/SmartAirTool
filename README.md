# ✈️SmartAir - Smart Flight Search Engine

A powerful flight search application built with FastAPI, Streamlit, and the Amadeus API that helps you find the cheapest and shortest flights across multiple dates.

![DRAir Logo](https://cdn-icons-png.flaticon.com/512/2830/2830284.png)

## 🌟 Features

### 🚀 **Smart Flight Search**
- Search flights across multiple dates (1-6 months)
- Find the absolute cheapest flight across all dates
- Find the shortest duration flight across all dates
- Compare multiple routes instantly

### 🎨 **Beautiful UI**
- Modern Streamlit interface with custom styling
- Interactive charts and visualizations
- Real-time search progress indicators
- Responsive design for all devices

### 📊 **Advanced Analytics**
- Price vs Duration comparison charts
- Flight statistics and metrics
- Popular routes quick selection
- Export results as JSON or CSV

### ⚡ **High Performance**
- Async API calls for fast processing
- Intelligent caching system
- Error handling and retry logic
- Real-time progress tracking

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **API**: Amadeus Flight API
- **Visualization**: Plotly
- **Data Processing**: Pandas
- **HTTP Client**: HTTPX

## 📋 Prerequisites

- Python 3.8+
- Amadeus API credentials (free at [developers.amadeus.com](https://developers.amadeus.com))

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd DRAir/Tool1
```

### 2. Create Environment File
Create a `.env` file in the project root:
```env
AMADEUS_CLIENT_ID=your_client_id_here
AMADEUS_CLIENT_SECRET=your_client_secret_here
AMADEUS_BASE_URL=https://test.api.amadeus.com
```

### 3. Install Dependencies
The virtual environment and dependencies are automatically managed. Simply run:
```bash
./start_app.sh
```

### 4. Access the Application
- **Streamlit UI**: http://127.0.0.1:8501
- **FastAPI Backend**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## 🎯 Usage

### Web Interface (Streamlit)
1. Open http://127.0.0.1:8501
2. Enter origin and destination airport codes (3-letter IATA codes)
3. Select search period (1-6 months)
4. Click "🔍 Search Flights"
5. View results with beautiful visualizations

### API Interface (FastAPI)
```bash
# Search flights
curl "http://127.0.0.1:8000/search?origin=DEL&destination=HYD&months=3"
```

## 📱 Interface Features

### 🎛️ **Sidebar Controls**
- Flight search parameters
- API configuration
- Quick stats display
- Popular routes shortcuts

### 📊 **Main Dashboard**
- Flight search results
- Price and duration metrics
- Interactive comparison charts
- Detailed flight information

### 💾 **Export Options**
- Download results as JSON
- Export data as CSV
- Share search results

## 🛣️ Supported Routes

The application supports all IATA airport codes. Popular Indian routes include:
- DEL (Delhi) ↔ HYD (Hyderabad)
- BOM (Mumbai) ↔ BLR (Bangalore)
- CCU (Kolkata) ↔ DEL (Delhi)
- And many more...

## 📊 Sample Response

```json
{
  "total_flights_found": 150,
  "search_period": "3 months",
  "cheapest_flight": {
    "price": "59.70",
    "currency": "USD",
    "departure_date": "2025-08-11",
    "duration": "PT9H20M",
    "segments": 2,
    "airline": "AI"
  },
  "shortest_flight": {
    "duration": "PT6H15M",
    "price": "89.50",
    "currency": "USD",
    "departure_date": "2025-08-15",
    "segments": 1,
    "airline": "6E"
  }
}
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `AMADEUS_CLIENT_ID` | Your Amadeus API client ID | Required |
| `AMADEUS_CLIENT_SECRET` | Your Amadeus API client secret | Required |
| `AMADEUS_BASE_URL` | Amadeus API base URL | `https://test.api.amadeus.com` |

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | GET | Search flights with origin, destination, and months |
| `/docs` | GET | Interactive API documentation |

## 🐛 Troubleshooting

### Common Issues

1. **"Command not found: uvicorn"**
   - Solution: Run `./start_app.sh` to use the virtual environment

2. **"API Authentication Failed"**
   - Check your `.env` file has correct Amadeus credentials
   - Verify your API key is active

3. **"No flights found"**
   - Verify airport codes are valid 3-letter IATA codes
   - Check if the route exists and has available flights

### Debug Mode
To run in debug mode:
```bash
# Start FastAPI with debug logs
uvicorn app.main:app --reload --log-level debug

# Start Streamlit with debug info
streamlit run streamlit_app.py --logger.level debug
```

## 📈 Performance

- **Search Speed**: ~2-5 seconds for 3-month search
- **API Calls**: Optimized with intelligent batching
- **Memory Usage**: ~50MB for typical searches
- **Concurrent Users**: Supports multiple simultaneous searches

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Amadeus API** for flight data
- **Streamlit** for the amazing UI framework
- **FastAPI** for the robust backend framework
- **Plotly** for beautiful visualizations

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Happy Flying with DRAir! ✈️**
