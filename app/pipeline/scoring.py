"""Step 4: Calculate AgriScore using the trained ML model + deterministic sub-scores."""

import logging

import numpy as np

logger = logging.getLogger(__name__)

# Same crop type encoding as training
CROP_TYPES = ["maiz", "frijol", "chile", "tomate", "sorgo", "aguacate", "cana", "trigo"]


def predict_agriscore(
    model,
    ndvi_mean: float,
    ndvi_trend: float,
    avg_temperature: float,
    total_precipitation: float,
    soil_moisture: float,
    et0: float,
    area_hectares: float,
    crop_type: str | None,
    agri_establishments: int,
    months_active: int = 1,
    challenges_completed: int = 0,
) -> dict:
    """Predict AgriScore and compute sub-scores.

    Returns dict with total_score, sub_productive, sub_climate, sub_behavioral, sub_esg.
    """
    crop_idx = CROP_TYPES.index(crop_type.lower()) if crop_type and crop_type.lower() in CROP_TYPES else 0

    features = np.array(
        [
            [
                ndvi_mean,
                ndvi_trend,
                avg_temperature,
                total_precipitation,
                soil_moisture,
                et0,
                area_hectares,
                crop_idx,
                agri_establishments,
                months_active,
                challenges_completed,
            ]
        ]
    )

    # ML model prediction (model trained on 0-100, convert to 300-850)
    raw_score = float(np.clip(model.predict(features)[0], 0, 100))
    total_score = 300 + (raw_score / 100) * 550

    # Deterministic sub-scores (compute on 0-100, then convert to 300-850)
    def _to_850(score_0_100: float) -> float:
        return 300 + (float(np.clip(score_0_100, 0, 100)) / 100) * 550

    sub_productive = _to_850((ndvi_mean * 60) + (ndvi_trend * 40) + (min(area_hectares, 20) / 20 * 20))
    sub_climate = _to_850(
        (1 - abs(avg_temperature - 24) / 20) * 40 + (min(total_precipitation, 1200) / 1200) * 30 + soil_moisture * 30
    )
    sub_behavioral = _to_850((challenges_completed / max(months_active, 1)) * 60 + (min(months_active, 12) / 12) * 40)
    sub_esg = _to_850((max(ndvi_trend, 0) / 0.15) * 50 + (challenges_completed / 12) * 50)

    result = {
        "total_score": round(total_score, 1),
        "sub_productive": round(sub_productive, 1),
        "sub_climate": round(sub_climate, 1),
        "sub_behavioral": round(sub_behavioral, 1),
        "sub_esg": round(sub_esg, 1),
    }

    logger.info("AgriScore calculated: %s", result)
    return result
