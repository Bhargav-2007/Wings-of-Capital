# Data Classification and Retention Policy

## Data Classes

| Class | Examples | Handling Rule |
|---|---|---|
| Public | Documentation and static metadata | Open distribution |
| Internal | Operational telemetry and non-sensitive metrics | Controlled internal access |
| Confidential | Business rules and scoring models | Restricted role-based access |
| Regulated | KYC identity data and financial records | Tokenized, encrypted, audited |

## Retention Baseline

- KYC and transaction audit trails: retain per legal requirement and jurisdiction.
- Operational logs: retain based on security and forensics baseline.
- AI feature data: minimize and expire according to lawful basis.
