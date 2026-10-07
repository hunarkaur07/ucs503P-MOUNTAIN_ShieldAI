import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from pathlib import Path


# ==========================================
# DATASET + FEATURE CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "landslide_dataset.csv"


FEATURE_COLUMNS = [
    "Rainfall_mm",
    "Slope_Angle",
    "Soil_Saturation",
    "Vegetation_Cover",
    "Earthquake_Activity",
    "Proximity_to_Water",
    "Soil_Type_Gravel",
    "Soil_Type_Sand",
    "Soil_Type_Silt"
]


# ==========================================
# LOAD DATASET
# ==========================================

df = pd.read_csv(
    DATASET_PATH
)


# ==========================================
# PREPARE FEATURES
# ==========================================

X = df[
    FEATURE_COLUMNS
]


# ==========================================
# SCALE FEATURES
# ==========================================

scaler = StandardScaler()

scaled_features = scaler.fit_transform(
    X
)


# ==========================================
# TRAIN ISOLATION FOREST
# ==========================================

model = IsolationForest(
    contamination=0.05,
    random_state=42
)

model.fit(
    scaled_features
)


# ==========================================
# SPAM / ANOMALY DETECTION FUNCTION
# ==========================================

def detect_spam(
    report_data: dict
):

    # Create DataFrame with exact feature names
    features = pd.DataFrame(
        [[
            report_data.get("Rainfall_mm", 0),
            report_data.get("Slope_Angle", 0),
            report_data.get("Soil_Saturation", 0),
            report_data.get("Vegetation_Cover", 0),
            report_data.get("Earthquake_Activity", 0),
            report_data.get("Proximity_to_Water", 0),
            report_data.get("Soil_Type_Gravel", 0),
            report_data.get("Soil_Type_Sand", 0),
            report_data.get("Soil_Type_Silt", 0)
        ]],
        columns=FEATURE_COLUMNS
    )


    # Scale features
    scaled_features = scaler.transform(
        features
    )


    # Predict anomaly
    prediction = model.predict(
        scaled_features
    )[0]


    # Calculate anomaly score
    score = model.decision_function(
        scaled_features
    )[0]


    return {

        "is_spam":
            bool(prediction == -1),

        "prediction":
            int(prediction),

        "anomaly_score":
            float(score)

    }