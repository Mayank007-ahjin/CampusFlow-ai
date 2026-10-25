# 🎯 CampusFlow AI - Quick Start Card

## ⚡ Start Development (2 terminals)

### Terminal 1 - Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python seed_data.py
uvicorn app.main:app --reload
```
✅ Backend: http://localhost:8000  
📚 API Docs: http://localhost:8000/docs

### Terminal 2 - Frontend
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend: http://localhost:5173

---

## 📁 Key Files to Know

```
backend/app/
├── main.py                          # FastAPI app entry
├── api/
│   ├── facilities.py               # GET/POST facilities
│   ├── reports.py                  # Submit student reports
│   └── recommendations.py          # AI recommendations
├── services/
│   ├── crowd_estimator.py         # Weighted averaging logic
│   └── recommendation_engine.py   # Scoring algorithm + LLM
└── models/
    ├── facility.py                 # Database tables
    └── schemas.py                  # API request/response models

frontend/src/
├── App.jsx                         # Main app with state
├── components/
│   ├── HomeScreen.jsx             # Facility list
│   ├── DetailScreen.jsx           # Details + report form
│   └── ChatScreen.jsx             # AI assistant
└── services/api.js                # API client
```

---

## 🧪 Quick Test Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Get all facilities
curl http://localhost:8000/api/v1/facilities

# Submit a report
curl -X POST http://localhost:8000/api/v1/reports \
  -H "Content-Type: application/json" \
  -d '{"facility_id": 1, "crowd_level": "low", "available_seats": 50}'

# Get recommendation
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Where should I study?"}'
```

---

## 🎨 Customization Points

### Add Your Campus Facilities
Edit: `backend/seed_data.py`
```python
Facility(
    name="Your Building Name",
    type=FacilityType.LIBRARY,  # or CANTEEN, STATIONERY
    location="Building X, Floor Y",
    opening_time="08:00",
    closing_time="22:00",
    # ... rest of fields
)
```

### Add Groq API Key (Optional - for LLM responses)
Edit: `backend/.env`
```
GROQ_API_KEY=your_key_here
```
Get free key: https://console.groq.com/keys

### Change Colors
Edit: `frontend/tailwind.config.js`
```javascript
colors: {
  brand: {
    primary: '#YOUR_COLOR',  // Change this
  }
}
```

---

## 🐛 Troubleshooting

**"Module not found" in backend:**
```bash
pip install -r requirements.txt
```

**"Command not found: vite" in frontend:**
```bash
npm install
```

**Frontend shows "Loading facilities...":**
- Check backend is running on port 8000
- Open browser console (F12) to see errors

**Database errors:**
```bash
cd backend
rm campusflow.db  # Delete old DB
python seed_data.py  # Recreate
```

---

## 📊 Project Stats

- **31 files** created
- **Backend**: 15 Python files, 1,200+ lines
- **Frontend**: 10 JS/JSX files, 800+ lines
- **Database**: 2 tables (Facility, Report)
- **API**: 11 endpoints
- **Components**: 4 React screens

---

## 🚀 Development Workflow

1. Make changes to backend → FastAPI auto-reloads
2. Make changes to frontend → Vite HMR updates instantly
3. Submit test reports via UI
4. Check database: `sqlite3 backend/campusflow.db`
5. View API logs in backend terminal
6. Test endpoints in Swagger UI: http://localhost:8000/docs

---

## 📦 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend API | FastAPI | Fast, modern, auto-docs |
| Backend Logic | Python 3.9+ | Clean, readable algorithms |
| Database | SQLAlchemy + SQLite | Easy setup, PostgreSQL-ready |
| Frontend UI | React 18 | Component-based, efficient |
| Build Tool | Vite | Lightning fast HMR |
| Styling | Tailwind CSS | Utility-first, consistent |
| LLM (Optional) | Groq API | Fast inference, free tier |

---

## ✅ What's Working Now

- ✅ Full CRUD for facilities
- ✅ Student report submission
- ✅ Crowd estimation with weighted averaging
- ✅ AI recommendations (deterministic + optional LLM)
- ✅ 3-screen mobile UI
- ✅ Real-time data updates
- ✅ Confidence scoring
- ✅ Data source tracking
- ✅ API documentation
- ✅ Seed data with 3 facilities

---

## 🎯 MVP Demo Script

1. Open frontend → Show dashboard with 3 facilities
2. Point out status badges (Low/Moderate/High)
3. Click Library → Show detailed view with metrics
4. Submit report "Packed" → Show success feedback
5. Go back → Crowd level updates to "High"
6. Click AI Assistant tab → Ask "Where's the shortest line?"
7. Show recommendation with reasoning
8. Open API docs → Show Swagger UI at /docs
9. Execute API call in Swagger → Show live JSON response

**Time: 3-5 minutes**

---

## 🔮 Easy Extensions

1. **Add more facilities** → Edit seed_data.py
2. **Mobile app** → React Native uses same API
3. **Real sensors** → POST to /reports endpoint
4. **Analytics dashboard** → Query Report table
5. **Email alerts** → When crowd level changes
6. **Campus map** → Integrate Leaflet with lat/long
7. **Historical charts** → Show busy periods
8. **User accounts** → Add authentication
9. **Push notifications** → WebSocket live updates
10. **QR codes** → Quick facility check-in

---

**Built:** October 24, 2026 07:18 UTC  
**Status:** 🟢 Ready to Run  
**Docs:** See docs/SETUP.md and PROJECT_SUMMARY.md

---

## 💡 Pro Tips

- Keep backend terminal visible to see API logs
- Use browser DevTools Network tab to debug API calls
- SQLite database is just a file → easy to backup/reset
- Tailwind classes update live → no build step needed
- FastAPI auto-generates docs → use /docs for testing
- Environment variables in .env → never commit API keys

---

**Need help?** Check docs/SETUP.md for detailed instructions.

🎉 **Happy coding!**
