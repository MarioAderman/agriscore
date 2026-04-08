#!/usr/bin/env bash
# AgriScore — AWS Deploy Script
# Run on April 7 to stand up the full stack.
# Prerequisites: aws cli configured, docker running.
#
# Usage:
#   chmod +x scripts/deploy_aws.sh
#   ./scripts/deploy_aws.sh          # Full deploy
#   ./scripts/deploy_aws.sh teardown  # Delete everything (stop billing)

set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
REGION="us-east-1"
PROJECT="agriscore-test"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# ECR
ECR_API="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${PROJECT}-api"
ECR_EVOLUTION="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${PROJECT}-evolution"

# ECS
CLUSTER="${PROJECT}-cluster"
API_SERVICE="${PROJECT}-api"
EVOLUTION_SERVICE="${PROJECT}-evolution"

# Networking (default VPC)
VPC_ID=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text --region $REGION)
SUBNETS=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query 'Subnets[*].SubnetId' --output text --region $REGION | tr '\t' ',')

# S3
S3_BUCKET="${PROJECT}-data-${ACCOUNT_ID}"

# ── Colors ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# ── Teardown ────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "teardown" ]]; then
  warn "Tearing down all AWS resources..."

  echo "Stopping ECS services..."
  aws ecs update-service --cluster $CLUSTER --service $API_SERVICE --desired-count 0 --region $REGION 2>/dev/null || true
  aws ecs update-service --cluster $CLUSTER --service $EVOLUTION_SERVICE --desired-count 0 --region $REGION 2>/dev/null || true

  echo "Deleting ECS services..."
  aws ecs delete-service --cluster $CLUSTER --service $API_SERVICE --force --region $REGION 2>/dev/null || true
  aws ecs delete-service --cluster $CLUSTER --service $EVOLUTION_SERVICE --force --region $REGION 2>/dev/null || true

  echo "Deleting ECS cluster..."
  aws ecs delete-cluster --cluster $CLUSTER --region $REGION 2>/dev/null || true

  echo "Deleting ALB..."
  ALB_ARN=$(aws elbv2 describe-load-balancers --names ${PROJECT}-alb --query 'LoadBalancers[0].LoadBalancerArn' --output text --region $REGION 2>/dev/null || echo "")
  if [[ -n "$ALB_ARN" && "$ALB_ARN" != "None" ]]; then
    LISTENERS=$(aws elbv2 describe-listeners --load-balancer-arn $ALB_ARN --query 'Listeners[*].ListenerArn' --output text --region $REGION 2>/dev/null || echo "")
    for L in $LISTENERS; do aws elbv2 delete-listener --listener-arn $L --region $REGION 2>/dev/null || true; done
    aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN --region $REGION 2>/dev/null || true
  fi

  echo "Deleting target groups..."
  for TG_NAME in ${PROJECT}-api-tg ${PROJECT}-evolution-tg; do
    TG_ARN=$(aws elbv2 describe-target-groups --names $TG_NAME --query 'TargetGroups[0].TargetGroupArn' --output text --region $REGION 2>/dev/null || echo "")
    if [[ -n "$TG_ARN" && "$TG_ARN" != "None" ]]; then
      aws elbv2 delete-target-group --target-group-arn $TG_ARN --region $REGION 2>/dev/null || true
    fi
  done

  echo "Deleting Lambda functions..."
  for fname in extract-docs fetch-satellite fetch-climate fetch-socioeconomic calculate-score generate-expediente pipeline-proxy; do
    aws lambda delete-function --function-name ${PROJECT}-${fname} --region $REGION 2>/dev/null || true
  done

  echo "Deleting Lambda layers..."
  for layer in ${PROJECT}-common-deps ${PROJECT}-science-deps; do
    VERSIONS=$(aws lambda list-layer-versions --layer-name $layer --query 'LayerVersions[*].Version' --output text --region $REGION 2>/dev/null || echo "")
    for v in $VERSIONS; do
      aws lambda delete-layer-version --layer-name $layer --version-number $v --region $REGION 2>/dev/null || true
    done
  done

  echo "Deleting Step Functions state machine..."
  SFN_ARN=$(aws stepfunctions list-state-machines --query "stateMachines[?name=='${PROJECT}-pipeline'].stateMachineArn | [0]" --output text --region $REGION 2>/dev/null || echo "")
  if [[ -n "$SFN_ARN" && "$SFN_ARN" != "None" ]]; then
    aws stepfunctions delete-state-machine --state-machine-arn $SFN_ARN --region $REGION 2>/dev/null || true
  fi

  echo "Deleting security groups..."
  for SG_NAME in ${PROJECT}-alb-sg ${PROJECT}-api-sg ${PROJECT}-evolution-sg ${PROJECT}-lambda-sg; do
    SG_ID=$(aws ec2 describe-security-groups --filters Name=group-name,Values=$SG_NAME --query 'SecurityGroups[0].GroupId' --output text --region $REGION 2>/dev/null || echo "")
    if [[ -n "$SG_ID" && "$SG_ID" != "None" ]]; then
      aws ec2 delete-security-group --group-id $SG_ID --region $REGION 2>/dev/null || true
    fi
  done

  log "Teardown complete. RDS, ECR repos, and S3 bucket preserved (manual delete if needed)."
  exit 0
fi

# ── Step 1: ECR Repos ──────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Step 1: ECR Repositories"
echo "═══════════════════════════════════════════════════"

aws ecr describe-repositories --repository-names ${PROJECT}-api --region $REGION 2>/dev/null \
  || aws ecr create-repository --repository-name ${PROJECT}-api --region $REGION
log "ECR: ${PROJECT}-api"

aws ecr describe-repositories --repository-names ${PROJECT}-evolution --region $REGION 2>/dev/null \
  || aws ecr create-repository --repository-name ${PROJECT}-evolution --region $REGION
log "ECR: ${PROJECT}-evolution"

# ── Step 2: Build & Push Docker Images ──────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Step 2: Build & Push Docker Images"
echo "═══════════════════════════════════════════════════"

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

docker build -f infra/docker/Dockerfile.api -t ${ECR_API}:latest .
docker push ${ECR_API}:latest
log "Pushed ${PROJECT}-api image"

docker build -f infra/docker/Dockerfile.evolution -t ${ECR_EVOLUTION}:latest .
docker push ${ECR_EVOLUTION}:latest
log "Pushed ${PROJECT}-evolution image"

# ── Step 3: S3 Bucket ──────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Step 3: S3 Bucket"
echo "═══════════════════════════════════════════════════"

aws s3api head-bucket --bucket $S3_BUCKET --region $REGION 2>/dev/null \
  || aws s3api create-bucket --bucket $S3_BUCKET --region $REGION
log "S3: $S3_BUCKET"

# Upload ML model
if [[ -f ml/model.pkl ]]; then
  aws s3 cp ml/model.pkl s3://${S3_BUCKET}/ml/model.pkl
  log "Uploaded model.pkl"
else
  warn "ml/model.pkl not found — run 'uv run python ml/train.py' first"
fi

# ── Step 4: Security Groups ────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Step 4: Security Groups"
echo "═══════════════════════════════════════════════════"

create_sg() {
  local NAME=$1 DESC=$2
  local SG_ID=$(aws ec2 describe-security-groups --filters Name=group-name,Values=$NAME Name=vpc-id,Values=$VPC_ID \
    --query 'SecurityGroups[0].GroupId' --output text --region $REGION 2>/dev/null)
  if [[ -z "$SG_ID" || "$SG_ID" == "None" ]]; then
    SG_ID=$(aws ec2 create-security-group --group-name $NAME --description "$DESC" --vpc-id $VPC_ID --query 'GroupId' --output text --region $REGION)
  fi
  echo $SG_ID
}

SG_ALB=$(create_sg "${PROJECT}-alb-sg" "ALB — public HTTP/HTTPS")
SG_API=$(create_sg "${PROJECT}-api-sg" "FastAPI — from ALB only")
SG_EVOLUTION=$(create_sg "${PROJECT}-evolution-sg" "EvolutionAPI — from ALB only")
SG_LAMBDA=$(create_sg "${PROJECT}-lambda-sg" "Lambda — outbound only")

# ALB: inbound 80 from anywhere
aws ec2 authorize-security-group-ingress --group-id $SG_ALB --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $REGION 2>/dev/null || true
# API: inbound 8000 from ALB
aws ec2 authorize-security-group-ingress --group-id $SG_API --protocol tcp --port 8000 --source-group $SG_ALB --region $REGION 2>/dev/null || true
# Evolution: inbound 8080 from ALB
aws ec2 authorize-security-group-ingress --group-id $SG_EVOLUTION --protocol tcp --port 8080 --source-group $SG_ALB --region $REGION 2>/dev/null || true

log "Security groups: ALB=$SG_ALB, API=$SG_API, Evolution=$SG_EVOLUTION, Lambda=$SG_LAMBDA"

# ── Step 5: ALB + Target Groups ────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Step 5: ALB + Target Groups"
echo "═══════════════════════════════════════════════════"

# Target groups (IP type for Fargate awsvpc)
API_TG=$(aws elbv2 describe-target-groups --names ${PROJECT}-api-tg --query 'TargetGroups[0].TargetGroupArn' --output text --region $REGION 2>/dev/null || echo "None")
if [[ "$API_TG" == "None" || -z "$API_TG" ]]; then
  API_TG=$(aws elbv2 create-target-group --name ${PROJECT}-api-tg --protocol HTTP --port 8000 \
    --vpc-id $VPC_ID --target-type ip --health-check-path /docs \
    --query 'TargetGroups[0].TargetGroupArn' --output text --region $REGION)
fi
log "Target group: API → $API_TG"

EVOLUTION_TG=$(aws elbv2 describe-target-groups --names ${PROJECT}-evolution-tg --query 'TargetGroups[0].TargetGroupArn' --output text --region $REGION 2>/dev/null || echo "None")
if [[ "$EVOLUTION_TG" == "None" || -z "$EVOLUTION_TG" ]]; then
  EVOLUTION_TG=$(aws elbv2 create-target-group --name ${PROJECT}-evolution-tg --protocol HTTP --port 8080 \
    --vpc-id $VPC_ID --target-type ip --health-check-path / \
    --query 'TargetGroups[0].TargetGroupArn' --output text --region $REGION)
fi
log "Target group: Evolution → $EVOLUTION_TG"

# ALB
ALB_ARN=$(aws elbv2 describe-load-balancers --names ${PROJECT}-alb --query 'LoadBalancers[0].LoadBalancerArn' --output text --region $REGION 2>/dev/null || echo "None")
if [[ "$ALB_ARN" == "None" || -z "$ALB_ARN" ]]; then
  ALB_ARN=$(aws elbv2 create-load-balancer --name ${PROJECT}-alb --subnets ${SUBNETS//,/ } \
    --security-groups $SG_ALB --scheme internet-facing --type application \
    --query 'LoadBalancers[0].LoadBalancerArn' --output text --region $REGION)
fi
ALB_DNS=$(aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --query 'LoadBalancers[0].DNSName' --output text --region $REGION)
log "ALB: $ALB_DNS"

# Listener: port 80, default → API
LISTENER_ARN=$(aws elbv2 describe-listeners --load-balancer-arn $ALB_ARN --query 'Listeners[0].ListenerArn' --output text --region $REGION 2>/dev/null || echo "None")
if [[ "$LISTENER_ARN" == "None" || -z "$LISTENER_ARN" ]]; then
  LISTENER_ARN=$(aws elbv2 create-listener --load-balancer-arn $ALB_ARN --protocol HTTP --port 80 \
    --default-actions Type=forward,TargetGroupArn=$API_TG \
    --query 'Listeners[0].ListenerArn' --output text --region $REGION)
fi
log "Listener: port 80 → API (default)"

# ── Step 6: ECS Cluster + Task Definitions ──────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Step 6: ECS Cluster + Task Definitions"
echo "═══════════════════════════════════════════════════"

aws ecs describe-clusters --clusters $CLUSTER --query 'clusters[?status==`ACTIVE`].clusterName' --output text --region $REGION 2>/dev/null | grep -q $CLUSTER \
  || aws ecs create-cluster --cluster-name $CLUSTER --region $REGION
log "ECS cluster: $CLUSTER"

# Create execution role if needed
EXEC_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${PROJECT}-ecs-exec-role"
if ! aws iam get-role --role-name ${PROJECT}-ecs-exec-role 2>/dev/null; then
  aws iam create-role --role-name ${PROJECT}-ecs-exec-role \
    --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
  aws iam attach-role-policy --role-name ${PROJECT}-ecs-exec-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
  log "Created ECS execution role"
else
  log "ECS execution role exists"
fi

# Task definition: FastAPI
cat > /tmp/api-task-def.json <<TASKEOF
{
  "family": "${PROJECT}-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "${EXEC_ROLE_ARN}",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "${ECR_API}:latest",
      "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "DATABASE_URL", "value": "REPLACE_WITH_RDS_URL"},
        {"name": "EVOLUTIONAPI_URL", "value": "http://REPLACE_WITH_EVOLUTION_IP:8080"},
        {"name": "STEP_FUNCTIONS_ARN", "value": "REPLACE_AFTER_SFN_CREATED"},
        {"name": "S3_BUCKET", "value": "${S3_BUCKET}"},
        {"name": "AWS_DEFAULT_REGION", "value": "${REGION}"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/${PROJECT}-api",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      }
    }
  ]
}
TASKEOF

aws ecs register-task-definition --cli-input-json file:///tmp/api-task-def.json --region $REGION > /dev/null
log "Task definition: ${PROJECT}-api"

# Task definition: EvolutionAPI
cat > /tmp/evolution-task-def.json <<TASKEOF
{
  "family": "${PROJECT}-evolution",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "${EXEC_ROLE_ARN}",
  "containerDefinitions": [
    {
      "name": "evolution",
      "image": "${ECR_EVOLUTION}:latest",
      "portMappings": [{"containerPort": 8080, "protocol": "tcp"}],
      "environment": [
        {"name": "AUTHENTICATION_API_KEY", "value": "REPLACE_WITH_EVOLUTION_KEY"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/${PROJECT}-evolution",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      }
    }
  ]
}
TASKEOF

aws ecs register-task-definition --cli-input-json file:///tmp/evolution-task-def.json --region $REGION > /dev/null
log "Task definition: ${PROJECT}-evolution"

# ── Step 7: ECS Services ───────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Step 7: ECS Services"
echo "═══════════════════════════════════════════════════"

FIRST_SUBNET=$(echo $SUBNETS | cut -d',' -f1)

aws ecs describe-services --cluster $CLUSTER --services $API_SERVICE --query 'services[?status==`ACTIVE`].serviceName' --output text --region $REGION 2>/dev/null | grep -q $API_SERVICE \
  || aws ecs create-service --cluster $CLUSTER --service-name $API_SERVICE \
    --task-definition ${PROJECT}-api --desired-count 1 --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$FIRST_SUBNET],securityGroups=[$SG_API],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$API_TG,containerName=api,containerPort=8000" \
    --region $REGION > /dev/null
log "ECS service: $API_SERVICE"

aws ecs describe-services --cluster $CLUSTER --services $EVOLUTION_SERVICE --query 'services[?status==`ACTIVE`].serviceName' --output text --region $REGION 2>/dev/null | grep -q $EVOLUTION_SERVICE \
  || aws ecs create-service --cluster $CLUSTER --service-name $EVOLUTION_SERVICE \
    --task-definition ${PROJECT}-evolution --desired-count 1 --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$FIRST_SUBNET],securityGroups=[$SG_EVOLUTION],assignPublicIp=ENABLED}" \
    --region $REGION > /dev/null
log "ECS service: $EVOLUTION_SERVICE"

# ── Step 8: Lambda Layers + Pipeline Functions + Step Functions ────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Step 8: Lambda Layers + Pipeline Functions"
echo "═══════════════════════════════════════════════════"

# Lambda execution role
if ! aws iam get-role --role-name ${PROJECT}-lambda-role 2>/dev/null; then
  aws iam create-role --role-name ${PROJECT}-lambda-role \
    --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
  aws iam attach-role-policy --role-name ${PROJECT}-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
  aws iam attach-role-policy --role-name ${PROJECT}-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
  # Lambda also needs S3 read access (for ML model download)
  aws iam put-role-policy --role-name ${PROJECT}-lambda-role --policy-name s3-read \
    --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"s3:GetObject\"],\"Resource\":\"arn:aws:s3:::${S3_BUCKET}/*\"}]}"
  sleep 10  # Wait for role propagation
  log "Created Lambda execution role"
else
  log "Lambda execution role exists"
fi
LAMBDA_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${PROJECT}-lambda-role"

# Load env vars from .env for Lambda configuration
if [[ -f .env ]]; then
  export $(grep -v '^#' .env | grep -v '^\s*$' | xargs)
fi

# Shared env vars for all Lambdas (Settings uses extra="ignore")
LAMBDA_ENV_VARS="DATABASE_URL=${DATABASE_URL:-},ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-},SENTINEL_HUB_ID=${SENTINEL_HUB_ID:-},SENTINEL_HUB_SECRET=${SENTINEL_HUB_SECRET:-},INEGI_TOKEN=${INEGI_TOKEN:-},GROQ_API_KEY=${GROQ_API_KEY:-},OPENAI_API_KEY=${OPENAI_API_KEY:-},S3_BUCKET=${S3_BUCKET},EVOLUTIONAPI_URL=${EVOLUTIONAPI_URL:-http://localhost:8080},EVOLUTIONAPI_AUTHENTICATION_API_KEY=${EVOLUTIONAPI_AUTHENTICATION_API_KEY:-},EVOLUTION_INSTANCE_NAME=${EVOLUTION_INSTANCE_NAME:-Fintegra solutions}"

# Package Lambda functions
log "Packaging Lambda functions..."
bash scripts/package_lambda.sh all

# ── Lambda Layers ──

# Common deps layer
COMMON_LAYER_ARN=$(aws lambda publish-layer-version \
  --layer-name ${PROJECT}-common-deps \
  --compatible-runtimes python3.12 \
  --zip-file fileb:///tmp/lambda-layers/common-deps.zip \
  --query 'LayerVersionArn' --output text --region $REGION)
log "Layer: common-deps → $COMMON_LAYER_ARN"

# Science deps layer
SCIENCE_LAYER_ARN=$(aws lambda publish-layer-version \
  --layer-name ${PROJECT}-science-deps \
  --compatible-runtimes python3.12 \
  --zip-file fileb:///tmp/lambda-layers/science-deps.zip \
  --query 'LayerVersionArn' --output text --region $REGION)
log "Layer: science-deps → $SCIENCE_LAYER_ARN"

# ── Deploy 6 Lambda Functions ──

# Handler config: name:memory:timeout:layers
LAMBDA_CONFIGS=(
  "extract-docs:extract_docs:256:60:common"
  "fetch-satellite:fetch_satellite:512:90:both"
  "fetch-climate:fetch_climate:256:60:common"
  "fetch-socioeconomic:fetch_socioeconomic:256:60:common"
  "calculate-score:calculate_score:512:30:both"
  "generate-expediente:generate_expediente:256:60:common"
)

declare -A LAMBDA_ARNS

for config in "${LAMBDA_CONFIGS[@]}"; do
  IFS=':' read -r fname handler_file memory timeout layer_type <<< "$config"
  func_name="${PROJECT}-${fname}"

  # Determine layers
  if [[ "$layer_type" == "both" ]]; then
    LAYERS="${COMMON_LAYER_ARN},${SCIENCE_LAYER_ARN}"
  else
    LAYERS="${COMMON_LAYER_ARN}"
  fi

  EXISTING_ARN=$(aws lambda get-function --function-name $func_name --query 'Configuration.FunctionArn' --output text --region $REGION 2>/dev/null || echo "None")

  if [[ "$EXISTING_ARN" == "None" || -z "$EXISTING_ARN" ]]; then
    FUNC_ARN=$(aws lambda create-function --function-name $func_name \
      --runtime python3.12 --handler handler.handler \
      --role $LAMBDA_ROLE_ARN \
      --zip-file fileb:///tmp/lambda-packages/${handler_file}.zip \
      --timeout $timeout --memory-size $memory \
      --layers $LAYERS \
      --environment "Variables={${LAMBDA_ENV_VARS}}" \
      --query 'FunctionArn' --output text --region $REGION)
  else
    aws lambda update-function-code --function-name $func_name \
      --zip-file fileb:///tmp/lambda-packages/${handler_file}.zip --region $REGION > /dev/null
    # Wait for code update before changing config
    aws lambda wait function-updated --function-name $func_name --region $REGION 2>/dev/null || sleep 5
    aws lambda update-function-configuration --function-name $func_name \
      --layers $LAYERS \
      --timeout $timeout --memory-size $memory \
      --environment "Variables={${LAMBDA_ENV_VARS}}" --region $REGION > /dev/null
    FUNC_ARN="$EXISTING_ARN"
  fi

  LAMBDA_ARNS[$fname]="$FUNC_ARN"
  log "Lambda: $func_name → $FUNC_ARN"
done

# ── Step Functions ──

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Step Functions State Machine"
echo "═══════════════════════════════════════════════════"

SFN_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${PROJECT}-sfn-role"

# Build resource ARN list for IAM policy
ALL_LAMBDA_ARNS=""
for arn in "${LAMBDA_ARNS[@]}"; do
  ALL_LAMBDA_ARNS="${ALL_LAMBDA_ARNS}\"${arn}\","
done
ALL_LAMBDA_ARNS="[${ALL_LAMBDA_ARNS%,}]"

if ! aws iam get-role --role-name ${PROJECT}-sfn-role 2>/dev/null; then
  aws iam create-role --role-name ${PROJECT}-sfn-role \
    --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"states.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
  sleep 5
  log "Created Step Functions role"
fi
# Update policy to allow invoking all 6 Lambdas
aws iam put-role-policy --role-name ${PROJECT}-sfn-role --policy-name invoke-lambda \
  --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"lambda:InvokeFunction\",\"Resource\":${ALL_LAMBDA_ARNS}}]}"
log "Updated Step Functions IAM policy for 6 Lambdas"

# Replace 6 ARN placeholders in state machine definition
SFN_DEFINITION=$(cat infra/step-functions.json)
SFN_DEFINITION=$(echo "$SFN_DEFINITION" | sed "s|\${ExtractDocsLambdaArn}|${LAMBDA_ARNS[extract-docs]}|g")
SFN_DEFINITION=$(echo "$SFN_DEFINITION" | sed "s|\${FetchSatelliteLambdaArn}|${LAMBDA_ARNS[fetch-satellite]}|g")
SFN_DEFINITION=$(echo "$SFN_DEFINITION" | sed "s|\${FetchClimateLambdaArn}|${LAMBDA_ARNS[fetch-climate]}|g")
SFN_DEFINITION=$(echo "$SFN_DEFINITION" | sed "s|\${FetchSocioeconomicLambdaArn}|${LAMBDA_ARNS[fetch-socioeconomic]}|g")
SFN_DEFINITION=$(echo "$SFN_DEFINITION" | sed "s|\${CalculateScoreLambdaArn}|${LAMBDA_ARNS[calculate-score]}|g")
SFN_DEFINITION=$(echo "$SFN_DEFINITION" | sed "s|\${GenerateExpedienteLambdaArn}|${LAMBDA_ARNS[generate-expediente]}|g")

SFN_ARN=$(aws stepfunctions list-state-machines --query "stateMachines[?name=='${PROJECT}-pipeline'].stateMachineArn | [0]" --output text --region $REGION 2>/dev/null)
if [[ -z "$SFN_ARN" || "$SFN_ARN" == "None" ]]; then
  SFN_ARN=$(aws stepfunctions create-state-machine --name ${PROJECT}-pipeline \
    --definition "$SFN_DEFINITION" --role-arn $SFN_ROLE_ARN \
    --query 'stateMachineArn' --output text --region $REGION)
else
  aws stepfunctions update-state-machine --state-machine-arn $SFN_ARN \
    --definition "$SFN_DEFINITION" --region $REGION > /dev/null
fi
log "Step Functions: $SFN_ARN"

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  Deploy Complete"
echo "═══════════════════════════════════════════════════"
echo ""
echo "ALB URL:          http://${ALB_DNS}"
echo "Step Functions:   ${SFN_ARN}"
echo "S3 Bucket:        ${S3_BUCKET}"
echo ""
echo "Lambda Functions:"
for fname in "${!LAMBDA_ARNS[@]}"; do
  echo "  ${fname}: ${LAMBDA_ARNS[$fname]}"
done
echo ""
echo "Lambda Layers:"
echo "  common-deps: ${COMMON_LAYER_ARN}"
echo "  science-deps: ${SCIENCE_LAYER_ARN}"
echo ""
echo "Next steps:"
echo "  1. Create RDS instance (if not done):"
echo "     aws rds create-db-instance --db-instance-identifier ${PROJECT}-db \\"
echo "       --db-instance-class db.t4g.micro --engine postgres --engine-version 16 \\"
echo "       --master-username agriscore --master-user-password CHANGE_ME \\"
echo "       --allocated-storage 20 --vpc-security-group-ids SG_RDS_ID \\"
echo "       --region ${REGION}"
echo ""
echo "  2. Update task definition with real DATABASE_URL and STEP_FUNCTIONS_ARN:"
echo "     STEP_FUNCTIONS_ARN=${SFN_ARN}"
echo ""
echo "  3. Update ECS services to pick up new task definitions:"
echo "     aws ecs update-service --cluster ${CLUSTER} --service ${API_SERVICE} --force-new-deployment --region ${REGION}"
echo ""
echo "  4. Connect WhatsApp: scan QR code from EvolutionAPI"
echo ""
echo "  5. Teardown after event:"
echo "     ./scripts/deploy_aws.sh teardown"
