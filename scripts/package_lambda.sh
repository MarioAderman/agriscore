#!/bin/bash
# Package individual Lambda functions for deployment.
# Usage: ./scripts/package_lambda.sh [handler_name|layers|all]
#
# Builds Lambda zips in /tmp/lambda-packages/ with the correct structure:
#   handler.py + shared/ + app/ (config + pipeline module)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="/tmp/lambda-packages"
LAYER_DIR="/tmp/lambda-layers"

# Handler definitions: name → pipeline module needed
declare -A HANDLER_PIPELINE=(
  [extract_docs]="document"
  [fetch_satellite]="satellite"
  [fetch_climate]="climate"
  [fetch_socioeconomic]="socioeconomic"
  [calculate_score]="scoring"
  [generate_expediente]=""
)

log() { echo "  → $1"; }

package_handler() {
  local name="$1"
  local pipeline_module="${HANDLER_PIPELINE[$name]}"
  local work_dir="/tmp/lambda-build-${name}"
  local zip_path="${OUT_DIR}/${name}.zip"

  echo "Packaging ${name}..."
  rm -rf "$work_dir"
  mkdir -p "$work_dir" "$OUT_DIR"

  # Handler entry point
  cp "${PROJECT_ROOT}/infra/lambda/handlers/${name}.py" "${work_dir}/handler.py"

  # Shared DB helpers
  mkdir -p "${work_dir}/shared"
  cp "${PROJECT_ROOT}/infra/lambda/shared/__init__.py" "${work_dir}/shared/"
  cp "${PROJECT_ROOT}/infra/lambda/shared/db.py" "${work_dir}/shared/"

  # App package (config + pipeline module)
  if [[ -n "$pipeline_module" ]]; then
    mkdir -p "${work_dir}/app_pkg/app/pipeline"
    cp "${PROJECT_ROOT}/app/__init__.py" "${work_dir}/app_pkg/app/" 2>/dev/null || echo "" > "${work_dir}/app_pkg/app/__init__.py"
    cp "${PROJECT_ROOT}/app/config.py" "${work_dir}/app_pkg/app/"
    cp "${PROJECT_ROOT}/app/pipeline/__init__.py" "${work_dir}/app_pkg/app/pipeline/" 2>/dev/null || echo "" > "${work_dir}/app_pkg/app/pipeline/__init__.py"
    cp "${PROJECT_ROOT}/app/pipeline/${pipeline_module}.py" "${work_dir}/app_pkg/app/pipeline/"
  fi

  # Create zip
  cd "$work_dir"
  zip -r "$zip_path" . > /dev/null
  cd "$PROJECT_ROOT"

  local size=$(du -h "$zip_path" | cut -f1)
  log "${name}.zip → ${size}"

  rm -rf "$work_dir"
}

build_layer_common() {
  echo "Building common-deps layer..."
  local work_dir="${LAYER_DIR}/common"
  rm -rf "$work_dir"
  mkdir -p "$work_dir/python" "$LAYER_DIR"

  pip install --quiet --target "$work_dir/python" \
    httpx psycopg2-binary pydantic pydantic-settings anthropic 2>/dev/null

  cd "$work_dir"
  zip -r "${LAYER_DIR}/common-deps.zip" python > /dev/null
  cd "$PROJECT_ROOT"

  local size=$(du -h "${LAYER_DIR}/common-deps.zip" | cut -f1)
  log "common-deps.zip → ${size}"
  rm -rf "$work_dir"
}

build_layer_science() {
  echo "Building science-deps layer..."
  local work_dir="${LAYER_DIR}/science"
  rm -rf "$work_dir"
  mkdir -p "$work_dir/python" "$LAYER_DIR"

  pip install --quiet --target "$work_dir/python" \
    numpy scikit-learn joblib Pillow 2>/dev/null

  cd "$work_dir"
  zip -r "${LAYER_DIR}/science-deps.zip" python > /dev/null
  cd "$PROJECT_ROOT"

  local size=$(du -h "${LAYER_DIR}/science-deps.zip" | cut -f1)
  log "science-deps.zip → ${size}"
  rm -rf "$work_dir"
}

case "${1:-all}" in
  layers)
    build_layer_common
    build_layer_science
    ;;
  all)
    build_layer_common
    build_layer_science
    for name in "${!HANDLER_PIPELINE[@]}"; do
      package_handler "$name"
    done
    echo ""
    echo "Done! Packages in ${OUT_DIR}/, layers in ${LAYER_DIR}/"
    ;;
  *)
    if [[ -n "${HANDLER_PIPELINE[$1]+x}" ]]; then
      package_handler "$1"
    else
      echo "Unknown handler: $1"
      echo "Available: ${!HANDLER_PIPELINE[*]} | layers | all"
      exit 1
    fi
    ;;
esac
