# Observability Design

## Signals

- Metrics: latency, throughput, error rate, queue lag.
- Logs: structured JSON with correlation IDs.
- Traces: distributed spans from gateway to data stores.

## Alerting

- SLO burn-rate alerts for API endpoints.
- Fraud scoring latency and model failure alerts.
- Ledger integrity and reconciliation anomaly alerts.
