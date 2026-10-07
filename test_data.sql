-- Insert test users
INSERT INTO users (email, name, password_hash, location) VALUES
('user1@example.com', 'User 1', 'hashed_pw_1', ST_GeographyFromText('SRID=4326;POINT(76.3711 30.8977)')),
('user2@example.com', 'User 2', 'hashed_pw_2', ST_GeographyFromText('SRID=4326;POINT(76.3800 30.9000)')),
('user3@example.com', 'User 3', 'hashed_pw_3', ST_GeographyFromText('SRID=4326;POINT(76.4000 30.9100)'));

-- Insert test reports
INSERT INTO reports (user_id, location, hazard_type, severity, description) VALUES
(1, ST_GeographyFromText('SRID=4326;POINT(76.3711 30.8977)'), 'landslide', 0.75, 'Heavy rainfall risk'),
(2, ST_GeographyFromText('SRID=4326;POINT(76.3800 30.9000)'), 'flooding', 0.60, 'River overflow'),
(3, ST_GeographyFromText('SRID=4326;POINT(76.4000 30.9100)'), 'avalanche', 0.85, 'Snow accumulation');

-- Insert test infrastructure
INSERT INTO infrastructure (location, type, criticality, description) VALUES
(ST_GeographyFromText('SRID=4326;POINT(76.3750 30.9000)'), 'hospital', 'HIGH', 'District Hospital'),
(ST_GeographyFromText('SRID=4326;POINT(76.3900 30.8950)'), 'school', 'MEDIUM', 'Government School');

-- Insert test hazard zones
INSERT INTO hazard_zones (location, radius, severity, hazard_type) VALUES
(ST_GeographyFromText('SRID=4326;POINT(76.3711 30.8977)'), 20000, 0.75, 'landslide'),
(ST_GeographyFromText('SRID=4326;POINT(76.3800 30.9000)'), 15000, 0.60, 'flooding');