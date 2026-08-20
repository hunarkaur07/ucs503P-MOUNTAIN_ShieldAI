# 🏔️ Mountain Shield AI

Multi-agent disaster prediction platform for Himachal Pradesh. Real-time 🚨 landslide risk detection + 👥 community reporting + 🗺️ geofenced alerts.

## 🎯 What It Does

Predicts landslide hazards across Kinnaur, Spiti, and Lahaul using ML models. Five autonomous agents coordinate to detect risks, validate reports, verify photo evidence, and detect network cascade failures. When a hazard is detected, community members within 20km get WebSocket alerts.

**Live demo**: Dashboard shows hazard zones, weather forecast strip, agent status cards, and chat for geofenced areas.

## 🛠️ Stack

**Backend** 🔧
- FastAPI (Python)
- PostgreSQL + PostGIS (spatial queries)
- Socket.IO (WebSocket for chat)
- XGBoost (landslide prediction)

**Frontend** 🎨
- JS + HTML/CSS
- Real-time charts & interactive dashboard

**ML** 🤖
- XGBoost for landslide prediction
- Community voting for report validation

## 🧠 Architecture

### Five Agents

1. **🌍 Hazard Agent** - XGBoost landslide prediction. Runs on weather + terrain data (landslide.csv). Returns risk zones.
2. **👥 Community Agent** - Validates ground-truth disaster reports from users.
3. **📍 Presence & Chat Agent** - 20km geofenced WebSocket chat. Auto-notifies users when hazards detected nearby.
4. **⚡ Network Agent** - Detects cascade failures in infrastructure (power grids, roads).
5. **✅ Verifier Agent** - Photo verification + community voting on authenticity.

**🎭 Orchestrator** (main.py) - Routes data between agents, maintains state, triggers alerts.

### Current Status ✨

- ✅ Hazard Agent fully working (localhost:8000)
- ✅ All 5 agent files created (community_agent.py, network_agent.py, presence_agent.py, verifier_agent.py)
- ✅ Frontend scaffold (index.html, script.js, style.css)
- 📍 Two main endpoints: `/hazard_predict` and `/agent_status`

## 🚀 Setup

### Backend

```bash
cd backend
pip install -r requirements.txt

# Start FastAPI server
python main.py

# Runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
# Open index.html in browser
# Or use live server: python -m http.server 5173
```

## 📁 File Structure

```
├── backend/
│   ├── agents/
│   │   ├── community_agent.py      # Report validation
│   │   ├── hazard_agent.py         # XGBoost predictions ⭐
│   │   ├── network_agent.py        # Infrastructure failure detection
│   │   ├── presence_agent.py       # Geofenced chat + alerts
│   │   └── verifier_agent.py       # Photo verification
│   ├── landslide.csv               # Training data
│   ├── main.py                     # FastAPI orchestrator
│   ├── requirements.txt
│   └── __init__.py
├── frontend/
│   ├── index.html                  # Dashboard UI
│   ├── script.js                   # Logic + charts
│   └── style.css                   # Styling
└── README.md
```

## ▶️ Running

1. **Start backend**: `python backend/main.py`
2. **Open frontend**: Open `frontend/index.html` in browser
3. Dashboard loads on localhost + connects to FastAPI

## 👥 Team

- **🔧 Backend**: Hunar Kaur, Bismanjot Singh
- **⚡ Frontend**: Anmol Jwandha, Jasmeh Singh Sodhi

## 🎯 Next Steps

- [ ] Upgrade remaining 4 agents with real data
- [ ] Integrate weather API
- [ ] User authentication + profiles
- [ ] Mobile push notifications
- [ ] PostgreSQL + PostGIS backend integration

## 📜 License

