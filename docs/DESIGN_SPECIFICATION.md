# Design Specification

Document ID: SML-DS-001  
Version: 1.0  
Effective Date: 2026-04-06  
System: OncoSML mRNA Vaccine System

## 1. Purpose

Defines logical and deployment design for a controlled clinical-support software environment aligned with URS requirements.

## 2. Architecture Overview

Primary components:
- CLI Orchestrator: main workflow command interface
- Pipeline Modules: mutation analysis, candidate scoring, mRNA design, validation
- Compliance Modules: audit trail, electronic signatures, privacy controls, RBAC
- Status API: health and operational status endpoints
- Storage: local artifacts and configured database backends

## 3. Deployment Model

- Container image: Dockerfile.clinical
- Orchestration baseline: docker-compose.clinical.yml
- Runtime command: run-service with health endpoint on port 8787
- Non-root runtime user and writable application artifact directories

## 4. Data Flow

1. Input acquisition (normal/tumor data + metadata)
2. Pipeline execution and rule evaluation
3. Artifact generation (JSON reports, release records)
4. Compliance logging and record retention
5. Monitoring via status API

## 5. Security Design

- RBAC model with role-permission mapping
- Password complexity and session timeout controls
- Audit trail chain linking for tamper indication
- Signature linkage for record authenticity
- Privacy controls for de-identification/pseudonymization paths

## 6. Interface Specification

| Interface | Method | Purpose | Response |
|---|---|---|---|
| /health | GET | Liveness and DB presence check | JSON status payload |
| /status | GET | Runtime and pipeline summary | JSON metrics payload |

## 7. Traceability to URS

| URS ID | Design Element |
|---|---|
| FR-001/FR-002 | Pipeline modules and report serializers |
| FR-003 | Status API endpoints |
| RR-001/RR-002 | Audit trail and e-signature modules |
| RR-003 | Access control manager |
| RR-004 | Privacy manager methods |
| TR-001 | Clinical container and compose artifacts |

## 8. Constraints and Assumptions

- External genomics tooling may be required for full real-world stack runs.
- Clinical evidence generation depends on controlled validation environment execution.
- Integration with enterprise IAM/HSM/SIEM is pending implementation plan.

## 9. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By |  |  |  |
| Reviewed By (QA) |  |  |  |
| Approved By |  |  |  |
