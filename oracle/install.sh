#!/usr/bin/env bash
set -euo pipefail

# Run this on the SLES VM as root to install L'Oracle de Geeko as a systemd service.
# Usage: ./install.sh

INSTALL_DIR=/opt/geeko-oracle

zypper --non-interactive install -y python312 python312-pip

mkdir -p "$INSTALL_DIR"
cp -r oracle_service requirements.txt "$INSTALL_DIR/"

python3.12 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --no-cache-dir -r "$INSTALL_DIR/requirements.txt"

install -m 644 geeko-oracle.service /etc/systemd/system/geeko-oracle.service
systemctl daemon-reload
systemctl enable --now geeko-oracle

echo "L'Oracle de Geeko est démarré. Vérification :"
curl -sf http://localhost:9000/healthz && echo
