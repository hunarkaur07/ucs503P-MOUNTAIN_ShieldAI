class NetworkAgent:

    def predict(self):
        return [
            {
                "id": 1,
                "infrastructure_type": "Power Grid",
                "location": "Kinnaur",
                "status": "disconnected",
                "impact_level": 85,
                "timestamp": "2026-08-18T20:00:00"
            },
            {
                "id": 2,
                "infrastructure_type": "Road Network",
                "location": "Spiti",
                "status": "blocked",
                "impact_level": 60,
                "timestamp": "2026-08-18T20:05:00"
            },
            {
                "id": 3,
                "infrastructure_type": "Water Supply",
                "location": "Shimla",
                "status": "damaged",
                "impact_level": 45,
                "timestamp": "2026-08-18T20:10:00"
            }
        ]