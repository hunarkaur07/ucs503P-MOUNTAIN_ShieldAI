from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.hazard_agent import HazardAgent
from agents.community_agent import CommunityAgent
from agents.presence_agent import PresenceAgent
from agents.network_agent import NetworkAgent
from agents.verifier_agent import VerifierAgent


app = FastAPI()


# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create agents
agent = HazardAgent("landslide_dataset.csv")
community_agent = CommunityAgent()
presence_agent = PresenceAgent()
network_agent = NetworkAgent()
verifier_agent = VerifierAgent()


# Agent status endpoint
@app.get("/api/agents")
def get_agents():
    return {
        "agents": [
            {
                "id": "hazard",
                "name": "Hazard Agent",
                "status": "online"
            },
            {
                "id": "community",
                "name": "Community Agent",
                "status": "online"
            },
            {
                "id": "presence",
                "name": "Presence & Chat Agent",
                "status": "online"
            },
            {
                "id": "network",
                "name": "Network Agent",
                "status": "online"
            },
            {
                "id": "verifier",
                "name": "Verifier Agent",
                "status": "online"
            }
        ]
    }


# Hazard Agent
@app.get("/api/hazards")
def get_hazards():
    return {
        "hazards": agent.predict()
    }


# Community Agent
@app.get("/api/community-reports")
def get_community():
    return {
        "reports": community_agent.predict()
    }


# Presence & Chat Agent
@app.get("/api/presence-chat")
def get_presence():
    return {
        "messages": presence_agent.predict()
    }


# Network Agent
@app.get("/api/network-failures")
def get_network():
    return {
        "failures": network_agent.predict()
    }


# Verifier Agent
@app.get("/api/verified-photos")
def get_verifier():
    return {
        "photos": verifier_agent.predict()
    }


# Start server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001
    )