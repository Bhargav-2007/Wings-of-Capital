# RBI and SEBI Regulatory Mapping

## Scope

This document maps core RBI and SEBI expectations to Wings of Capital platform services and controls.

## Control Mapping

| Regulation Area | Platform Control | Service Owner | Evidence Artifact |
|---|---|---|---|
| KYC and Customer Onboarding | Identity verification and risk scoring pipeline | kyc-service | KYC logs, onboarding decisions |
| AML Monitoring | Transaction screening and anomaly scoring | fraud-detection, core-ledger | AML alerts and case records |
| Data Privacy and Consent | Consent-aware data access patterns | payment-gateway, ai-engine | Consent records and access logs |
| Auditability | Immutable event trail for financial operations | core-ledger | Event store snapshots |
| Cybersecurity Governance | Shift-left scans and hardening checks | shared/security | CI scan artifacts |
