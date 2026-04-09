# app/ — Backend AgriScore

Aplicación principal construida con FastAPI (Python 3.12). Contiene toda la lógica de negocio: agente conversacional IA, pipeline de evaluación, endpoints REST y modelos de datos.

## Por qué FastAPI

- **Async nativo** — Las llamadas a LLM, APIs satelitales y de clima son I/O-bound. FastAPI con asyncio permite manejar multiples conversaciones WhatsApp simultáneamente sin bloquear.
- **Pydantic integrado** — Validación automática de request/response. Los schemas de la API se generan automáticamente en `/docs` (OpenAPI).
- **Inyección de dependencias** — Manejo limpio de sesiones de BD, autenticación y API keys sin acoplar la lógica de negocio.
- **Rendimiento** — Sobre Uvicorn (ASGI), comparable a Node.js/Go para cargas I/O-bound.

## Dos Entrypoints — Servicios Aislados

El backend se divide en dos servicios Fargate independientes:

| Entrypoint | Servicio | Proposito | Dependencias pesadas |
|------------|----------|-----------|---------------------|
| `main.py` | **Core** | Agente IA + pipeline de evaluación | anthropic, openai, boto3, scikit-learn, sentinelhub |
| `main_api.py` | **API REST** | Endpoints de consulta (solo lectura) | sqlalchemy, pydantic |

**Por qué separar:** Un crash del agente IA (OOM procesando documentos grandes, timeout de LLM) no debe afectar los endpoints que consultan instituciones financieras. Diferentes patrones de tráfico, diferentes necesidades de escalamiento.

## Estructura

```
app/
├── main.py              # Entrypoint Core: webhook WhatsApp → agente → pipeline
├── main_api.py          # Entrypoint API REST: /api/customer/*, /api/farmer/*
├── config.py            # Configuracion via variables de entorno (Pydantic Settings)
├── auth.py              # Verificacion JWT (Cognito) para endpoints de agricultor
├── dependencies.py      # Inyeccion: sesion BD, validacion API key
├── llm.py               # Factory de clientes LLM (Bedrock, Anthropic, OpenAI, Groq)
│
├── agent/               # Agente conversacional IA
│   ├── agent.py         #   Loop de tool-use (max 5 iteraciones por mensaje)
│   ├── handler.py       #   Parser de webhooks EvolutionAPI → IncomingMessage
│   ├── prompts.py       #   System prompt en español mexicano
│   └── tools.py         #   5 herramientas: save_profile, save_location,
│                        #   trigger_evaluation, get_agriscore, extract_document
│
├── api/                 # Endpoints REST
│   ├── customer.py      #   GET /api/customer/* — para instituciones financieras (API key)
│   ├── farmer.py        #   GET /api/farmer/* — para agricultores (JWT Cognito)
│   └── webhook.py       #   POST /api/webhook/whatsapp — receptor de mensajes
│
├── pipeline/            # Pipeline de evaluación (5 pasos)
│   ├── orchestrator.py  #   Orquestación local o via Step Functions
│   ├── document.py      #   Paso 1: Extracción de docs (Claude Vision)
│   ├── satellite.py     #   Paso 2: Datos NDVI (Sentinel Hub / Copernicus)
│   ├── climate.py       #   Paso 3a: Clima (Open-Meteo + NASA POWER)
│   ├── socioeconomic.py #   Paso 3b: Socioeconómico (INEGI)
│   ├── scoring.py       #   Paso 4: Cálculo AgriScore (ML, escala 300-850)
│   └── expediente.py    #   Paso 5: Generación de expediente + notificación
│
├── models/
│   ├── database.py      # ORM: Farmer, Parcela, Application, AgriScoreResult, etc.
│   └── schemas.py       # Schemas Pydantic para request/response
│
├── services/
│   └── evolution.py     # Cliente HTTP para EvolutionAPI (envio de mensajes WhatsApp)
│
└── db/
    └── connection.py    # Pool de conexiones async (asyncpg + SQLAlchemy)
```

## Agente IA

El agente utiliza el patron de **tool-use** de Claude:

1. Recibe mensaje de WhatsApp via webhook
2. Carga los ultimos 20 mensajes de la conversación (contexto)
3. Ejecuta loop de herramientas (máximo 5 iteraciones)
4. Persiste conversación en BD
5. Responde al agricultor via EvolutionAPI

**Proveedores LLM soportados:** Bedrock (producción), Anthropic API, OpenAI, Groq. Selección via `LLM_PROVIDER` en config.

## Pipeline de Evaluacion

```
Agricultor envia documentos + ubicación
        ↓
[1] ExtractDocs — Claude Vision extrae datos, valida GPS en México
        ↓
[2a] FetchSatellite ─┐
[2b] FetchClimate  ──┤ (paralelo)
[2c] FetchSocioeco ──┘
        ↓
[3] CalculateScore — Modelo ML + sub-scores deterministas → 300-850
        ↓
[4] GenerateExpediente — Almacena en RDS, notifica via WhatsApp
```

## Sistema de Scoring (300-850)

Similar a FICO, el AgriScore opera en escala 300-850:

| Sub-score | Peso | Fuente de datos |
|-----------|------|----------------|
| Productivo | 40% | NDVI satelital, tendencia, área cultivada |
| Climático | 25% | Temperatura, precipitación, humedad del suelo |
| Comportamiento | 20% | Retos completados, meses activos |
| ESG | 15% | Tendencia NDVI, practicas sostenibles |

**Categorias de riesgo:**
- **Bajo** (>= 658) — Sujeto de crédito confiable
- **Moderado** (>= 520) — Requiere garantías adicionales
- **Alto** (< 520) — Perfil de riesgo elevado

## Endpoints REST

### Customer (`/api/customer/*`) — Autenticacion: API Key

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/farmers` | Lista agricultores con score completado |
| GET | `/farmers/{id}` | Perfil completo con sub-scores |
| GET | `/farmers/{id}/expediente` | Expediente completo (score + satelital + clima + socioeconómico) |
| GET | `/farmers/{id}/satellite` | Imagen satelital NDVI o RGB |
| GET | `/stats` | Estadísticas agregadas del dashboard |

### Farmer (`/api/farmer/*`) — Autenticación: JWT Cognito

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/{phone}/profile` | Perfil del agricultor |
| GET | `/{phone}/agriscore` | Score actual e histórico |
| GET | `/{phone}/challenges` | Retos de gamificación |
| GET | `/{phone}/satellite` | Imagen satelital de parcela |

## Seguridad

### Inyeccion de Prompts (OWASP LLM01)

El agente implementa multiples capas de defensa:

1. **Etiquetado XML** — Todo contenido del usuario se envuelve en `<user_message>...</user_message>` antes de enviarlo al modelo. El system prompt instruye tratar el contenido dentro de esas etiquetas como datos, no como instrucciones.
2. **Directivas explicitas** — El system prompt incluye reglas de seguridad: no revelar instrucciones, no ejecutar acciones fuera del dominio AgriScore, no acceder a datos de otros agricultores.
3. **Limite de iteraciones** — Maximo 5 rondas de tool-use por mensaje (`MAX_TOOL_ROUNDS`), previniendo loops infinitos.
4. **Herramientas de alcance limitado** — Solo 5 herramientas disponibles, cada una con alcance especifico (guardar perfil, ubicacion, disparar evaluacion, consultar score, extraer documento).
5. **Errores enmascarados** — Las excepciones de herramientas devuelven mensajes genericos al usuario, sin exponer detalles internos.

### Autenticacion

- **Customer API** — Header `X-API-Key` validado con `secrets.compare_digest()` (comparacion timing-safe contra ataques de timing).
- **Farmer API** — JWT firmado por Cognito, verificado via JWKS con validacion de issuer y audience.
- **Bypass de desarrollo** — Solo activo cuando `ENVIRONMENT != production` y `COGNITO_USER_POOL_ID` no esta configurado. Bloqueado en produccion.

### CORS

Origenes configurables via `ALLOWED_ORIGINS` (separados por coma). En produccion se configura con el dominio especifico de CloudFront. Metodos limitados a GET/POST, headers a Content-Type, Authorization y X-API-Key.

### Base de Datos

Todas las consultas usan SQLAlchemy ORM (parametrizacion automatica). Sin consultas SQL crudas en el codigo.
