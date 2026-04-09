# ml/ — Modelo de Machine Learning

Modelo de predicción AgriScore basado en Random Forest para scoring crediticio agrícola.

## Por qué Random Forest

- **Interpretabilidad** — Los sub-scores se calculan con fórmulas deterministas transparentes. El modelo total es una combinación ponderada que los analistas de crédito pueden entender y auditar.
- **Rendimiento con datos tabulares** — Random Forest es consistentemente competitivo con datos tabulares estructurados, sin necesidad de feature engineering complejo.
- **Velocidad de inferencia** — Predicción en milisegundos, permite cargar el modelo en memoria (Lambda/Fargate) sin necesidad de GPU.
- **Robusto con datos sintéticos** — Tolera bien las distribuciones generadas sintéticamente para bootstrapping del MVP.

## Escala 300-850

Similar a FICO/Buro de Credito, el AgriScore opera en escala 300-850. El modelo fue entrenado en escala 0-100 y la conversión se aplica post-prediccion:

```
score_850 = 300 + (score_100 / 100) * 550
```

## Features de Entrada (11)

| # | Feature | Fuente | Rango |
|---|---------|--------|-------|
| 1 | `ndvi_mean` | Sentinel Hub | 0.05 - 0.85 |
| 2 | `ndvi_trend` | Sentinel Hub | -0.3 - 0.3 |
| 3 | `avg_temperature` | Open-Meteo | 12 - 38 C |
| 4 | `total_precipitation` | Open-Meteo | 100 - 2000 mm |
| 5 | `soil_moisture` | NASA POWER | 0.05 - 0.9 |
| 6 | `et0` | NASA POWER | 2.0 - 9.0 mm/dia |
| 7 | `area_hectares` | Agricultor | 0.5 - 100 ha |
| 8 | `crop_type_idx` | Agricultor | 0-7 (8 cultivos) |
| 9 | `agri_establishments` | INEGI | 0 - 500 |
| 10 | `months_active` | Plataforma | 1 - 24 |
| 11 | `challenges_completed` | Gamificacion | 0 - 24 |

## Sub-scores y Pesos

| Sub-score | Peso | Fórmula |
|-----------|------|---------|
| **Productivo** | 40% | NDVI mean * 60 + NDVI trend * 40 + area normalizada * 20 |
| **Climático** | 25% | Proximidad a 24C * 40 + precipitación normalizada * 30 + humedad * 30 |
| **Comportamiento** | 20% | Retos/mes * 60 + antiguedad normalizada * 40 |
| **ESG** | 15% | Tendencia NDVI positiva * 50 + retos completados * 50 |

Cada sub-score se calcula de forma determinista (transparente) y se convierte a escala 300-850.

## Reproducir el Modelo

```bash
# 1. Generar datos sinteticos
uv run python ml/generate_data.py

# 2. Entrenar modelo
uv run python ml/train.py

# Salida: ml/model.pkl (serializado con joblib)
```

El modelo entrenado (`model.pkl`) esta en `.gitignore`.
