# Brightloop – Production Deployment & DevOps Engineering Guide
## Clean Installation, PostgreSQL Optimization, Docker Deployment, and Disaster Recovery
**Odoo Kochi Hackathon 2026**

---

### Table of Contents
1. [Prerequisites & System Requirements](#1-prerequisites--system-requirements)
2. [Bare-Metal / Virtual Machine Deployment](#2-bare-metal--virtual-machine-deployment)
3. [Containerized Deployment (Docker & Compose)](#3-containerized-deployment-docker--compose)
4. [PostgreSQL Tuning & Sizing](#4-postgresql-tuning--sizing)
5. [Production `odoo.conf` Optimization](#5-production-odooconf-optimization)
6. [Fresh Installation & Module Upgrade Procedures](#6-fresh-installation--module-upgrade-procedures)
7. [Backup, Archival & Disaster Recovery](#7-backup-archival--disaster-recovery)
8. [Production Deployment Verification Checklist](#8-production-deployment-verification-checklist)

---

### 1. Prerequisites & System Requirements

#### Minimum Hardware Sizing (Up to 5,000 Active Subscriptions):
- **CPU**: 4 vCPU cores (Intel Xeon or AMD EPYC).
- **RAM**: 8 GB ECC RAM (16 GB recommended for heavy BI reporting).
- **Disk Storage**: 50 GB NVMe SSD (RAID-1 mirror recommended).
- **Operating System**: Ubuntu 22.04 LTS / 24.04 LTS or Debian 12.

#### Software Dependencies:
- **Odoo Version**: Community or Enterprise 17.0 (also forward-compatible with 18.0).
- **Database**: PostgreSQL 14, 15, or 16.
- **Python**: Python 3.10, 3.11, or 3.12.
- **Reverse Proxy**: NGINX with SSL termination (Let's Encrypt / Certbot).

---

### 2. Bare-Metal / Virtual Machine Deployment

#### Step 1: Install PostgreSQL & Create Dedicated Database User
```bash
sudo apt update && sudo apt install -y postgresql postgresql-contrib
sudo -u postgres createuser --createdb --username postgres --no-createrole --no-superuser odoo
sudo -u postgres psql -c "ALTER USER odoo WITH ENCRYPTED PASSWORD 'SUPER_SECURE_PASSWORD';"
```

#### Step 2: Clone Repository into Custom Addons Directory
```bash
sudo mkdir -p /opt/odoo/custom_addons
cd /opt/odoo/custom_addons
git clone https://github.com/Mahadharani3003/Subscription_Management_System.git brightloop
sudo chown -R odoo:odoo /opt/odoo/custom_addons
```

#### Step 3: Configure `odoo.conf`
Copy the production configuration template:
```bash
sudo cp /opt/odoo/custom_addons/brightloop/config/odoo.conf.example /etc/odoo/odoo.conf
sudo chown odoo:odoo /etc/odoo/odoo.conf
sudo chmod 640 /etc/odoo/odoo.conf
```
Update `/etc/odoo/odoo.conf`:
- Set `addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom_addons/brightloop`
- Set `db_password = SUPER_SECURE_PASSWORD`
- Set `admin_passwd` using a PBKDF2 hash.

---

### 3. Containerized Deployment (Docker & Compose)

To launch Brightloop in a fully containerized, isolated stack within 60 seconds:

```bash
# Clone the repository
git clone https://github.com/Mahadharani3003/Subscription_Management_System.git
cd Subscription_Management_System

# Launch stack with persistent database volume
docker compose up -d
```

The stack automatically:
1. Spawns PostgreSQL 16 on Alpine Linux with health check validation.
2. Mounts the `brightloop_subscription` addon into Odoo 17 container.
3. Automatically creates the database `brightloop_db` and installs `brightloop_subscription`.
4. Exposes HTTP service on `http://localhost:8069`.

---

### 4. PostgreSQL Tuning & Sizing

For optimal transactional latency during batch billing cron executions, configure `/etc/postgresql/16/main/postgresql.conf`:

```ini
# Memory Configuration for 8GB RAM Server
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 32MB

# Checkpoints & WAL
min_wal_size = 1GB
max_wal_size = 4GB
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min

# Connection Pooling & Workers
max_connections = 100
random_page_cost = 1.1          # Optimized for NVMe SSD
effective_io_concurrency = 200
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

### 5. Production `odoo.conf` Optimization

#### Worker Sizing Formula:
$$\text{Workers} = (\text{CPU Cores} \times 2) + 1$$
Example for 4 Cores: `workers = 9` (8 HTTP request workers + 1 cron worker).

```ini
[options]
workers = 9
max_cron_threads = 2
limit_memory_hard = 2684354560   ; 2.5 GB
limit_memory_soft = 2147483648   ; 2.0 GB
limit_request = 8192
limit_time_cpu = 120
limit_time_real = 240
limit_time_real_cron = 600
proxy_mode = True
```

---

### 6. Fresh Installation & Module Upgrade Procedures

#### Fresh Installation via CLI:
```bash
# Initialize clean database and install Brightloop
odoo-bin -c /etc/odoo/odoo.conf -d brightloop_prod -i brightloop_subscription --stop-after-init
```

#### Safe Zero-Downtime Module Upgrade:
When updating views, models, or cron data:
```bash
# Upgrade module in target database
odoo-bin -c /etc/odoo/odoo.conf -d brightloop_prod -u brightloop_subscription --stop-after-init

# Gracefully reload Odoo workers
sudo systemctl restart odoo
```

---

### 7. Backup, Archival & Disaster Recovery

#### Automated Daily PostgreSQL Backup Script (`/usr/local/bin/backup_brightloop.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/brightloop"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATABASE="brightloop_prod"

mkdir -p $BACKUP_DIR

# 1. Dump database schema and data
pg_dump -U odoo -Fc -b -v -f "$BACKUP_DIR/${DATABASE}_${TIMESTAMP}.dump" $DATABASE

# 2. Archive Odoo filestore (attachments, icons, customer documents)
tar -czf "$BACKUP_DIR/filestore_${DATABASE}_${TIMESTAMP}.tar.gz" -C /var/lib/odoo/.local/share/Odoo/filestore $DATABASE

# 3. Rotate backups older than 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "[$(date)] Backup completed: ${DATABASE}_${TIMESTAMP}"
```

#### Database Restoration Workflow:
```bash
# 1. Terminate existing database connections
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'brightloop_prod';"

# 2. Re-create clean database
sudo -u postgres dropdb brightloop_prod
sudo -u postgres createdb -O odoo brightloop_prod

# 3. Restore binary dump
pg_restore -U odoo -d brightloop_prod -v /var/backups/brightloop/brightloop_prod_LATEST.dump

# 4. Extract filestore archive
tar -xzf /var/backups/brightloop/filestore_brightloop_prod_LATEST.tar.gz -C /var/lib/odoo/.local/share/Odoo/filestore/
```

---

### 8. Production Deployment Verification Checklist

- [x] Dedicated non-root `odoo` system user created.
- [x] PostgreSQL connection credentials secured in `odoo.conf` (permissions `640`).
- [x] All 5 automated cron jobs verified active and scheduled.
- [x] Reverse proxy (NGINX) configured with HTTP/2 and Let's Encrypt SSL.
- [x] Outgoing SMTP mail server tested and verified.
- [x] Portal self-service routes tested with unauthenticated redirect protection.
- [x] Daily automated database and filestore backup cron operational.
- [x] Multi-company record rules verified if operating multi-entity enterprise.
