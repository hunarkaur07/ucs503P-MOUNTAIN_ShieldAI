from spam_detection import detect_spam


suspicious_report = {
    "Rainfall_mm": 10000,
    "Slope_Angle": 89,
    "Soil_Saturation": 10,
    "Vegetation_Cover": 100,
    "Earthquake_Activity": 1000,
    "Proximity_to_Water": 10000,
    "Soil_Type_Gravel": 1,
    "Soil_Type_Sand": 1,
    "Soil_Type_Silt": 1
}


result = detect_spam(suspicious_report)

print(result)