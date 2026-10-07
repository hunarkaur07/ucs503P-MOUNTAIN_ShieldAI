from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    location = Column(Geography('POINT', 4326))
    device_token = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    location = Column(Geography('POINT', 4326), nullable=False)
    hazard_type = Column(String(100))
    severity = Column(Float)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Infrastructure(Base):
    __tablename__ = "infrastructure"
    
    id = Column(Integer, primary_key=True)
    location = Column(Geography('POINT', 4326), nullable=False)
    type = Column(String(100))
    criticality = Column(String(50))
    description = Column(String)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    geofence_id = Column(Integer)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class HazardZone(Base):
    __tablename__ = "hazard_zones"
    
    id = Column(Integer, primary_key=True)
    location = Column(Geography('POINT', 4326), nullable=False)
    radius = Column(Float)
    severity = Column(Float)
    hazard_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelFeatures(Base):
    __tablename__ = "model_features"
    
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    rainfall = Column(Float)
    snowmelt = Column(Float)
    affected_users = Column(Integer)
    infrastructure_risk = Column(Float)
    season = Column(String(20))
    hazard_severity = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)