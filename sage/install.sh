#!/usr/bin/env bash
set -euo pipefail

# Run this on the SLES VM as root to install Le Sage de Geeko as a systemd service.
# Usage: ./install.sh

INSTALL_DIR=/opt/geeko-sage

mkdir -p "$INSTALL_DIR"
cp -r sage_service requirements.txt "$INSTALL_DIR/"

python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --no-cache-dir -r "$INSTALL_DIR/requirements.txt"

install -m 644 geeko-sage.service /etc/systemd/system/geeko-sage.service
systemctl daemon-reload
systemctl enable --now geeko-sage

echo "Le Sage de Geeko est démarré. Vérification :"
curl -sf http://localhost:9000/healthz && echo
