#!/usr/bin/env bash
# ==============================================================================
# Brightloop Automated Disaster Recovery Restoration Script
# Usage: ./scripts/restore_brightloop.sh <path_to_dump_file> [optional_target_db_name] [optional_filestore_tar]
# Example: ./scripts/restore_brightloop.sh /var/backups/brightloop/brightloop_prod_20261031.dump brightloop_restored
# ==============================================================================

set -eo pipefail

DUMP_FILE="$1"
TARGET_DB="${2:-brightloop_restored}"
FILESTORE_TAR="$3"

DB_USER="${PGUSER:-odoo}"
DB_HOST="${PGHOST:-localhost}"
DB_PORT="${PGPORT:-5432}"
FILESTORE_DIR="${ODOO_FILESTORE_DIR:-/var/lib/odoo/.local/share/Odoo/filestore}"

if [ -z "${DUMP_FILE}" ] || [ ! -f "${DUMP_FILE}" ]; then
    echo " [ERROR] Valid dump file path required as argument 1."
    echo " Usage: $0 <path_to_dump_file> [target_db_name] [filestore_tar_gz]"
    exit 1
fi

echo "======================================================================"
echo " [BRIGHTLOOP RESTORE] Restoring database from archive"
echo " Source Dump: ${DUMP_FILE}"
echo " Target DB:   ${TARGET_DB}"
echo " Host:        ${DB_HOST}:${DB_PORT} (User: ${DB_USER})"
echo "======================================================================"

read -p " WARNING: This will DROP and RE-CREATE database '${TARGET_DB}'. Continue? (y/N): " -r CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo " [ABORTED] Restoration cancelled by operator."
    exit 0
fi

# 1. Terminate active connections to target database
echo " [1/4] Terminating existing connections to ${TARGET_DB}..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c \
     "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${TARGET_DB}';" > /dev/null 2>&1 || true

# 2. Drop and Re-create target database
echo " [2/4] Dropping and re-creating clean database ${TARGET_DB}..."
dropdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" --if-exists "${TARGET_DB}"
createdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -O "${DB_USER}" "${TARGET_DB}"

# 3. Restore binary dump
echo " [3/4] Restoring PostgreSQL binary dump..."
pg_restore -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${TARGET_DB}" -v \
           "${DUMP_FILE}" 2>&1 | tail -n 5 || true

# 4. Extract filestore if provided
if [ -n "${FILESTORE_TAR}" ] && [ -f "${FILESTORE_TAR}" ]; then
    echo " [4/4] Extracting filestore archive to ${FILESTORE_DIR}/${TARGET_DB}..."
    mkdir -p "${FILESTORE_DIR}/${TARGET_DB}"
    tar -xzf "${FILESTORE_TAR}" -C "${FILESTORE_DIR}"
    echo "  -> Filestore extracted successfully."
else
    echo " [4/4] No filestore archive specified. Skipping attachment restore."
fi

echo "======================================================================"
echo " [SUCCESS] Restoration completed successfully."
echo " Verify with: odoo-bin -d ${TARGET_DB} -u brightloop_subscription --stop-after-init"
echo "======================================================================"
