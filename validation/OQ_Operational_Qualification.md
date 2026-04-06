# Operational Qualification (OQ) Protocol

Document ID: SML-OQ-001  
Version: 1.0  
Effective Date: 2026-04-06  
System: OncoSML mRNA Vaccine System

## 1. Purpose

Demonstrate the installed system operates as intended under controlled operating conditions.

## 2. Entry Criteria

- IQ completed and approved.
- URS and Design Specification approved.
- OQ environment baseline frozen.

## 3. OQ Test Matrix

| Test ID | Test Description | Acceptance Criteria | Result | Evidence |
|---|---|---|---|---|
| OQ-FUNC-01 | Run baseline patient pipeline | JSON output generated with expected schema | PASS | validation/evidence/OQ-FUNC-01_TS-002_20260406_142815.json |
| OQ-FUNC-02 | Validate status endpoint | /status returns valid JSON payload | PASS | validation/evidence/OQ-FUNC-02_03_TS-001_20260406_142214.json |
| OQ-FUNC-03 | Validate health endpoint | /health returns status ok | PASS | validation/evidence/OQ-FUNC-02_03_TS-001_20260406_142214.json |
| OQ-SEC-01 | Verify RBAC access denial | Unauthorized action blocked and logged | PASS | validation/evidence/OQ-SEC-01_02_TS-004_20260406_143655.json |
| OQ-SEC-02 | Verify session timeout behavior | Session invalid after configured timeout | PASS | validation/evidence/OQ-SEC-01_02_TS-004_20260406_143655.json |
| OQ-COMP-01 | Verify audit log creation | Critical user actions appear in audit trail | PASS | validation/evidence/OQ-COMP-01_02_TS-005_20260406_143602.json |
| OQ-COMP-02 | Verify e-signature linkage | Signature bound to record hash and metadata | PASS | validation/evidence/OQ-COMP-01_02_TS-005_20260406_143602.json |
| OQ-PRIV-01 | Verify de-identification controls | PHI/PII fields redacted per policy | PASS | validation/evidence/OQ-PRIV-01_TS-006_20260406_143603.json |
| OQ-DR-01 | Backup test | Backup artifact produced and cataloged | PASS | validation/evidence/OQ-DR-01_02_TS-003_20260406_142152.json |
| OQ-DR-02 | Restore test | Restored data integrity confirmed | PASS | validation/evidence/OQ-DR-01_02_TS-003_20260406_142152.json |

## 4. Deviations and CAPA

| Deviation ID | Description | Impact | CAPA | Status |
|---|---|---|---|---|
|  |  |  |  |  |

## 5. OQ Summary

| Total Tests | Passed | Failed | Blocked |
|---|---|---|---|
| 10 | 10 | 0 | 0 |

Conclusion:
- ☑ PASS - System suitable to proceed to PQ (pending formal QA/approver signatures)
- ☐ FAIL - Corrective action required before PQ

## 6. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By |  |  |  |
| Reviewed By (QA) |  |  |  |
| Approved By |  |  |  |
