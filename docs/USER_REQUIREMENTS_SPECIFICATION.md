# User Requirements Specification (URS)

Document ID: SML-URS-001  
Version: 1.0  
Effective Date: 2026-04-06  
System: OncoSML mRNA Vaccine System

## 1. Purpose

This URS defines user, regulatory, and technical requirements for the OncoSML system intended to support clinical trial preparation workflows under controlled quality processes.

## 2. Scope

In scope:
- Controlled clinical analysis workflows
- Data integrity, traceability, and auditability
- Security, privacy, and access control
- Validation evidence generation (IQ/OQ/PQ)

Out of scope:
- Direct diagnosis/treatment decisioning
- GMP wet-lab manufacturing execution systems

## 3. Stakeholders

- Regulatory Lead
- QA Lead
- Clinical Lead
- Bioinformatics/Software Lead
- Data Protection Lead

## 4. Functional Requirements

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| FR-001 | System shall ingest normal and tumor sequence inputs and produce a structured pipeline output. | High | OQ functional test |
| FR-002 | System shall generate machine-readable report artifacts (JSON) for each run. | High | OQ functional test |
| FR-003 | System shall provide status endpoints for runtime monitoring. | Medium | OQ interface test |
| FR-004 | System shall preserve run metadata including timestamps and sample identifiers. | High | OQ data integrity test |
| FR-005 | System shall support controlled release records for GMP-aligned review. | High | PQ workflow test |

## 5. Regulatory and Compliance Requirements

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| RR-001 | Audit trail entries shall be attributable, time-stamped, and reviewable. | High | OQ security/compliance test |
| RR-002 | Electronic signatures shall be linked to signed records. | High | OQ signature test |
| RR-003 | Access control shall enforce role-based permissions. | High | OQ security test |
| RR-004 | Data handling shall align with HIPAA/GDPR principles for PHI/PII. | High | OQ privacy test |
| RR-005 | Change control shall be documented via controlled SOPs. | High | QA document review |

## 6. Technical Requirements

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| TR-001 | System shall run in containerized deployment mode for controlled environments. | High | IQ deployment check |
| TR-002 | System shall expose health and status API endpoints. | High | IQ/OQ test |
| TR-003 | System shall support backup and restore procedures for critical artifacts. | High | OQ/PQ recovery test |
| TR-004 | System shall generate logs sufficient for investigation and CAPA. | High | OQ log review |
| TR-005 | System shall maintain environment separation (DEV/TEST/VAL/PROD) by procedure. | High | QA audit |

## 7. Performance Requirements

| ID | Requirement | Target | Verification |
|---|---|---|---|
| PR-001 | Health endpoint response time | <= 2 seconds | OQ performance test |
| PR-002 | Status endpoint response time | <= 3 seconds | OQ performance test |
| PR-003 | Single patient pipeline completion (reference sample) | <= 10 minutes in validation env | PQ performance test |

## 8. Acceptance Criteria

The URS is considered accepted when:
- Requirements are approved by QA and business owners.
- Each requirement is mapped in a traceability matrix to OQ/PQ evidence.
- Deviations are documented and resolved via CAPA.

## 9. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By |  |  |  |
| Reviewed By (QA) |  |  |  |
| Approved By |  |  |  |
