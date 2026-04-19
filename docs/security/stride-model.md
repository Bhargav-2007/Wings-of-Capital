# STRIDE Threat Model

## Trust Boundaries

- Public client to API gateway
- API gateway to internal microservices
- Microservices to data stores and event bus
- Internal workloads to external APIs and public RPC endpoints

## Threat Summary

| Category | Example Threat | Initial Mitigation |
|---|---|---|
| Spoofing | Forged service identity | mTLS and signed service tokens |
| Tampering | Ledger mutation in transit | Immutable event chain and request signatures |
| Repudiation | Untraceable money movement | Correlated audit IDs and append-only logs |
| Information Disclosure | PII leakage in logs | Tokenization and field-level redaction |
| Denial of Service | API exhaustion | Rate limiting, autoscaling, queue isolation |
| Elevation of Privilege | Over-broad service roles | Least-privilege IAM and short-lived credentials |
