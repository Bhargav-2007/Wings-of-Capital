# Event Sourcing and Immutable Audit Log

- Every state-changing command emits an append-only event.
- Events carry correlation ID, actor ID, and integrity checksum.
- Ledger and compliance views are reconstructed from events.
- Audit stream is write-once and tamper-evident.
