#!/usr/bin/env bash
set -euo pipefail

#######################################################################
# Milvus Standalone Enhanced Launcher (Based on official script)
#
# Features:
#
# 1. Full compatibility with the official Milvus standalone_embed.sh
#    - Uses embedded Etcd + standalone Milvus mode
#    - Preserves official config/user.yaml behavior
#
# 2. Automatic Python environment check and pymilvus validation
#    - Ensures RAG clients (LlamaIndex, LangChain, DSPy, custom SDKs)
#      can connect to Milvus after startup
#
# 3. Python dependency installation with uv-first fallback strategy
#    - If uv is available → use `uv pip install <package>`
#    - Otherwise fall back to `pip install <package>`
#    - Ideal for modern Python projects using uv environments
#
# 4. Automatic creation and mounting of local Milvus volume directories
#    - Defaults to ./volumes/milvus (overridable via environment variables)
#
# 5. Automatic pulling and running of Milvus Standalone Docker container
#    - Embedded Etcd configuration is injected automatically
#    - StorageType=local for lightweight local development workflows
#    - Ports and image versions can be overridden via env vars
#
# 6. Two-layer health checking (stronger than the official script)
#    (a) Docker-level health check via /healthz endpoint
#    (b) Python-level health check using pymilvus:
#        - Attempts RPC connection
#        - Calls list_collections()
#        - Ensures the Milvus service is ready for RAG workloads
#
# 7. Fully RAG-ready:
#    - Ensures RPC readiness before returning success
#    - Works seamlessly with LlamaIndex, LangChain, DSPy, etc.
#
# 8. Preserves official lifecycle commands
#    - start / stop / restart / delete / upgrade remain supported
#
# Suitable for:
#    - Local RAG development and testing
#    - Lightweight standalone Milvus setups
#    - uv-managed Python environments
#    - Projects needing reliable SDK-level readiness checks
#
#######################################################################

# Licensed to the LF AI & Data foundation under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

############################################
# Config (can be overridden via env vars)
############################################

MILVUS_IMAGE="${MILVUS_IMAGE:-milvusdb/milvus:v2.6.7}"
MILVUS_CONTAINER_NAME="${MILVUS_CONTAINER_NAME:-milvus-standalone}"
MILVUS_VOLUME_DIR="${MILVUS_VOLUME_DIR:-$(pwd)/volumes/milvus}"

MILVUS_PORT="${MILVUS_PORT:-19530}"       # Milvus RPC
MILVUS_HTTP_PORT="${MILVUS_HTTP_PORT:-9091}" # HTTP /healthz
ETCD_PORT="${ETCD_PORT:-2379}"

############################################
# Helper: basic environment checks
############################################

check_virtual_env() {
  if [[ -z "${VIRTUAL_ENV:-}" && -z "${CONDA_PREFIX:-}" ]]; then
    echo "WARNING: You are not inside a Python virtual environment (venv/conda)."
    echo "         It is recommended to use a virtual environment for RAG clients."
  else
    echo "Virtual environment detected."
  fi
}

ensure_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: docker command not found. Please install Docker first."
    exit 1
  fi
}

ensure_python3() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "WARNING: python3 is not available on PATH."
    echo "         Milvus container will still start, but Python SDK health check will be skipped."
    return 1
  fi
  return 0
}

############################################
# Helper: install Python packages (uv → pip)
############################################

install_python_pkg() {
  local package="$1"

  echo "Installing Python package: ${package} (uv-first, pip fallback)..."

  if command -v uv >/dev/null 2>&1; then
    echo "Using: uv pip install ${package}"
    if uv pip install "${package}"; then
      return 0
    else
      echo "uv pip install failed, falling back to pip..."
    fi
  fi

  if command -v pip >/dev/null 2>&1; then
    echo "Using: pip install ${package}"
    pip install "${package}"
    return 0
  else
    echo "ERROR: Neither uv nor pip is available to install ${package}."
    return 1
  fi
}

ensure_pymilvus() {
  if ! ensure_python3; then
    echo "Skipping pymilvus installation because python3 is not available."
    return
  fi

  if python3 -c "import pymilvus" 2>/dev/null; then
    echo "pymilvus is already installed."
  else
    echo "pymilvus is not installed. Attempting to install..."
    if ! install_python_pkg "pymilvus"; then
      echo "WARNING: Failed to install pymilvus. Python-level health check will be skipped."
    fi
  fi
}

############################################
# Helper: Python-level health check
############################################

python_health_check() {
  if ! ensure_python3; then
    echo "Skipping Python-level health check: python3 not available."
    return
  fi

  if ! python3 -c "import pymilvus" 2>/dev/null; then
    echo "Skipping Python-level health check: pymilvus not available."
    return
  fi

  echo "Running Python-level health check against Milvus..."

  python3 - <<EOF
import time
from pymilvus import MilvusClient

uri = "http://localhost:${MILVUS_PORT}"

for i in range(20):
    try:
        client = MilvusClient(uri=uri)
        client.list_collections()
        print("Python-level health check passed: Milvus is ready for RAG workloads.")
        break
    except Exception as e:
        print(f"Waiting for Milvus to become ready (attempt {i + 1}/20)...")
        time.sleep(2)
else:
    raise SystemExit("Milvus did not pass Python-level health check within the timeout.")
EOF
}

############################################
# Original run_embed from official script,
# with minor enhancements & parameterization
############################################

run_embed() {
  # Write embedEtcd.yaml
  cat << EOF > embedEtcd.yaml
listen-client-urls: http://0.0.0.0:2379
advertise-client-urls: http://0.0.0.0:2379
quota-backend-bytes: 4294967296
auto-compaction-mode: revision
auto-compaction-retention: '1000'
EOF

  # Write user.yaml (can be extended by the user)
  cat << EOF > user.yaml
# Extra config to override default milvus.yaml
EOF

  if [ ! -f "./embedEtcd.yaml" ]; then
    echo "embedEtcd.yaml file does not exist. Please try to create it in the current directory."
    exit 1
  fi

  if [ ! -f "./user.yaml" ]; then
    echo "user.yaml file does not exist. Please try to create it in the current directory."
    exit 1
  fi

  # Ensure volume directory exists
  mkdir -p "${MILVUS_VOLUME_DIR}"

  echo "Starting Milvus standalone container (${MILVUS_CONTAINER_NAME}) using image ${MILVUS_IMAGE}..."

  sudo docker run -d \
    --name "${MILVUS_CONTAINER_NAME}" \
    --security-opt seccomp:unconfined \
    -e ETCD_USE_EMBED=true \
    -e ETCD_DATA_DIR=/var/lib/milvus/etcd \
    -e ETCD_CONFIG_PATH=/milvus/configs/embedEtcd.yaml \
    -e COMMON_STORAGETYPE=local \
    -e DEPLOY_MODE=STANDALONE \
    -v "${MILVUS_VOLUME_DIR}":/var/lib/milvus \
    -v "$(pwd)/embedEtcd.yaml":/milvus/configs/embedEtcd.yaml \
    -v "$(pwd)/user.yaml":/milvus/configs/user.yaml \
    -p "${MILVUS_PORT}:19530" \
    -p "${MILVUS_HTTP_PORT}:9091" \
    -p "${ETCD_PORT}:2379" \
    --health-cmd="curl -f http://localhost:9091/healthz" \
    --health-interval=30s \
    --health-start-period=90s \
    --health-timeout=20s \
    --health-retries=3 \
    "${MILVUS_IMAGE}" \
    milvus run standalone 1> /dev/null
}

wait_for_milvus_running() {
  echo "Waiting for Milvus container health (Docker-level)..."
  while true
  do
    res=$(sudo docker ps | grep "${MILVUS_CONTAINER_NAME}" | grep healthy | wc -l || true)
    if [ "${res}" -eq 1 ]; then
      echo "Milvus container is healthy."
      echo "You can add extra settings to user.yaml and restart the service if needed."
      break
    fi
    sleep 1
  done
}

############################################
# Lifecycle commands (start/stop/delete/upgrade)
############################################

start() {
  ensure_docker
  check_virtual_env
  ensure_pymilvus

  res=$(sudo docker ps | grep "${MILVUS_CONTAINER_NAME}" | grep healthy | wc -l || true)
  if [ "${res}" -eq 1 ]; then
    echo "Milvus is already running."
    exit 0
  fi

  res=$(sudo docker ps -a | grep "${MILVUS_CONTAINER_NAME}" | wc -l || true)
  if [ "${res}" -eq 1 ]; then
    echo "Starting existing Milvus container ${MILVUS_CONTAINER_NAME}..."
    sudo docker start "${MILVUS_CONTAINER_NAME}" 1> /dev/null
  else
    echo "No existing Milvus container found. Creating a new one..."
    run_embed
  fi

  if [ $? -ne 0 ]; then
    echo "Start failed."
    exit 1
  fi

  wait_for_milvus_running
  python_health_check

  echo "Milvus standalone is now ready on:"
  echo "  RPC   : localhost:${MILVUS_PORT}"
  echo "  HTTP  : http://localhost:${MILVUS_HTTP_PORT}/healthz"
}

stop() {
  ensure_docker
  echo "Stopping Milvus container ${MILVUS_CONTAINER_NAME}..."
  sudo docker stop "${MILVUS_CONTAINER_NAME}" 1> /dev/null || {
    echo "Stop failed."
    exit 1
  }
  echo "Stop successfully."
}

delete_container() {
  ensure_docker
  res=$(sudo docker ps | grep "${MILVUS_CONTAINER_NAME}" | wc -l || true)
  if [ "${res}" -eq 1 ]; then
    echo "Please stop Milvus service before delete."
    exit 1
  fi

  echo "Deleting Milvus container ${MILVUS_CONTAINER_NAME}..."
  sudo docker rm "${MILVUS_CONTAINER_NAME}" 1> /dev/null || {
    echo "Delete Milvus container failed."
    exit 1
  }
  echo "Delete Milvus container successfully."
}

delete_data_and_configs() {
  echo "Removing local volumes and config files..."
  rm -rf "$(pwd)/volumes" || true
  rm -rf "$(pwd)/embedEtcd.yaml" || true
  rm -rf "$(pwd)/user.yaml" || true
}

delete() {
  read -p "This operation will delete the container and data. Confirm with 'y' for yes or 'n' for no. > " check
  if [ "${check}" = "y" ] || [ "${check}" = "Y" ]; then
    delete_container
    delete_data_and_configs
    echo "Delete successfully."
  else
    echo "Exit delete."
    exit 0
  fi
}

upgrade() {
  read -p "This will upgrade using the latest official script. Confirm with 'y' for yes or 'n' for no. > " check
  if [ "${check}" = "y" ] || [ "${check}" = "Y" ]; then
    res=$(sudo docker ps -a | grep "${MILVUS_CONTAINER_NAME}" | wc -l || true)
    if [ "${res}" -eq 1 ]; then
      stop
      delete_container
    fi
    curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed_latest.sh && \
      bash standalone_embed_latest.sh start 1> /dev/null && \
      echo "Upgrade successfully (using official script)."
  else
    echo "Exit upgrade."
    exit 0
  fi
}

############################################
# CLI entrypoint
############################################

if [ $# -lt 1 ]; then
  echo "Usage: bash $0 {start|stop|restart|upgrade|delete}"
  exit 1
fi

case "$1" in
  restart)
    stop
    start
    ;;
  start)
    start
    ;;
  stop)
    stop
    ;;
  upgrade)
    upgrade
    ;;
  delete)
    delete
    ;;
  *)
    echo "Usage: bash $0 {start|stop|restart|upgrade|delete}"
    exit 1
    ;;
esac
