#!/usr/bin/env bash
# ==============================================================================
# Brightloop Automated Backup Script
# Platform: Odoo 17 / PostgreSQL 14+
# Usage: ./scripts/backup_brightloop.sh [optional_database_name]
# Recommended Cron: 0 2 * * * /opt/odoo/custom_addons/brightloop/scripts/backup_brightloop.sh
# ==============================================================================

set -eo pipefail

DB_NAME="${1:-brightloop_prod}"
DB_USER="${PGUSER:-odoo}"
DB_HOST="${PGHOST:-localhost}"
DB_PORT="${PGPORT:-5432}"

BACKUP_DIR="${BRIGHTLOOP_BACKUP_DIR:-/var/backups/brightloop}"
FILESTORE_DIR="${ODOO_FILESTORE_DIR:-/var/lib/odoo/.local/share/Odoo/filestore}"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "======================================================================"
echo " [BRIGHTLOOP BACKUP] Initiating backup for database: ${DB_NAME}"
echo " Timestamp: ${TIMESTAMP}"
echo "======================================================================"

# 1. Create target backup directory
mkdir -p "${BACKUP_DIR}"

DB_BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump"
FILESTORE_BACKUP_FILE="${BACKUP_DIR}/filestore_${DB_NAME}_${TIMESTAMP}.tar.gz"
CHECKSUM_FILE="${BACKUP_DIR}/manifest_${TIMESTAMP}.sha256"

# 2. Dump PostgreSQL Database (Custom compressed binary format)
echo " [1/4] Dumping PostgreSQL database..."
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -Fc -b -v \
        -f "${DB_BACKUP_FILE}" "${DB_NAME}" 2>&1 | tail -n 5
echo "  -> Database dump created: ${DB_BACKUP_FILE} ($(du -h "${DB_BACKUP_FILE}" | cut -f1))"

# 3. Archive Odoo Filestore
echo " [2/4] Archiving Odoo filestore attachments..."
if [ -d "${FILESTORE_DIR}/${DB_NAME}" ]; then
    tar -czf "${FILESTORE_BACKUP_FILE}" -C "${FILESTORE_DIR}" "${DB_NAME}"
    echo "  -> Filestore archive created: ${FILESTORE_BACKUP_FILE} ($(du -h "${FILESTORE_BACKUP_FILE}" | cut -f1))"
else
    echo "  [WARN] No filestore directory found at ${FILESTORE_DIR}/${DB_NAME}. Skipping filestore tarball."
fi

# 4. Generate SHA-256 Checksums
echo " [3/4] Generating SHA-256 cryptographic verification checksums..."
cd "${BACKUP_DIR}"
sha256sum "$(basename "${DB_BACKUP_FILE}")" > "${CHECKSUM_FILE}"
if [ -f "${FILESTORE_BACKUP_FILE}" ]; then
    sha256sum "$(basename "${FILESTORE_BACKUP_FILE}")" >> "${CHECKSUM_FILE}"
fi
echo "  -> Checksum manifest written: ${CHECKSUM_FILE}"

# 5. Backup Retention Pruning (Rotate backups older than RETENTION_DAYS)
echo " [4/4] Pruning archives older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -type f -name "${DB_NAME}_*.dump" -mtime "+${RETENTION_DAYS}" -delete
find "${BACKUP_DIR}" -type f -name "filestore_${DB_NAME}_*.tar.gz" -mtime "+${RETENTION_DAYS}" -delete
find "${BACKUP_DIR}" -type f -name "manifest_*.sha256" -mtime "+${RETENTION_DAYS}" -delete

echo "======================================================================"
echo " [SUCCESS] Backup completed successfully."
echo " Location: ${BACKUP_DIR}"
echo "======================================================================"
