# Requirements Traceability Matrix (RTM)

Document ID: SML-RTM-001  
Version: 1.0  
Effective Date: 2026-04-06

## 1. Purpose

Provide bidirectional traceability from URS requirements to verification protocols, test cases, and objective evidence.

## 2. Source Documents

- SML-URS-001 (User Requirements Specification)
- SML-IQ-001 (Installation Qualification)
- SML-OQ-001 (Operational Qualification)
- SML-PQ-001 (Performance Qualification)

## 3. RTM Table

| Requirement ID | Requirement Summary | Risk Ref | Verification Level | Test/Check ID | Evidence Artifact | Status |
|---|---|---|---|---|---|---|
| FR-001 | Ingest normal/tumor inputs and produce structured output | R-004 | OQ | OQ-FUNC-01 | OQ execution record, output JSON sample | Planned |
| FR-002 | Generate machine-readable report artifacts | R-004 | OQ | OQ-FUNC-01 | OQ execution record, schema validation log | Planned |
| FR-003 | Provide runtime status endpoints | R-004 | OQ | OQ-FUNC-02, OQ-FUNC-03 | Endpoint response capture | Planned |
| FR-004 | Preserve run metadata and timestamps | R-002 | OQ | OQ-FUNC-01, OQ-COMP-01 | Audit log extract and run artifact | Planned |
| FR-005 | Support controlled release records | R-006 | PQ | PQ-E2E-01 | PQ workflow evidence and release record | Planned |
| RR-001 | Attributable, time-stamped, reviewable audit trail | R-002 | OQ | OQ-COMP-01 | Audit trail test report | Planned |
| RR-002 | Electronic signatures linked to records | R-002 | OQ | OQ-COMP-02 | Signature verification report | Planned |
| RR-003 | Role-based permissions enforcement | R-001 | OQ | OQ-SEC-01 | Access matrix and denied-action log | Planned |
| RR-004 | PHI/PII handling aligned to privacy requirements | R-003 | OQ | OQ-PRIV-01 | De-identification test evidence | Planned |
| RR-005 | Change control via controlled SOPs | R-004 | QA | SOP review | Approved SOP package with signatures | Planned |
| TR-001 | Containerized deployment mode | R-004 | IQ | IQ-SW-02 | Installation verification evidence | Planned |
| TR-002 | Health/status API exposure | R-004 | IQ/OQ | IQ-SW-06, OQ-FUNC-02, OQ-FUNC-03 | API check logs | Planned |
| TR-003 | Backup and restore support | R-005 | OQ/PQ | OQ-DR-01, OQ-DR-02, PQ-PERF-02 | Backup and restore execution logs | Planned |
| TR-004 | Logging for investigation and CAPA | R-002 | OQ | OQ-COMP-01 | Log retention and sample investigation report | Planned |
| TR-005 | Environment separation by procedure | R-004 | QA | Deployment audit | DEV/TEST/VAL/PROD release records | Planned |
| PR-001 | Health response <= 2s | R-004 | OQ | OQ-FUNC-03 | Timed endpoint test output | Planned |
| PR-002 | Status response <= 3s | R-004 | OQ | OQ-FUNC-02 | Timed endpoint test output | Planned |
| PR-003 | Pipeline completion <= 10 minutes | R-006 | PQ | PQ-PERF-01 | Timed PQ run report | Planned |

## 4. Execution Notes

- Update Status to Pass/Fail/Blocked during OQ/PQ execution.
- Each evidence artifact must include date, executor, and approver.
- Any failed requirement requires deviation entry and CAPA linkage.

## 5. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By |  |  |  |
| Reviewed By (QA) |  |  |  |
| Approved By |  |  |  |
