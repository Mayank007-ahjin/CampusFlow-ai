# CampusFlow AI

A multi-agent campus intelligence platform that helps students make informed decisions about where to go and when by showing estimated queues, crowd levels, and facility availability.

## 📋 Project Overview

CampusFlow provides real-time insights into campus facility usage, helping students:
- Check library seat availability and crowd levels
- Estimate canteen wait times
- See stationery shop queue lengths
- Get AI-powered recommendations for optimal visit timing

## 🏗️ Project Structure

```
CampusFlow-ai/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── core/           # Configuration, security, dependencies
│   │   ├── models/         # Database models (SQLAlchemy)
│   │   ├── services/       # Business logic & agent modules
│   │   └── utils/          # Helper functions
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React + Vite frontend
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Screen components
│   │   ├── services/      # API client & utilities
│   │   ├── utils/         # Helper functions
│   │   └── assets/        # Images, styles
│   └── package.json       # Node dependencies
├── data/                  # Seed data & datasets
├── docs/                  # Documentation & API specs
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (or SQLite for local development)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Current Scope (Phase 1)

**Facilities:**
- Central Library (occupancy, seat availability)
- Main Canteen (queue estimates, wait times)
- Stationery & Print Shop (crowd levels, availability)

**Data Sources:**
- Student-submitted reports
- Historical patterns
- Simulated data (clearly labeled for demo)

## 🧠 Multi-Agent Architecture

1. **Campus Data Module** — Retrieves facility details
2. **Crowd Estimator** — Calculates wait times from reports
3. **Demand Forecaster** — Predicts busy periods
4. **Routing Engine** — Recommends optimal facilities
5. **Campus Assistant** — LLM-powered natural language interface
6. **Orchestrator** — Coordinates all modules

## 🛠️ Tech Stack

- **Frontend:** React, Vite, Tailwind CSS
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL / Supabase
- **LLM:** Groq API (backend only)
- **Maps:** Leaflet / MapLibre (planned)

## 📅 Development Roadmap

- [x] Project planning & requirements
- [x] UI/UX prototype design
- [ ] Backend API & database setup
- [ ] Frontend component development
- [ ] Student report submission system
- [ ] Crowd estimation logic
- [ ] AI assistant integration
- [ ] Historical data & forecasting
- [ ] Testing & validation

## 🔒 Security & Privacy

- API keys stored in environment variables (never in frontend)
- Minimal personal data collection
- Anonymous reporting system
- Clear labeling of data sources (live/simulated/historical)

## 📝 License

This is a college project. All rights reserved.

---

