"""SageMaker inference script for AgriScore Random Forest model."""

import json
import os

import joblib
import numpy as np

CROP_TYPES = ["maiz", "frijol", "chile", "tomate", "sorgo", "aguacate", "cana", "trigo"]


def model_fn(model_dir):
    """Load the sklearn model from the SageMaker model directory."""
    return joblib.load(os.path.join(model_dir, "model.pkl"))


def input_fn(request_body, content_type):
    """Parse JSON input with 11 features."""
    if content_type != "application/json":
        raise ValueError(f"Unsupported content type: {content_type}")
    return json.loads(request_body)


def predict_fn(input_data, model):
    """Run prediction and compute sub-scores."""
    crop_type = input_data.get("crop_type")
    crop_idx = CROP_TYPES.index(crop_type.lower()) if crop_type and crop_type.lower() in CROP_TYPES else 0

    ndvi_mean = input_data["ndvi_mean"]
    ndvi_trend = input_data.get("ndvi_trend", 0.02)
    avg_temperature = input_data["avg_temperature"]
    total_precipitation = input_data["total_precipitation"]
    soil_moisture = input_data["soil_moisture"]
    et0 = input_data["et0"]
    area_hectares = input_data.get("area_hectares", 5.0)
    agri_establishments = input_data.get("agri_establishments", 100)
    months_active = input_data.get("months_active", 1)
    challenges_completed = input_data.get("challenges_completed", 0)

    features = np.array(
        [[ndvi_mean, ndvi_trend, avg_temperature, total_precipitation,
          soil_moisture, et0, area_hectares, crop_idx,
          agri_establishments, months_active, challenges_completed]]
    )

    # Model trained on 0-100, convert to 300-850 scale
    raw_score = float(np.clip(model.predict(features)[0], 0, 100))
    total_score = 300 + (raw_score / 100) * 550

    def _to_850(s):
        return 300 + (float(np.clip(s, 0, 100)) / 100) * 550

    sub_productive = _to_850(
        (ndvi_mean * 60) + (ndvi_trend * 40) + (min(area_hectares, 20) / 20 * 20)
    )
    sub_climate = _to_850(
        (1 - abs(avg_temperature - 24) / 20) * 40
        + (min(total_precipitation, 1200) / 1200) * 30
        + soil_moisture * 30
    )
    sub_behavioral = _to_850(
        (challenges_completed / max(months_active, 1)) * 60
        + (min(months_active, 12) / 12) * 40
    )
    sub_esg = _to_850(
        (max(ndvi_trend, 0) / 0.15) * 50 + (challenges_completed / 12) * 50
    )

    return {
        "total_score": round(total_score, 1),
        "sub_productive": round(sub_productive, 1),
        "sub_climate": round(sub_climate, 1),
        "sub_behavioral": round(sub_behavioral, 1),
        "sub_esg": round(sub_esg, 1),
    }


def output_fn(prediction, accept):
    """Serialize prediction to JSON."""
    return json.dumps(prediction), "application/json"
