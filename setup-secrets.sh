#!/usr/bin/env bash
# Bootstrap secrets for the api-smoke-tests CronJob namespace.
#
# Run this once after ArgoCD has created the namespace (or run with --create-namespace
# to create it yourself before ArgoCD syncs).
#
# Required for image pulls (always):
#   - ghcr-secret        copied from an existing namespace
#
# Optional — tests skip automatically when these are absent:
#   - grafana-smoke-secret   needs GRAFANA_API_KEY env var
#   - minio-smoke-secret     needs MINIO_ACCESS_KEY + MINIO_SECRET_KEY env vars
#
# Usage:
#   ./setup-secrets.sh [--create-namespace] [--source-ns <ns>]

set -euo pipefail

NAMESPACE="api-smoke-tests"
SOURCE_NS="cluster-ops-agent"   # any namespace that already has ghcr-secret

# --- parse flags ---
CREATE_NS=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --create-namespace) CREATE_NS=true; shift ;;
    --source-ns) SOURCE_NS="$2"; shift 2 ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

# --- namespace ---
if $CREATE_NS; then
  kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
else
  if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
    echo "Namespace '$NAMESPACE' does not exist yet."
    echo "Wait for ArgoCD to create it, or re-run with --create-namespace."
    exit 1
  fi
fi

echo "Namespace: $NAMESPACE"

# --- ghcr-secret (copy from source namespace) ---
echo ""
echo "Copying ghcr-secret from namespace '$SOURCE_NS'..."
kubectl get secret ghcr-secret -n "$SOURCE_NS" -o json \
  | python3 -c "
import sys, json
s = json.load(sys.stdin)
s['metadata'].pop('creationTimestamp', None)
s['metadata'].pop('resourceVersion', None)
s['metadata'].pop('uid', None)
s['metadata'].pop('annotations', None)
s['metadata']['namespace'] = '$NAMESPACE'
print(json.dumps(s))
" | kubectl apply -f -
echo "ghcr-secret applied."

# --- grafana-smoke-secret (optional) ---
echo ""
if [[ -n "${GRAFANA_API_KEY:-}" ]]; then
  kubectl create secret generic grafana-smoke-secret \
    --namespace "$NAMESPACE" \
    --from-literal=GRAFANA_API_KEY="$GRAFANA_API_KEY" \
    --dry-run=client -o yaml | kubectl apply -f -
  echo "grafana-smoke-secret applied."
else
  echo "GRAFANA_API_KEY not set — skipping grafana-smoke-secret."
  echo "  To add later: GRAFANA_API_KEY=<key> ./setup-secrets.sh"
fi

# --- minio-smoke-secret (optional) ---
echo ""
if [[ -n "${MINIO_ACCESS_KEY:-}" && -n "${MINIO_SECRET_KEY:-}" ]]; then
  kubectl create secret generic minio-smoke-secret \
    --namespace "$NAMESPACE" \
    --from-literal=MINIO_ACCESS_KEY="$MINIO_ACCESS_KEY" \
    --from-literal=MINIO_SECRET_KEY="$MINIO_SECRET_KEY" \
    --dry-run=client -o yaml | kubectl apply -f -
  echo "minio-smoke-secret applied."
else
  echo "MINIO_ACCESS_KEY / MINIO_SECRET_KEY not set — skipping minio-smoke-secret."
  echo "  To add later: MINIO_ACCESS_KEY=<key> MINIO_SECRET_KEY=<secret> ./setup-secrets.sh"
fi

echo ""
echo "Done. Verify with:"
echo "  kubectl get secrets -n $NAMESPACE"
