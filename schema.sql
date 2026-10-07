-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    device_token VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reports table
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    hazard_type VARCHAR(100),
    severity FLOAT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Infrastructure table
CREATE TABLE infrastructure (
    id SERIAL PRIMARY KEY,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    type VARCHAR(100),
    criticality VARCHAR(50),
    description TEXT
);

-- Chat messages table
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    geofence_id INTEGER,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Hazard zones table
CREATE TABLE hazard_zones (
    id SERIAL PRIMARY KEY,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    radius FLOAT,
    severity FLOAT,
    hazard_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Model features table (for ML)
CREATE TABLE model_features (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES reports(id),
    rainfall FLOAT,
    snowmelt FLOAT,
    affected_users INTEGER,
    infrastructure_risk FLOAT,
    season VARCHAR(20),
    hazard_severity FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_location ON users USING GIST(location);
CREATE INDEX idx_reports_location ON reports USING GIST(location);
CREATE INDEX idx_infrastructure_location ON infrastructure USING GIST(location);
CREATE INDEX idx_hazard_zones_location ON hazard_zones USING GIST(location);