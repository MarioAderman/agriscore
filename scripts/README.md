# scripts/ — Scripts Operacionales

Scripts para despliegue, empaquetado y configuración inicial de la plataforma.

## Scripts

| Script | Descripción | Uso |
|--------|-------------|-----|
| `deploy_aws.sh` | Bootstrap completo de infraestructura AWS (ECR, ALB, ECS, Lambda, Step Functions, S3, IAM) | `./scripts/deploy_aws.sh` |
| `package_lambda.sh` | Empaqueta handlers Lambda + layers de dependencias en archivos ZIP | `bash scripts/package_lambda.sh all` |
| `setup_db.py` | Inicializa tablas en PostgreSQL + PostGIS | `uv run python scripts/setup_db.py` |

## deploy_aws.sh

Script imperativo que crea toda la infraestructura desde cero en una sola ejecución. Diseñado para bootstrap inicial — los despliegues posteriores de código se manejan via GitHub Actions CI/CD.

**8 pasos:**
1. Crear repositorios ECR (core, api-rest, evolution)
2. Construir y subir imágenes Docker
3. Crear bucket S3, subir modelo ML
4. Configurar security groups (ALB, API, Evolution, Lambda)
5. Crear ALB + target groups con routing basado en path
6. Crear cluster ECS, roles IAM, task definitions (3 servicios)
7. Desplegar servicios ECS en Fargate
8. Empaquetar y desplegar Lambdas, layers y Step Functions

**Teardown:** `./scripts/deploy_aws.sh teardown` elimina todos los recursos (excepto RDS, ECR y S3).

## package_lambda.sh

Empaqueta los handlers Lambda y sus dependencias compartidas en formato ZIP para despliegue.

```bash
bash scripts/package_lambda.sh all        # Todos los handlers + layers
bash scripts/package_lambda.sh handlers   # Solo handlers
bash scripts/package_lambda.sh layers     # Solo layers de dependencias
```

**Layers generados:**
- `common-deps` — httpx, psycopg2-binary, pydantic, anthropic
- `science-deps` — Pillow
