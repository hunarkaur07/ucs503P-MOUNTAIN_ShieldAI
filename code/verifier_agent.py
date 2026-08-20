class VerifierAgent:

    def predict(self):
        return [
            {
                "id": 1,
                "photo_url": "photo_1.jpg",
                "verified": True,
                "vote_count": 12,
                "confidence": 92,
                "timestamp": "2026-08-18T20:00:00"
            },
            {
                "id": 2,
                "photo_url": "photo_2.jpg",
                "verified": False,
                "vote_count": 3,
                "confidence": 35,
                "timestamp": "2026-08-18T20:05:00"
            },
            {
                "id": 3,
                "photo_url": "photo_3.jpg",
                "verified": True,
                "vote_count": 8,
                "confidence": 81,
                "timestamp": "2026-08-18T20:10:00"
            }
        ]