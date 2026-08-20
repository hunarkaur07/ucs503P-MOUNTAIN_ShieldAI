import pandas as pd
import random
from datetime import datetime, timedelta

class HazardAgent:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data = self.load_data()
    
    def load_data(self):
        df = pd.read_csv(self.csv_path)
        return df.head(10).to_dict('records')
    
    def calculate_risk_score(self, row):
        rainfall = float(row.get('Rainfall_mm', 0)) / 300 * 30
        slope = float(row.get('Slope_Angle', 0)) / 60 * 30
        soil = float(row.get('Soil_Saturation', 0)) * 25
        veg = (1 - float(row.get('Vegetation_Cover', 0.5))) * 15
        
        risk = min(100, rainfall + slope + soil + veg)
        return round(risk, 2)
    
    def predict(self):
        predictions = []
        now = datetime.now()
        
        for i, row in enumerate(self.data):
            lat = round(random.uniform(31.5, 32.8), 2)
            lng = round(random.uniform(77.8, 79.0), 2)
            
            risk_score = self.calculate_risk_score(row)
            timestamp = (now - timedelta(hours=i)).isoformat()
            
            predictions.append({
                "id": i + 1,
                "lat": lat,
                "lng": lng,
                "risk_score": risk_score,
                "rainfall": round(float(row.get('Rainfall_mm', 0)), 2),
                "slope": round(float(row.get('Slope_Angle', 0)), 2),
                "timestamp": timestamp
            })
        
        return predictions