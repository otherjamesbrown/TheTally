# Logging Strategy

## Overview

TheTally implements a comprehensive logging strategy using Grafana Loki + Prometheus + Grafana for observability, security, and debugging. This approach provides cost-effective, platform-agnostic logging with real-time analysis capabilities.

## Architecture

### Logging Stack
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │      Loki       │    │    Grafana      │
│   (Structured   │───►│   (Logs)        │───►│  (Dashboards)   │
│    Logs)        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        │
                       ┌─────────────────┐              │
                       │  Cloud Storage  │              │
                       │ (Log Chunks)    │              │
                       └─────────────────┘              │
                                                        │
┌─────────────────┐    ┌─────────────────┐              │
│   Application   │    │   Prometheus    │──────────────┘
│   (Metrics)     │───►│   (Metrics)     │
└─────────────────┘    └─────────────────┘
```

### Components
- **Loki**: Log aggregation and storage
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Cloud Storage**: Long-term log archive
- **Single Instance**: All components on one Compute Engine instance

## Log Types

### 1. Audit Logs 🔍
**Purpose**: Security, compliance, and regulatory requirements

**What to log**:
- Authentication events (login, logout, failed attempts, 2FA)
- Data access (who accessed what financial data when)
- Administrative actions (user management, permission changes)
- Sensitive operations (file uploads, data exports, account deletions)
- API key usage (which keys accessed what endpoints)

**Storage**:
- **Primary**: Loki (searchable, real-time)
- **Archive**: Cloud Storage (immutable, long-term)
- **Retention**: 7 years in Cloud Storage, 1 year in Loki (configurable)

**Sample Log**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "AUDIT",
  "user_id": "user_123",
  "session_id": "sess_456",
  "action": "transaction_import",
  "resource": "account_789",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "result": "success",
  "metadata": {
    "file_size": 1024,
    "transaction_count": 150
  }
}
```

### 2. Functional Logs 📊
**Purpose**: Business intelligence and application usage analytics

**What to log**:
- User actions (transaction imports, categorization rules created)
- Feature usage (which features are used most/least)
- Performance metrics (response times, file processing times)
- Business events (new accounts created, monthly summaries generated)
- User journeys (complete workflows from login to action completion)

**Storage**:
- **Primary**: Loki (real-time analysis)
- **Retention**: 1 year (configurable)

**Sample Log**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "event": "categorization_rule_created",
  "user_id": "user_123",
  "rule_id": "rule_456",
  "pattern": "Tesco",
  "category": "Groceries",
  "metadata": {
    "confidence": 0.95,
    "auto_generated": false
  }
}
```

### 3. Debug Logs 🐛
**Purpose**: Development, troubleshooting, and AI assistant debugging

**What to log**:
- Application flow (function entry/exit, decision points)
- Error details (stack traces, error context, recovery attempts)
- Performance (database query times, memory usage)
- Integration points (external API calls, file processing steps)
- AI assistant context (reasoning steps, token usage, decision points)

**Storage**:
- **Primary**: Loki (searchable)
- **Retention**: 30 days (configurable)

**Sample Log**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "DEBUG",
  "component": "ai_assistant",
  "action": "deploy_application",
  "tokens_used": 1500,
  "reasoning": "User requested deployment, checking prerequisites...",
  "steps": [
    "Checking infrastructure status",
    "Running test suite",
    "Building Docker images"
  ],
  "result": "success",
  "metadata": {
    "deployment_time": "2m30s",
    "tests_passed": 45,
    "tests_failed": 0
  }
}
```

## Configuration

### Log Retention (Configurable)
```yaml
# loki-config.yaml
retention_period:
  audit_logs: "1y"      # 1 year in Loki
  functional_logs: "1y" # 1 year in Loki
  debug_logs: "30d"     # 30 days in Loki

# Cloud Storage archive
archive_retention:
  audit_logs: "7y"      # 7 years in Cloud Storage
```

### Log Levels (Configurable)
```yaml
# application-config.yaml
logging:
  levels:
    audit: "AUDIT"
    functional: "INFO"
    debug: "DEBUG"
  
  components:
    ai_assistant:
      level: "DEBUG"
      include_tokens: true
      include_reasoning: true
    database:
      level: "INFO"
    api:
      level: "INFO"
```

### Instance Sizing
```yaml
# infrastructure-config.yaml
logging_instance:
  machine_type: "e2-medium"  # 2 vCPU, 4GB RAM
  disk_size: "50GB"
  cost_estimate: "$25/month"
  
  # Alternative for higher loads
  # machine_type: "e2-large"   # 2 vCPU, 8GB RAM
  # cost_estimate: "$50/month"
```

## Query Examples

### LogQL Queries (Loki)
```logql
# Get all errors in the last hour
{level="ERROR"} |= "error" | json

# Get audit logs for specific user
{level="AUDIT"} | json | user_id="user_123"

# Get AI assistant debug logs
{component="ai_assistant"} | json | level="DEBUG"

# Get functional logs for categorization
{event="categorization_rule_created"} | json
```

### PromQL Queries (Prometheus)
```promql
# API response time (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Active users
sum(rate(user_sessions_total[5m]))
```

## AI Assistant Integration

### Querying Logs
```python
import requests
from datetime import datetime, timedelta

class LogAnalyzer:
    def __init__(self, loki_url, prometheus_url):
        self.loki_url = loki_url
        self.prometheus_url = prometheus_url
    
    def get_recent_errors(self, hours=1):
        """Get recent errors for debugging"""
        query = '{level="ERROR"} |= "error"'
        return self.query_loki(query, hours)
    
    def get_user_actions(self, user_id):
        """Get audit trail for specific user"""
        query = f'{{level="AUDIT"}} | json | user_id="{user_id}"'
        return self.query_loki(query)
    
    def get_ai_context(self, action):
        """Get AI assistant debug context"""
        query = f'{{component="ai_assistant"}} | json | action="{action}"'
        return self.query_loki(query)
    
    def get_performance_metrics(self):
        """Get application performance metrics"""
        query = 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))'
        return self.query_prometheus(query)
```

## Security & Access Control

### Access Control
- **Audit logs**: Only accessible by you (admin)
- **Functional logs**: Accessible by you and authorized users
- **Debug logs**: Accessible by you and development team

### Data Privacy
- **PII handling**: No PII in functional or debug logs
- **Audit logs**: Minimal PII (user_id, IP address)
- **Data retention**: Configurable per log type
- **Encryption**: All logs encrypted in transit and at rest

## Cost Optimization

### Storage Costs
- **Loki**: ~$15/month (e2-medium instance)
- **Cloud Storage**: ~$2-5/month (log chunks)
- **Total**: ~$20-25/month

### Optimization Strategies
- **Log compression**: Loki compresses logs automatically
- **Retention policies**: Aggressive retention for debug logs
- **Cloud Storage**: Use Nearline storage for archives
- **Instance sizing**: Start small, scale up as needed

## Monitoring & Alerting

### Key Metrics
- **Log volume**: Logs per second, storage usage
- **Error rates**: Application errors, failed requests
- **Performance**: Response times, database queries
- **Security**: Failed logins, suspicious activity

### Alerting Rules (Future)
- High error rate (>5% errors)
- Failed login attempts (>10 in 5 minutes)
- High memory usage (>80%)
- Log storage approaching limits

## Implementation

### Infrastructure Setup
The logging stack is included in the main infrastructure setup script:
```bash
./scripts/setup-infrastructure.sh
```

### Application Integration
```python
# Python logging configuration
import structlog
import logging

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

---

*This logging strategy will evolve as the application grows and new requirements emerge.*
