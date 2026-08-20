import json
import random
from datetime import datetime, timedelta

class CommunityAgent:
    def __init__(self):
        self.reports = self.load_reports()
    
    def load_reports(self):
        # Mock community reports
        return [
            {"lat": 31.5, "lng": 78.2, "text": "Landslide visible on hillside", "verified": True},
            {"lat": 31.6, "lng": 78.3, "text": "Heavy rainfall, soil erosion", "verified": True},
            {"lat": 31.7, "lng": 78.1, "text": "Trees uprooted near road", "verified": False},
            {"lat": 31.55, "lng": 78.25, "text": "Cracks in ground", "verified": True},
            {"lat": 31.65, "lng": 78.35, "text": "Water flowing down slope", "verified": False},
        ]
    
    def predict(self):
        predictions = []
        now = datetime.now()
        
        for i, report in enumerate(self.reports):
            timestamp = (now - timedelta(hours=i*2)).isoformat()
            
            predictions.append({
                "id": i + 1,
                "lat": report['lat'],
                "lng": report['lng'],
                "text": report['text'],
                "verified": report['verified'],
                "timestamp": timestamp,
                "votes": random.randint(1, 10)
            })
        
        return predictions