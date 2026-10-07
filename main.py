from fastapi import FastAPI, Depends, WebSocket
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter
from slowapi.util import get_remote_address

import json

from database import engine, get_db
from models import Base

from geofencing import (
    get_users_in_radius,
    get_reports_in_radius,
    get_affected_users,
    is_user_in_geofence
)

from auth import router as auth_router

from chat import chat_websocket, manager

from spam_detection import detect_spam

from redis_stream import get_recent_messages


# =========================
# RATE LIMITER
# =========================

limiter = Limiter(
    key_func=get_remote_address
)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="AI Mountain Shield Backend"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# AUTH ROUTER
# =========================

app.include_router(
    auth_router
)


# =========================
# RATE LIMITER STATE
# =========================

app.state.limiter = limiter


# =========================
# CREATE DATABASE TABLES
# =========================

Base.metadata.create_all(
    bind=engine
)


# =========================
# ROOT
# =========================

@app.get("/")
def read_root():

    return {
        "message": "AI Mountain Shield API Running"
    }


# =========================
# HAZARDS MAP API
# =========================

@app.get("/api/hazards")
@limiter.limit("100/hour")
def get_hazards(
    request,
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            id,
            ST_AsGeoJSON(location) AS geometry,
            severity,
            hazard_type,
            radius
        FROM hazard_zones
    """)

    result = db.execute(
        query
    ).fetchall()

    features = []

    for row in result:

        features.append({
            "type": "Feature",
            "id": row[0],
            "geometry": json.loads(row[1]),
            "properties": {
                "severity": row[2],
                "hazard_type": row[3],
                "radius": row[4]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


# =========================
# USER LOCATIONS MAP API
# =========================

@app.get("/api/users/locations")
@limiter.limit("100/hour")
def get_user_locations(
    request,
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            id,
            name,
            ST_AsGeoJSON(location) AS geometry
        FROM users
        WHERE location IS NOT NULL
    """)

    result = db.execute(
        query
    ).fetchall()

    features = []

    for row in result:

        features.append({
            "type": "Feature",
            "id": row[0],
            "geometry": json.loads(row[2]),
            "properties": {
                "name": row[1]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


# =========================
# INFRASTRUCTURE MAP API
# =========================

@app.get("/api/infrastructure")
@limiter.limit("100/hour")
def get_infrastructure(
    request,
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            id,
            type,
            criticality,
            ST_AsGeoJSON(location) AS geometry
        FROM infrastructure
    """)

    result = db.execute(
        query
    ).fetchall()

    features = []

    for row in result:

        features.append({
            "type": "Feature",
            "id": row[0],
            "geometry": json.loads(row[3]),
            "properties": {
                "type": row[1],
                "criticality": row[2]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


# =========================
# USERS IN GEOFENCE API
# =========================

@app.get("/api/geofence/users")
@limiter.limit("100/hour")
def get_geofence_users(
    request,
    lat: float,
    lon: float,
    radius: int = 20,
    db: Session = Depends(get_db)
):

    users = get_users_in_radius(
        db=db,
        lat=lat,
        lon=lon,
        radius_km=radius
    )

    return {
        "center": {
            "lat": lat,
            "lon": lon
        },
        "radius_km": radius,
        "user_count": len(users),
        "users": [
            {
                "id": u[0],
                "name": u[1],
                "lat": u[3],
                "lon": u[2]
            }
            for u in users
        ]
    }


# =========================
# REPORTS IN GEOFENCE API
# =========================

@app.get("/api/geofence/reports")
@limiter.limit("100/hour")
def get_geofence_reports(
    request,
    lat: float,
    lon: float,
    radius: int = 20,
    db: Session = Depends(get_db)
):

    reports = get_reports_in_radius(
        db=db,
        lat=lat,
        lon=lon,
        radius_km=radius
    )

    return {
        "center": {
            "lat": lat,
            "lon": lon
        },
        "radius_km": radius,
        "report_count": len(reports),
        "reports": [
            {
                "id": r[0],
                "hazard_type": r[1],
                "severity": r[2],
                "lat": r[4],
                "lon": r[3]
            }
            for r in reports
        ]
    }


# =========================
# AFFECTED USERS API
# =========================

@app.get("/api/geofence/affected-users")
@limiter.limit("100/hour")
def get_affected(
    request,
    hazard_lat: float,
    hazard_lon: float,
    radius: int = 20,
    db: Session = Depends(get_db)
):

    affected = get_affected_users(
        db=db,
        hazard_lat=hazard_lat,
        hazard_lon=hazard_lon,
        radius_km=radius
    )

    return {
        "hazard_location": {
            "lat": hazard_lat,
            "lon": hazard_lon
        },
        "radius_km": radius,
        "affected_user_count": len(affected),
        "affected_users": affected
    }


# =========================
# CHECK USER IN GEOFENCE API
# =========================

@app.get("/api/geofence/check")
@limiter.limit("100/hour")
def check_in_geofence(
    request,
    user_lat: float,
    user_lon: float,
    hazard_lat: float,
    hazard_lon: float,
    radius: int = 20,
    db: Session = Depends(get_db)
):

    in_geofence = is_user_in_geofence(
        db=db,
        user_lat=user_lat,
        user_lon=user_lon,
        hazard_lat=hazard_lat,
        hazard_lon=hazard_lon,
        radius_km=radius
    )

    return {
        "user_location": {
            "lat": user_lat,
            "lon": user_lon
        },
        "hazard_location": {
            "lat": hazard_lat,
            "lon": hazard_lon
        },
        "radius_km": radius,
        "in_geofence": in_geofence
    }


# =========================
# JWT PROTECTED WEBSOCKET CHAT
# =========================

@app.websocket("/ws/chat/{geofence_id}")
async def websocket_chat(
    websocket: WebSocket,
    geofence_id: int
):

    await chat_websocket(
        websocket=websocket,
        geofence_id=geofence_id
    )


# =========================
# GEOFENCE PRESENCE API
# =========================

@app.get("/api/geofence/{geofence_id}/presence")
def get_geofence_presence(
    geofence_id: int
):

    online_users = manager.get_online_users(
        geofence_id
    )

    return {
        "geofence_id": geofence_id,
        "online_user_count": len(online_users),
        "online_users": online_users
    }


# =========================
# ANOMALY DETECTION REQUEST
# =========================

class SpamDetectionRequest(BaseModel):

    Rainfall_mm: float = 0
    Slope_Angle: float = 0
    Soil_Saturation: float = 0
    Vegetation_Cover: float = 0
    Earthquake_Activity: float = 0
    Proximity_to_Water: float = 0

    Soil_Type_Gravel: int = 0
    Soil_Type_Sand: int = 0
    Soil_Type_Silt: int = 0


# =========================
# ANOMALY DETECTION API
# =========================

@app.post("/api/spam/detect")
@limiter.limit("100/hour")
def detect_report_spam(
    request,
    report: SpamDetectionRequest
):

    result = detect_spam(
        report.model_dump()
    )

    return result


# =========================
# REDIS RECENT CHAT MESSAGES
# =========================

@app.get("/api/chat/recent")
@limiter.limit("100/hour")
async def get_recent_chat_messages(
    request,
    count: int = 20
):

    messages = await get_recent_messages(
        count=count
    )

    return {
        "message_count": len(messages),
        "messages": messages
    }

# =========================
# REPORT SUBMISSION
# =========================

class ReportRequest(BaseModel):
    user_id: int
    lat: float
    lon: float
    hazard_type: str
    severity: float
    description: str = ""

    Rainfall_mm: float = 0
    Slope_Angle: float = 0
    Soil_Saturation: float = 0
    Vegetation_Cover: float = 0
    Earthquake_Activity: float = 0
    Proximity_to_Water: float = 0

    Soil_Type_Gravel: int = 0
    Soil_Type_Sand: int = 0
    Soil_Type_Silt: int = 0


@app.post("/api/reports")
@limiter.limit("100/hour")
def create_report(
    request,
    report: ReportRequest,
    db: Session = Depends(get_db)
):

    spam_result = detect_spam(
        {
            "Rainfall_mm": report.Rainfall_mm,
            "Slope_Angle": report.Slope_Angle,
            "Soil_Saturation": report.Soil_Saturation,
            "Vegetation_Cover": report.Vegetation_Cover,
            "Earthquake_Activity": report.Earthquake_Activity,
            "Proximity_to_Water": report.Proximity_to_Water,
            "Soil_Type_Gravel": report.Soil_Type_Gravel,
            "Soil_Type_Sand": report.Soil_Type_Sand,
            "Soil_Type_Silt": report.Soil_Type_Silt
        }
    )

    if spam_result["is_spam"]:
        return {
            "message": "Report rejected as suspicious",
            "spam_detection": spam_result
        }

    query = text("""
        INSERT INTO reports (
            user_id,
            location,
            hazard_type,
            severity,
            description
        )
        VALUES (
            :user_id,
            ST_SetSRID(
                ST_MakePoint(:lon, :lat),
                4326
            )::geography,
            :hazard_type,
            :severity,
            :description
        )
        RETURNING id
    """)

    result = db.execute(
        query,
        {
            "user_id": report.user_id,
            "lat": report.lat,
            "lon": report.lon,
            "hazard_type": report.hazard_type,
            "severity": report.severity,
            "description": report.description
        }
    ).fetchone()

    db.commit()

    return {
        "message": "Report submitted successfully",
        "report_id": result[0],
        "spam_detection": spam_result
    }

# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )