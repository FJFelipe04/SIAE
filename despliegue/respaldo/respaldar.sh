#!/usr/bin/env bash
# Respaldo diario de la base de datos SIAE con retención (GA10-AA9).
# Variables: PGHOST, PGPORT, PGUSER (estándar de PostgreSQL), BD (siae_dev), DESTINO (./respaldos), DIAS (7)
set -euo pipefail
BD="${BD:-siae_dev}"; DESTINO="${DESTINO:-./respaldos}"; DIAS="${DIAS:-7}"
mkdir -p "$DESTINO"
ARCHIVO="$DESTINO/${BD}_$(date +%Y%m%d_%H%M%S).dump"
pg_dump -d "$BD" -F c -f "$ARCHIVO"
shasum -a 256 "$ARCHIVO" > "$ARCHIVO.sha256"
pg_restore --list "$ARCHIVO" > /dev/null   # el archivo se puede leer
find "$DESTINO" -name "${BD}_*.dump*" -mtime +"$DIAS" -delete
echo "Respaldo OK: $ARCHIVO ($(du -h "$ARCHIVO" | cut -f1))"
