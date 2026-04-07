"""Generate synthetic Mexican farmer profiles for training the AgriScore model.

Usage: uv run python ml/generate_data.py
"""

import csv
import random

import numpy as np

random.seed(42)
np.random.seed(42)

NUM_SAMPLES = 1000
OUTPUT = "ml/training_data.csv"

# Crop types common in Mexican agriculture
CROP_TYPES = ["maiz", "frijol", "chile", "tomate", "sorgo", "aguacate", "cana", "trigo"]


def generate_profile() -> dict:
    """Generate a single synthetic farmer profile with realistic distributions."""
    crop = random.choice(CROP_TYPES)

    # NDVI: healthy vegetation 0.2-0.8, agricultural land typically 0.3-0.7
    ndvi_mean = np.clip(np.random.normal(0.45, 0.15), 0.05, 0.85)
    ndvi_trend = np.clip(np.random.normal(0.02, 0.08), -0.3, 0.3)

    # Climate (Mexican agriculture ranges)
    avg_temperature = np.clip(np.random.normal(24, 5), 12, 38)
    total_precipitation = np.clip(np.random.normal(800, 300), 100, 2000)
    soil_moisture = np.clip(np.random.normal(0.4, 0.15), 0.05, 0.9)
    et0 = np.clip(np.random.normal(5.0, 1.5), 2.0, 9.0)

    # Farm characteristics
    area_hectares = np.clip(np.random.lognormal(1.5, 0.8), 0.5, 100)
    crop_type_idx = CROP_TYPES.index(crop)

    # Socioeconomic
    agri_establishments = int(np.clip(np.random.normal(150, 80), 0, 500))

    # Behavioral (gamification)
    months_active = int(np.clip(np.random.exponential(6), 1, 24))
    challenges_completed = int(np.clip(np.random.poisson(months_active * 0.6), 0, 24))

    # Compute sub-scores (deterministic formulas)
    sub_productive = np.clip(
        (ndvi_mean * 60) + (ndvi_trend * 40) + (min(area_hectares, 20) / 20 * 20),
        0, 100,
    )
    sub_climate = np.clip(
        # Moderate temp is better, adequate rain, good moisture
        (1 - abs(avg_temperature - 24) / 20) * 40
        + (min(total_precipitation, 1200) / 1200) * 30
        + soil_moisture * 30,
        0, 100,
    )
    sub_behavioral = np.clip(
        (challenges_completed / max(months_active, 1)) * 60
        + (min(months_active, 12) / 12) * 40,
        0, 100,
    )
    sub_esg = np.clip(
        (max(ndvi_trend, 0) / 0.15) * 50
        + (challenges_completed / 12) * 50,
        0, 100,
    )

    # Total AgriScore: weighted combination + noise
    total_score = np.clip(
        0.40 * sub_productive
        + 0.25 * sub_climate
        + 0.20 * sub_behavioral
        + 0.15 * sub_esg
        + np.random.normal(0, 3),  # Small noise
        0, 100,
    )

    return {
        "ndvi_mean": round(ndvi_mean, 4),
        "ndvi_trend": round(ndvi_trend, 4),
        "avg_temperature": round(avg_temperature, 2),
        "total_precipitation": round(total_precipitation, 2),
        "soil_moisture": round(soil_moisture, 4),
        "et0": round(et0, 2),
        "area_hectares": round(area_hectares, 2),
        "crop_type_idx": crop_type_idx,
        "agri_establishments": agri_establishments,
        "months_active": months_active,
        "challenges_completed": challenges_completed,
        "sub_productive": round(sub_productive, 2),
        "sub_climate": round(sub_climate, 2),
        "sub_behavioral": round(sub_behavioral, 2),
        "sub_esg": round(sub_esg, 2),
        "total_score": round(total_score, 2),
    }


def main():
    profiles = [generate_profile() for _ in range(NUM_SAMPLES)]

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=profiles[0].keys())
        writer.writeheader()
        writer.writerows(profiles)

    scores = [p["total_score"] for p in profiles]
    print(f"Generated {NUM_SAMPLES} profiles → {OUTPUT}")
    print(f"Score range: {min(scores):.1f} - {max(scores):.1f}")
    print(f"Score mean: {np.mean(scores):.1f}, std: {np.std(scores):.1f}")


if __name__ == "__main__":
    main()
