#!/usr/bin/env bash
# Restaura un respaldo en una base nueva y compara conteos con la original (GA10-AA9).
# Uso: ./restaurar.sh respaldos/siae_dev_AAAAMMDD_HHMMSS.dump siae_restaurada [siae_dev]
set -euo pipefail
ARCHIVO="$1"; NUEVA="$2"; ORIGEN="${3:-}"
shasum -a 256 -c "$ARCHIVO.sha256"
dropdb --if-exists "$NUEVA" 2>/dev/null; createdb "$NUEVA"
pg_restore -d "$NUEVA" "$ARCHIVO"
CONTEO="SELECT 'usuarios='||(SELECT count(*) FROM usuario)||' tablas='||(SELECT count(*) FROM tabla_transformada)||' registros='||(SELECT count(*) FROM registro_venta)"
echo "Restaurada: $(psql -d "$NUEVA" -At -c "$CONTEO")"
if [ -n "$ORIGEN" ]; then echo "Origen:     $(psql -d "$ORIGEN" -At -c "$CONTEO")"; fi
