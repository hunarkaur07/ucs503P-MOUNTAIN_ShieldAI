class PresenceAgent:

    def predict(self):
        return [
            {
                "id": 1,
                "lat": 31.5,
                "lng": 78.2,
                "username": "user1",
                "message": "Evacuation alert issued",
                "distance_km": 2.1,
                "timestamp": "2026-08-18T20:00:00"
            },
            {
                "id": 2,
                "lat": 31.6,
                "lng": 78.3,
                "username": "user2",
                "message": "Road blocked near Kinnaur",
                "distance_km": 5.3,
                "timestamp": "2026-08-18T20:05:00"
            },
            {
                "id": 3,
                "lat": 31.7,
                "lng": 78.1,
                "username": "user3",
                "message": "Heavy rainfall in the area",
                "distance_km": 8.4,
                "timestamp": "2026-08-18T20:10:00"
            }
        ]