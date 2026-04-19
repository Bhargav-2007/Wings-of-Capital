# Wings of Capital - Implementation Plan

This plan follows SSDLC phases in strict order. Work proceeds only when explicitly approved with "NEXT TASK" or "PROCEED TO PHASE X".

## Planning Model

- Effort scale: XS (0.5 day), S (1 day), M (2-3 days), L (4-5 days), XL (1-2 weeks)
- Dependency notation: `D#` references prerequisite task IDs
- Completion gate: each phase has measurable success criteria

## Gantt-Style Roadmap (High Level)

```text
Week:     1   2   3   4   5   6   7   8   9   10  11  12
Phase 1: [########]
Phase 2:     [##########]
Phase 3:             [####################]
Phase 4:                           [############]
Phase 5:                                      [############]
```

## Phase 1 - Planning and Compliance Mapping

Objective: establish regulatory, threat, and architectural baseline.

| ID | Task | Effort | Dependencies | Deliverable | Success Criteria |
|---|---|---|---|---|---|
| P1-01 | Define system boundaries and fintech domains | S | - | `docs/scope/system-boundaries.md` | All in-scope domains listed and approved |
| P1-02 | Map RBI/SEBI controls to platform capabilities | M | P1-01 | `docs/compliance/rbi-sebi-mapping.md` | Controls mapped to owners and services |
| P1-03 | Map global controls (GDPR, DORA, NIS2, PSD3, PCI-DSS, EU AI Act) | M | P1-01 | `docs/compliance/global-mapping.md` | Required controls and applicability matrix complete |
| P1-04 | Build STRIDE threat model per trust boundary | M | P1-01 | `docs/security/stride-model.md` | Threats include mitigations and residual risk |
| P1-05 | Select open-core components and justify alternatives | S | P1-02, P1-03 | `docs/architecture/component-selection.md` | Every major dependency has rationale and risk |
| P1-06 | Define data classification and retention policy | S | P1-02, P1-03 | `docs/governance/data-policy.md` | PII and financial data handling approved |
| P1-07 | Phase 1 review gate | XS | P1-04, P1-05, P1-06 | `docs/reviews/phase-1-gate.md` | Formal sign-off for architecture design |

## Phase 2 - Design and Secure Architecture

Objective: produce secure target architecture and service contracts.

| ID | Task | Effort | Dependencies | Deliverable | Success Criteria |
|---|---|---|---|---|---|
| P2-01 | Define zero-trust microservice topology | M | P1-07 | `docs/architecture/topology.md` | East-west authN/authZ model finalized |
| P2-02 | Design immutable event sourcing and audit log schema | M | P1-07 | `docs/architecture/event-sourcing.md` | End-to-end event chain is tamper-evident |
| P2-03 | Define tokenization strategy (PII and payment data) | M | P1-06 | `docs/security/tokenization.md` | Data classes mapped to tokenization controls |
| P2-04 | Author API contracts (OpenAPI + event contracts) | L | P2-01, P2-02 | `docs/contracts/` | Contracts lint-clean and versioned |
| P2-05 | Design frontend information architecture and API bindings | S | P2-04 | `docs/frontend/ia-and-flows.md` | All UI modules mapped to service endpoints |
| P2-06 | Design observability and audit telemetry model | S | P2-01, P2-02 | `docs/ops/observability-design.md` | Metrics, logs, traces, and alerts defined |
| P2-07 | Phase 2 review gate | XS | P2-03, P2-04, P2-06 | `docs/reviews/phase-2-gate.md` | Architecture approved for implementation |

## Phase 3 - DevSecOps and Secure Implementation

Objective: build platform skeleton and core services with shift-left security.

| ID | Task | Effort | Dependencies | Deliverable | Success Criteria |
|---|---|---|---|---|---|
| P3-01 | Initialize repo structure and service scaffolds | S | P2-07 | `services/`, `frontend/`, `shared/` | Layout matches target structure |
| P3-02 | Create Docker and Compose baseline for all services | M | P3-01 | `docker-compose.yml`, service Dockerfiles | `docker compose config` valid |
| P3-03 | Implement Kong gateway and routing policies | M | P3-01 | `services/api-gateway/` | Authenticated routing for all service groups |
| P3-04 | Implement shared auth, secrets, audit middleware | L | P3-01 | `shared/security/` | Reusable middleware integrated in services |
| P3-05 | Implement core-ledger service (TigerBeetle/Blnk integration) | L | P3-02, P3-04 | `services/core-ledger/` | Double-entry posting and balance checks pass |
| P3-06 | Implement onchain-analytics ingestion and processing | L | P3-02, P3-04 | `services/onchain-analytics/` | Ingestion and aggregation pipelines operational |
| P3-07 | Implement ai-engine inference and scoring endpoints | L | P3-02, P3-04 | `services/ai-engine/` | Inference endpoints return deterministic schema |
| P3-08 | Implement fraud-detection service with anomaly pipeline | L | P3-07 | `services/fraud-detection/` | Risk score latency and quality baselines met |
| P3-09 | Implement payment-gateway and stablecoin/token rails adapter | L | P3-03, P3-04 | `services/payment-gateway/` | Sandbox transfer lifecycle complete |
| P3-10 | Implement kyc-service and AML checks workflow | L | P3-04 | `services/kyc-service/` | KYC states and audit trail complete |
| P3-11 | Build vanilla frontend modules and responsive dashboard | L | P2-05, P3-03 | `frontend/` | Mobile and desktop support validated |
| P3-12 | Integrate Trivy, Snyk, OWASP ZAP in shift-left pipelines | M | P3-02 | CI workflow configs | Security scans run on PR and main |
| P3-13 | Dependency pinning and SBOM generation | S | P3-02 | lockfiles + SBOM artifacts | Reproducible dependency graph |
| P3-14 | Phase 3 review gate | XS | P3-05..P3-13 | `docs/reviews/phase-3-gate.md` | MVP implementation approved for verification |

## Phase 4 - Verification and Testing

Objective: verify financial correctness, security posture, and system behavior.

| ID | Task | Effort | Dependencies | Deliverable | Success Criteria |
|---|---|---|---|---|---|
| P4-01 | Write ledger invariants and double-entry unit tests | M | P3-05 | `tests/ledger/` | No invariant violations across test suite |
| P4-02 | Build contract and integration tests for service mesh | M | P3-14 | `tests/integration/` | Critical flows pass in CI |
| P4-03 | Add SAST/DAST automation and policy thresholds | M | P3-12 | CI policy configs | Blocking thresholds enforced |
| P4-04 | Run security benchmark and hardening checks | S | P4-03 | `docs/security/hardening-report.md` | Critical findings resolved or accepted |
| P4-05 | Create penetration testing plan and mock execution report | S | P4-03 | `docs/security/pentest-plan.md` | Plan approved and traceable |
| P4-06 | Run performance and resilience tests (load + chaos-lite) | M | P3-14 | `docs/ops/perf-resilience.md` | SLO baselines defined and met |
| P4-07 | Phase 4 review gate | XS | P4-01..P4-06 | `docs/reviews/phase-4-gate.md` | Release candidate approved |

## Phase 5 - Deployment and Maintenance

Objective: deliver repeatable deployments, governance, and operational excellence.

| ID | Task | Effort | Dependencies | Deliverable | Success Criteria |
|---|---|---|---|---|---|
| P5-01 | Build Terraform modules for core infrastructure | L | P4-07 | `terraform/` | `terraform validate` passes for all modules |
| P5-02 | Implement GitHub Actions CI/CD pipelines | M | P4-07 | `.github/workflows/` | Build/test/security/deploy lanes green |
| P5-03 | Configure observability stack (ELK + Prometheus/Grafana) | M | P5-01 | `ops/monitoring/` configs | Alerts and dashboards operational |
| P5-04 | Define release process and environment promotion policy | S | P5-02 | `docs/governance/release-process.md` | Change approvals and rollback documented |
| P5-05 | Define incident response and vulnerability management workflow | S | P5-03 | `docs/governance/incident-response.md` | Incident runbooks tested |
| P5-06 | Publish operations handover and maintenance guide | S | P5-04, P5-05 | `docs/ops/maintenance.md` | Team can operate without tribal knowledge |
| P5-07 | Phase 5 review gate and v1.0 go/no-go | XS | P5-01..P5-06 | `docs/reviews/phase-5-gate.md` | Formal launch decision recorded |

## Cross-Phase Quality Gates

| Gate | Minimum Standard |
|---|---|
| Security | No untriaged critical vulnerabilities |
| Compliance | Mapped controls with evidence links |
| Reliability | SLO definitions and monitoring in place |
| Financial Integrity | Ledger invariants enforced in tests |
| Auditability | Immutable event trail for critical actions |
| Reproducibility | One-command local stack startup documented |

## Initial Command Set (Repository Bootstrap)

Use these commands when execution is approved:

```bash
mkdir -p terraform services/{core-ledger,ai-engine,onchain-analytics,payment-gateway,fraud-detection,kyc-service} frontend/{css,js,assets} shared docs .github/workflows .devcontainer scripts

cat > LICENSE << 'EOF'
Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
EOF

curl -fsSL https://www.apache.org/licenses/LICENSE-2.0.txt >> LICENSE

git add README.md IMPLEMENTATION-PLAN.md LICENSE
git commit -m "chore: initialize Wings of Capital project foundation docs"
```

## Task Execution Rule

No phase task starts until explicitly requested. Expected commands from user:

- `NEXT TASK`
- `PROCEED TO PHASE 1`
- `PROCEED TO PHASE 2`
- `PROCEED TO PHASE 3`
- `PROCEED TO PHASE 4`
- `PROCEED TO PHASE 5`
