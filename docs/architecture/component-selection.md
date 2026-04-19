# Open-Core Component Selection

## Selected Components

| Area | Selection | Reason |
|---|---|---|
| Backend Framework | FastAPI | Async support and clean OpenAPI generation |
| Task Queue | Celery + Redis | Broad ecosystem and predictable operations |
| Primary Database | PostgreSQL + TimescaleDB | Transactional core plus time-series analytics |
| Ledger | TigerBeetle or Blnk | High integrity double-entry support |
| API Gateway | Kong OSS | Mature open-source policy enforcement |
| Secret Management | HashiCorp Vault | Strong secret lifecycle controls |
| Security Tooling | Trivy, OWASP ZAP, Snyk | Shift-left and runtime scanning coverage |
| Observability | ELK + Prometheus + Grafana | Logs, metrics, and dashboards in one stack |
