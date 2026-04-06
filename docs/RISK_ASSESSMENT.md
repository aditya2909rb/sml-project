# Risk Assessment (GAMP 5 Aligned)

Document ID: SML-RA-001  
Version: 1.0  
Effective Date: 2026-04-06

## 1. Purpose

Identify and control software risks affecting data integrity, patient safety decisions, security, and compliance obligations.

## 2. Method

- Framework: GAMP 5 risk-based approach
- Dimensions: Severity (S), Occurrence (O), Detectability (D)
- Scoring: RPN = S x O x D
- Bands: High (>= 40), Medium (20-39), Low (< 20)

## 3. Risk Register

| Risk ID | Description | Category | S | O | D | RPN | Mitigation | Residual |
|---|---|---|---|---|---|---|---|---|
| R-001 | Unauthorized access to clinical artifacts | Security | 5 | 3 | 3 | 45 | Enforce RBAC, MFA, lockout, access reviews | Medium |
| R-002 | Incomplete audit history for critical actions | Compliance | 5 | 2 | 4 | 40 | Mandatory audit logging + integrity verification | Medium |
| R-003 | Improper PHI/PII handling in outputs/logs | Privacy | 5 | 3 | 3 | 45 | De-identification checks + privacy SOP controls | Medium |
| R-004 | Unvalidated runtime deployment drift | Validation | 4 | 3 | 3 | 36 | Controlled configs + IQ/OQ/PQ evidence | Medium |
| R-005 | Data loss during infrastructure incident | Business continuity | 4 | 3 | 3 | 36 | Backup/restore procedures + DR exercises | Medium |
| R-006 | Incorrect workflow interpretation by users | Clinical ops | 4 | 2 | 3 | 24 | Controlled training + competency records | Low |

## 4. High-Risk Control Plan

- R-001: Quarterly access review, least-privilege enforcement.
- R-002: Daily audit integrity check and monthly QA review.
- R-003: PHI/PII redaction test cases in OQ.
- R-004: Change control gating before environment promotion.

## 5. Verification Plan

- IQ verifies installation and baseline controls.
- OQ verifies functional/security/privacy behavior under controlled conditions.
- PQ verifies end-to-end workflow performance and operational consistency.

## 6. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By |  |  |  |
| Reviewed By (QA) |  |  |  |
| Approved By |  |  |  |
