# CampusFlow AI

A multi-agent campus intelligence platform that helps students make informed decisions about where to go and when by showing estimated queues, crowd levels, and facility availability.

## 📋 Project Overview

CampusFlow provides real-time insights into campus facility usage, helping students:
- Check library seat availability and crowd levels across multiple campus branches (Central Library & AB2 Branch)
- Estimate canteen wait times and rush status
- Check stationery shop queue lengths and operating hours
- **OpenCampus GIS Map Viewer**: Interactive OpenStreetMap-style campus map modal featuring live vector building blocks, pan/drag capabilities, zoom controls, and dynamic crowd status badges
- Get AI-powered recommendations and multi-facility route itineraries via direct database-grounded smart recommendation engine (natural language responses with bullet points, zero emojis, and auto-scrolling thinking state)

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
- Central Library (Academic Block 1)
- Central Library (AB2 Branch, Ground Floor)
- Main Canteen (Mess Building)
- Stationery & Print Shop (Near Workshop Building)

**Features & Enhancements:**
- 12-Hour Clock Format (`AM`/`PM`) for operating hours across all facilities and backend validations
- Interactive OpenCampus GIS Map Viewer with pan, zoom, and live facility markers
- Precision AI recommendation filtering (excludes libraries/unrelated facilities when specific office or stationery queries are made)

## 🧠 Multi-Agent Architecture

1. **Campus Data Module** — Retrieves facility details
2. **Crowd Estimator** — Calculates wait times from reports
3. **Demand Forecaster** — Predicts busy periods
4. **Routing Engine** — Recommends optimal facilities
5. **Campus Assistant** — LLM-powered natural language interface
6. **Orchestrator** — Coordinates all modules

## 🛠️ Tech Stack

- **Frontend:** React, Vite, Tailwind CSS, OpenCampus GIS Vector Viewport
- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic V2
- **Database:** SQLite / PostgreSQL
- **LLM:** Groq API (Groq SDK) for natural language recommendations and routing
- **Maps:** Custom interactive OpenStreetMap vector viewer with pan, drag, and zoom controls

## 📅 Development Roadmap

- [x] Project planning & requirements
- [x] UI/UX prototype design
- [x] Backend API & database setup
- [x] Frontend component development
- [x] Student report submission system
- [x] Crowd estimation logic
- [x] AI assistant integration
- [ ] Historical data & forecasting
- [x] Testing & validation

## 🔒 Security & Privacy

- API keys stored in environment variables (never in frontend)
- Minimal personal data collection
- Anonymous reporting system
- Clear labeling of data sources (live/simulated/historical)

## 📝 License

This is a college project. All rights reserved.

---

