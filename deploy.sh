#!/usr/bin/env bash
# Déploie la custom_components/proxmoxve locale vers HA dev et redémarre.
set -euo pipefail

DOMAIN="proxmoxve"
SRC="$(dirname "$0")/custom_components/$DOMAIN"
HA_CUSTOM="/home/stephane/homeassistant/config/custom_components/$DOMAIN"

echo "=== Deploy [$DOMAIN] ==="
docker exec homeassistant rm -rf "$HA_CUSTOM"
mkdir -p "$HA_CUSTOM"
rsync -a --exclude='__pycache__' "$SRC/" "$HA_CUSTOM/"

echo "=== check_config ==="
docker exec homeassistant python -m homeassistant --script check_config --config /config 2>&1 | tail -5

echo "=== restart ==="
docker restart homeassistant >/dev/null
echo "Attente du démarrage…"
sleep 25

echo "=== logs [$DOMAIN] 40s ==="
docker logs homeassistant --since 40s 2>&1 | grep -iE "proxmox.*(error|traceback|exception)|ERROR.*proxmox" | head -20 || true

ERRORS=$(docker logs homeassistant --since 40s 2>&1 | grep -icE "ERROR.*$DOMAIN|$DOMAIN.*ERROR|Traceback.*$DOMAIN" || true)
if [ "$ERRORS" -gt 0 ]; then
    echo "❌ $ERRORS erreurs détectées — STOP"
    exit 1
fi
echo "✅ Deploy OK, 0 erreur"
