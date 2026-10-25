# CampusFlow AI - Setup & Development Guide

## 📦 Project Structure Created

```
CampusFlow-ai/
├── backend/                    # FastAPI Python Backend
│   ├── app/
│   │   ├── api/               # API endpoints (facilities, reports, recommendations)
│   │   ├── core/              # Config, database, settings
│   │   ├── models/            # Database models & Pydantic schemas
│   │   ├── services/          # Business logic (crowd estimator, recommendation engine)
│   │   └── main.py            # FastAPI application entry point
│   ├── requirements.txt       # Python dependencies
│   ├── seed_data.py          # Database seeding script
│   └── .env.example          # Environment variables template
├── frontend/                  # React + Vite Frontend
│   ├── src/
│   │   ├── components/       # UI components (Navigation, screens)
│   │   ├── services/         # API client
│   │   ├── App.jsx           # Main application
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite configuration
│   └── tailwind.config.js    # Tailwind CSS config
├── data/                     # For datasets and exports
├── docs/                     # Documentation
└── README.md                 # Project overview
```

## 🚀 Quick Start

### 1. Backend Setup (FastAPI)

**Navigate to backend:**
```bash
cd backend
```

**Create virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Create .env file:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Groq API key (optional for MVP)
# Get free key from: https://console.groq.com/keys
```

**Initialize database with seed data:**
```bash
python seed_data.py
```

**Run the backend server:**
```bash
uvicorn app.main:app --reload
```

Backend will be available at: **http://localhost:8000**
- API docs (Swagger UI): **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

---

### 2. Frontend Setup (React + Vite)

**Open a new terminal, navigate to frontend:**
```bash
cd frontend
```

**Install dependencies:**
```bash
npm install
```

**Start development server:**
```bash
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## 🧪 Testing the Application

### Test Backend API Endpoints

**Check health:**
```bash
curl http://localhost:8000/health
```

**Get all facilities:**
```bash
curl http://localhost:8000/api/v1/facilities
```

**Submit a report:**
```bash
curl -X POST http://localhost:8000/api/v1/reports \
  -H "Content-Type: application/json" \
  -d '{
    "facility_id": 1,
    "crowd_level": "low",
    "available_seats": 45
  }'
```

**Get recommendations:**
```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Where should I study right now?"
  }'
```

### Test Frontend

1. Open **http://localhost:5173** in your browser
2. You should see the CampusFlow mobile interface
3. Navigate through the three screens:
   - **Home**: View all facilities and their status
   - **Facility Detail**: Click any facility to see details and submit reports
   - **AI Assistant**: Ask questions about campus facilities

---

## 🏗️ Architecture Overview

### Backend Services

**1. Crowd Estimator Service** (`services/crowd_estimator.py`)
- Aggregates student reports using weighted averaging
- Calculates confidence scores based on data freshness
- Uses exponential decay for time-based weighting
- Updates facility status in real-time

**2. Recommendation Engine** (`services/recommendation_engine.py`)
- Scores facilities based on:
  - Crowd level (lower is better)
  - Wait time (shorter is better)
  - Seat availability (more is better)
  - Data freshness & confidence
- Generates natural language explanations
- Optionally uses Groq LLM for dynamic responses

**3. API Endpoints**
- `GET /api/v1/facilities` - List all facilities
- `GET /api/v1/facilities/{id}` - Get facility details
- `GET /api/v1/facilities/{id}/estimate` - Get crowd estimate
- `POST /api/v1/reports` - Submit student report
- `POST /api/v1/recommend` - Get AI recommendations
- `POST /api/v1/plan` - Plan multi-facility route

### Frontend Components

**1. HomeScreen** - Dashboard with facility cards
**2. DetailScreen** - Facility details with report submission
**3. ChatScreen** - AI assistant with natural language queries
**4. Navigation** - Header and bottom nav components

### Database Models

**Facility Table:**
- Basic info (name, type, location, hours)
- Current status (crowd level, wait time, seats)
- Metadata (data source, confidence, last updated)

**Report Table:**
- Student-submitted observations
- Timestamped crowd/wait/seat data
- Anonymous session tracking

---

## 🎨 Design System

**Color Palette:**
- Primary Brand: `#4A7C9D` (Muted Blue)
- Surface: `#F5F5F5` (Light Gray)
- Status Colors:
  - Low/Green: `#DCFCE7` / `#166534`
  - Moderate/Amber: `#FEF3C7` / `#92400E`
  - High/Red: `#FEE2E2` / `#991B1B`

**Typography:**
- System font stack: `-apple-system, SF Pro, Segoe UI`
- Hero numbers: 34px bold
- Body text: 13-15px

**Spacing:**
- Border radius: 6-8px
- Minimum tap targets: 44px
- Card padding: 14-16px

---

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
# Database
DATABASE_URL=sqlite:///./campusflow.db
# For PostgreSQL: postgresql://user:password@localhost:5432/campusflow

# LLM API (Optional - fallback to deterministic responses)
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=mixtral-8x7b-32768

# Server
DEBUG=True
PORT=8000

# Data Settings
ENABLE_SIMULATED_DATA=True
REPORT_STALENESS_THRESHOLD_MINUTES=30
```

### Frontend Configuration

**Vite proxy** is configured to forward `/api` requests to `http://localhost:8000`

---

## 📊 Data Flow

1. **Student submits report** → POST `/api/v1/reports`
2. **Backend validates** → Saves to database
3. **Crowd estimator updates** → Recalculates facility status
4. **Frontend polls** → GET `/api/v1/facilities`
5. **UI updates** → Shows new crowd levels

---

## 🚧 Development Phases

### ✅ Phase 1 - Foundation (COMPLETE)
- [x] Project structure
- [x] Backend API with FastAPI
- [x] Frontend with React + Vite
- [x] Database models
- [x] Basic UI prototype
- [x] Seed data

### 🔄 Phase 2 - Core Features (IN PROGRESS)
- [ ] Student report validation
- [ ] Historical data tracking
- [ ] Crowd estimation refinement
- [ ] Real-time updates (WebSocket)

### 📅 Phase 3 - Intelligence Layer
- [ ] Demand forecasting
- [ ] Optimal routing algorithm
- [ ] LLM-powered assistant
- [ ] Confidence scoring improvements

### 🎯 Phase 4 - Polish & Testing
- [ ] User testing with classmates
- [ ] Performance optimization
- [ ] Error handling & edge cases
- [ ] Documentation & deployment

---

## 🐛 Troubleshooting

**Backend won't start:**
- Ensure virtual environment is activated
- Check all dependencies installed: `pip list`
- Verify Python version: `python --version` (needs 3.9+)

**Frontend shows "Loading facilities...":**
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify API proxy in `vite.config.js`

**Database errors:**
- Delete `campusflow.db` and run `seed_data.py` again
- Check database URL in `.env`

**LLM not working:**
- Verify `GROQ_API_KEY` in `.env`
- Check API key validity at https://console.groq.com
- System falls back to deterministic responses if LLM fails

---

## 📝 Next Steps

1. **Test the full stack**: Run both backend and frontend
2. **Submit test reports**: Use the UI to add crowd reports
3. **Verify data updates**: Check if facilities update after reports
4. **Try the AI assistant**: Ask questions and get recommendations
5. **Add more facilities**: Extend seed data with campus-specific locations
6. **Integrate with real sensors** (future): Replace simulated data

---

## 🤝 Contributing

This is a college project. Team members should:
1. Create feature branches: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Submit pull requests for review
4. Update documentation as needed

---

## 📄 License

College Project - All Rights Reserved

---

**Last Updated:** October 24, 2026

**Status:** MVP Ready for Testing 🎉
