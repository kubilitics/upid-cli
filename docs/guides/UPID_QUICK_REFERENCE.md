# UPID CLI Quick Reference

## Authentication
```bash
# Login
upid auth login

# Logout
upid auth logout

# Check status
upid auth status
```

## Analysis Commands
```bash
# Quick cluster analysis
upid analyze cluster

# Detailed analysis
upid analyze detailed --time-range 24h

# Pod analysis
upid analyze pod <pod-name> --namespace <namespace>

# Resource analysis
upid analyze cpu --time-range 7d
upid analyze memory --time-range 7d
```

## Optimization
```bash
# Get recommendations
upid optimize resources

# Apply optimization
upid optimize apply --recommendation-id <id>

# Cost optimization
upid optimize cost --time-range 30d
```

## Reporting
```bash
# Executive report
upid report executive --time-range 7d

# Technical report
upid report technical --time-range 24h

# Export report
upid report export --format pdf --output report.pdf
```

## Dashboard
```bash
# Launch dashboard
upid dashboard

# Specific metrics
upid dashboard --metric cpu --time-range 24h
```

## Machine Learning
```bash
# Resource prediction
upid ml predict --resource cpu --horizon 7d

# Anomaly detection
upid ml anomalies --severity high
```

## Business Intelligence
```bash
# View KPIs
upid bi kpis --time-range 30d

# ROI analysis
upid bi roi --time-range 90d
```

## Cloud Integration
```bash
# AWS costs
upid cloud aws costs --time-range 30d

# GCP costs
upid cloud gcp costs --time-range 30d

# Azure costs
upid cloud azure costs --time-range 30d
```

## Storage Management
```bash
# Backup data
upid storage backup --output backup.tar.gz

# Restore data
upid storage restore --input backup.tar.gz

# Cleanup old data
upid storage cleanup --older-than 30d
```

## Troubleshooting
```bash
# Test connection
upid test connection

# System status
upid system status

# Debug mode
upid --debug analyze cluster

# Support bundle
upid support bundle --output support-bundle.tar.gz
```

## Configuration
```bash
# Environment variables
export UPID_JWT_SECRET="your-secret"
export UPID_REDIS_HOST="localhost"
export UPID_DB_PATH="/path/to/upid.db"

# Config file: ~/.upid/config.yaml
auth:
  default_provider: "local"
  mfa_required: true
storage:
  database_path: "/path/to/upid.db"
monitoring:
  metrics_interval: 60
```

## API Commands
```bash
# Start API server
upid api start --port 8080

# API endpoints
GET /api/v1/analysis/cluster
POST /api/v1/auth/login
GET /api/v1/dashboard/metrics
```

## Help Commands
```bash
# General help
upid --help

# Command help
upid analyze --help
upid optimize --help

# Version
upid --version
```

## Default Credentials
- **Username**: admin
- **Password**: admin123
- **User**: user
- **Password**: user123

## Common Flags
```bash
--time-range 1h|6h|24h|7d|30d
--namespace <namespace>
--output <file>
--format json|pdf|csv
--debug
--verbose
```

## File Locations
- **Config**: `~/.upid/config.yaml`
- **Database**: `~/.upid/upid_data.db`
- **Logs**: `~/.upid/logs/`
- **Backups**: `~/.upid/backups/` 