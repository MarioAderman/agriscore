# AgriScore

Plataforma cloud-native que genera perfiles crediticios agrícolas verificados utilizando datos satelitales, procesamiento de documentos con IA y gamificación. Reemplaza los requisitos tradicionales de buró de crédito con scoring alternativo para agricultores no bancarizados.

**Hackathon:** Genius Arena @ Talent Land 2026 — Track: Capital One "Finanzas para un Futuro Sostenible"
**Equipo:** Fintegra

## Demo

<!-- TODO: Reemplazar con enlace al video de YouTube -->
[![Demo AgriScore](https://img.shields.io/badge/YouTube-Demo-red?style=for-the-badge&logo=youtube)](https://youtube.com/PLACEHOLDER)

## Arquitectura

<!-- TODO: Reemplazar con diagrama actualizado -->
![Arquitectura AWS](docs/references/images/AWS_architecture.png)

**3 servicios Fargate aislados + pipeline serverless:**

| Servicio | Ruta | Función |
|----------|------|---------|
| **Core** (Agente IA + Pipeline) | `/api/webhook/*` | Recibe mensajes WhatsApp, ejecuta agente con tool-use, orquesta pipeline de evaluación |
| **API REST** (Consulta) | `/api/customer/*`, `/api/farmer/*` | Endpoints de lectura para instituciones financieras y agricultores |
| **EvolutionAPI** | WhatsApp bridge | Puente WebSocket ↔ HTTP para mensajería WhatsApp |

**Pipeline de evaluación (Step Functions → 6 Lambdas):**

1. **ExtractDocs** — Extracción de documentos via Claude Vision + validacion GPS
2. **FetchSatellite** — Datos NDVI de Sentinel Hub (Copernicus) *(paralelo)*
3. **FetchClimate** — Datos climáticos de Open-Meteo + NASA POWER *(paralelo)*
4. **FetchSocioeconomic** — Indicadores de INEGI *(paralelo)*
5. **CalculateScore** — Modelo ML Random Forest, escala 300-850
6. **GenerateExpediente** — Genera reporte y notifica al agricultor via WhatsApp

## Estructura del Repositorio

```
agriscore/
├── app/                        # Backend FastAPI (Python)
│   ├── agent/                  #   Agente conversacional IA (WhatsApp)
│   ├── api/                    #   Endpoints REST (customer, farmer, webhook)
│   ├── pipeline/               #   Pipeline de evaluacion (5 pasos)
│   ├── models/                 #   Modelos ORM y schemas Pydantic
│   ├── services/               #   Integraciones externas (EvolutionAPI)
│   ├── db/                     #   Conexión PostgreSQL + PostGIS
│   ├── main.py                 #   Entrypoint: Core (agente + pipeline)
│   └── main_api.py             #   Entrypoint: API REST (consulta)
│
├── frontend/                   # Aplicacion web React (Next.js)
│   └── src/
│       ├── app/                #   Páginas (inicio, cultivo, reporte, retos, perfil)
│       ├── components/         #   Componentes UI reutilizables
│       ├── hooks/              #   Custom hooks para datos
│       └── lib/                #   API client y utilidades
│
├── infra/                      # Infraestructura AWS
│   ├── docker/                 #   Dockerfiles (Core, API REST, EvolutionAPI)
│   ├── lambda/                 #   Handlers de Lambda (6 pasos del pipeline)
│   ├── sagemaker/              #   Script de inferencia SageMaker
│   └── step-functions.json     #   Definición del state machine
│
├── ml/                         # Modelo de Machine Learning
│   ├── generate_data.py        #   Generación de datos sintéticos
│   └── train.py                #   Entrenamiento del modelo Random Forest
│
├── scripts/                    # Scripts operacionales
│   ├── deploy_aws.sh           #   Bootstrap de infraestructura AWS
│   ├── package_lambda.sh       #   Empaquetado de funciones Lambda
│   └── setup_db.py             #   Inicialización de base de datos
│
├── .github/workflows/ci.yml   # CI/CD (lint, build, deploy)
├── docker-compose.yml          # Desarrollo local
└── pyproject.toml              # Dependencias Python (uv)
```

## Inicio Rápido

### Requisitos previos

- Python 3.12+ con [uv](https://docs.astral.sh/uv/)
- Node.js 22+
- PostgreSQL con PostGIS
- Docker (opcional, para desarrollo local completo)

### Variables de entorno

Crear archivo `.env` en la raiz:

| Variable | Descripcion |
|----------|-------------|
| `DATABASE_URL` | Conexion PostgreSQL |
| `ANTHROPIC_API_KEY` | API key de Claude |
| `OPENAI_API_KEY` | API key de OpenAI (Whisper STT/TTS) |
| `SENTINEL_HUB_ID` | Client ID de Copernicus Data Space |
| `SENTINEL_HUB_SECRET` | Client secret de Copernicus Data Space |
| `INEGI_TOKEN` | Token API de INEGI |
| `CUSTOMER_API_KEY` | API key para endpoints de instituciones financieras |

### Desarrollo local

```bash
# Backend (Core — agente + pipeline)
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Backend (API REST — endpoints de consulta)
uv run uvicorn app.main_api:app --reload --port 8001

# Frontend
cd frontend && npm install && npm run dev

# Base de datos
uv run python scripts/setup_db.py

# Modelo ML (regenerar)
uv run python ml/generate_data.py
uv run python ml/train.py
```

### Docker Compose

```bash
docker compose up
```

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Cloud** | AWS (Fargate, Lambda, Step Functions, ALB, S3, CloudFront, EventBridge) |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0, asyncpg |
| **Frontend** | Next.js 16, React 19, Tailwind CSS 4, TypeScript |
| **IA** | Anthropic Claude (agente con tool-use), OpenAI Whisper (STT/TTS) |
| **ML** | scikit-learn (Random Forest), escala 300-850 |
| **Base de datos** | PostgreSQL + PostGIS (RDS) |
| **Satelital** | Sentinel Hub API (Copernicus, Sentinel-2) |
| **APIs externas** | INEGI, Open-Meteo, NASA POWER |
| **WhatsApp** | EvolutionAPI (bridge WebSocket) |

## Seguridad

| Amenaza | Mitigación |
|---------|-----------|
| **Inyeccion SQL** | SQLAlchemy ORM (consultas parametrizadas). Lambda usa psycopg2 con placeholders `%s`. Sin SQL crudo. |
| **Inyeccion de prompts** | Contenido del usuario envuelto en etiquetas `<user_message>` (separacion estructural). System prompt con directivas de seguridad explícitas. Máximo 5 iteraciones de herramientas por mensaje. |
| **CORS** | Orígenes permitidos configurables via `ALLOWED_ORIGINS` (no wildcard en produccion). Métodos y headers restringidos. |
| **Autenticacion** | API key con comparación timing-safe (`secrets.compare_digest`). JWT Cognito con verificación RS256 + JWKS. Bypass de desarrollo bloqueado en producción. |
| **Secretos** | Todos via variables de entorno (`.env` en gitignore). Sin credenciales hardcodeadas. |
| **Errores** | Mensajes genéricos al usuario. Excepciones internas solo en logs del servidor. |

## Equipo Fintegra

| Miembro | Rol |
|---------|-----|
| **Mario Aderman** | IA / Cloud |
| **Sebastian** | Negocios / Finanzas |
| **Ana** | UX / UI |
