# Tokenization Strategy

## Token Targets

- KYC PII fields
- Payment account identifiers
- Sensitive transaction metadata

## Rules

- Replace cleartext values with reversible vault-backed tokens.
- Restrict detokenization to approved service accounts.
- Log every tokenization and detokenization event.
