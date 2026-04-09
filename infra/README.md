# infra/ — Infraestructura AWS

Definiciones de contenedores, funciones Lambda, y orquestacion serverless. Toda la infraestructura se despliega en AWS us-east-1.

## Por qué Arquitectura Híbrida

| Componente | Computo | Justificacion |
|-----------|---------|---------------|
| Agente IA + Pipeline | **Fargate** | Conversaciones LLM de larga duracion, sin cold starts, pool de conexiones BD, modelo ML en memoria |
| API REST | **Fargate** | Servicio ligero aislado del agente — un crash del LLM no afecta consultas de instituciones financieras |
| EvolutionAPI | **Fargate** | WebSocket persistente con servidores de WhatsApp |
| Pipeline steps | **Lambda** | Ejecución corta, escalamiento automático, pago por uso. Ideal para pasos individuales del pipeline |
| Orquestación | **Step Functions** | Manejo nativo de paralelismo, reintentos y estados de error sin código custom |
| Cron mensual | **EventBridge** | Re-evaluación programada de todos los agricultores |

## Dockerfiles — 3 Servicios Aislados

```
docker/
├── Dockerfile.core       # Agente IA + Pipeline (pesado: anthropic, scikit-learn, sentinelhub)
├── Dockerfile.api-rest   # API REST solo lectura (ligero: sqlalchemy, pydantic)
└── Dockerfile.evolution  # EvolutionAPI (imagen base de atendai)
```

| Dockerfile | Imagen base | CPU/Mem | Incluye ML model | Deps pesadas |
|-----------|-------------|---------|-------------------|-------------|
| `Dockerfile.core` | python:3.12-slim | 512/1024 | Si | anthropic, openai, boto3, scikit-learn, sentinelhub |
| `Dockerfile.api-rest` | python:3.12-slim | 256/512 | No | sqlalchemy, pydantic, httpx |
| `Dockerfile.evolution` | atendai/evolution-api | 256/512 | N/A | Node.js runtime |

**Por qué separar Core y API REST:** Diferentes dependencias, diferentes patrones de fallo, diferentes necesidades de escala. La imagen API REST es significativamente más ligera (sin modelo ML ni SDKs de LLM).

## Lambda Handlers — Pipeline de Evaluación

```
lambda/
├── handlers/
│   ├── extract_docs.py           # Paso 1: Claude Vision + validacion GPS
│   ├── fetch_satellite.py        # Paso 2a: Sentinel Hub (NDVI)
│   ├── fetch_climate.py          # Paso 2b: Open-Meteo + NASA POWER
│   ├── fetch_socioeconomic.py    # Paso 2c: INEGI
│   ├── calculate_score.py        # Paso 3: ML scoring (modelo desde S3)
│   ├── generate_expediente.py    # Paso 4: Reporte + notificación WhatsApp
│   └── monthly_trigger.py        # Cron: re-evaluación mensual (EventBridge)
│
└── shared/
    └── db.py                     # Utilidades compartidas de BD (psycopg2)
```

| Función | Memoria | Timeout | Layers |
|---------|---------|---------|--------|
| extract-docs | 256 MB | 60s | common |
| fetch-satellite | 512 MB | 90s | common + science |
| fetch-climate | 256 MB | 60s | common |
| fetch-socioeconomic | 256 MB | 60s | common |
| calculate-score | 256 MB | 30s | common |
| generate-expediente | 256 MB | 60s | common |

**Lambda Layers:**
- `common-deps` — httpx, psycopg2-binary, pydantic, pydantic-settings, anthropic
- `science-deps` — Pillow (procesamiento de imágenes)

## Step Functions — Orquestación

Definido en `step-functions.json`. Flujo:

```
ExtractDocs
    ↓
ParallelFetch ─── FetchSatellite
              ├── FetchClimate
              └── FetchSocioeconomic
    ↓
CalculateScore
    ↓
GenerateExpediente
    ↓
PipelineSucceeded / PipelineFailed
```

Cada paso tiene configuración de `Retry` (3 intentos, backoff exponencial) y `Catch` (transicion a estado de error).

## SageMaker

```
sagemaker/
└── inference.py    # Script de inferencia para endpoint SageMaker
```

Alternativa al modelo local en Lambda. Cuando `SAGEMAKER_ENDPOINT` está configurado, `calculate_score.py` invoca el endpoint en lugar de cargar el modelo desde S3. Útil para modelos más grandes o cuando se necesita GPU.

## Despliegue

`scripts/deploy_aws.sh` es el script de bootstrap para crear toda la infraestructura desde cero (una sola vez). Despúes del bootstrap, GitHub Actions maneja los despliegues de código (ver `.github/workflows/`).
