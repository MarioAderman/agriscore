"""Train the AgriScore Random Forest model on synthetic data.

Usage: uv run python ml/train.py
"""

import csv

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

INPUT = "ml/training_data.csv"
OUTPUT = "ml/model.pkl"

FEATURE_COLUMNS = [
    "ndvi_mean",
    "ndvi_trend",
    "avg_temperature",
    "total_precipitation",
    "soil_moisture",
    "et0",
    "area_hectares",
    "crop_type_idx",
    "agri_establishments",
    "months_active",
    "challenges_completed",
]


def main():
    # Load data
    with open(INPUT) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    X = np.array([[float(row[col]) for col in FEATURE_COLUMNS] for row in rows])
    y = np.array([float(row["total_score"]) for row in rows])

    print(f"Dataset: {len(rows)} samples, {len(FEATURE_COLUMNS)} features")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"MAE: {mae:.2f}")
    print(f"R²:  {r2:.4f}")

    # Feature importance
    print("\nFeature importance:")
    for name, imp in sorted(zip(FEATURE_COLUMNS, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {name:.<30} {imp:.4f}")

    # Save
    joblib.dump(model, OUTPUT)
    import os

    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"\nModel saved to {OUTPUT} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
