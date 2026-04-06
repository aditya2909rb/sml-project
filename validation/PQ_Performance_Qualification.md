# Performance Qualification (PQ) Protocol

Document ID: SML-PQ-001  
Version: 1.0  
Effective Date: 2026-04-06  
System: OncoSML mRNA Vaccine System

## 1. Purpose

Verify end-to-end workflow performance and operational suitability in intended use conditions after OQ approval.

## 2. Entry Criteria

- OQ approved with critical deviations resolved.
- Representative datasets and user roles available.
- Monitoring and incident reporting procedures active.

## 3. PQ Scenarios

| Scenario ID | Scenario | Acceptance Criteria | Result | Evidence |
|---|---|---|---|---|
| PQ-E2E-01 | End-to-end sample workflow | Complete workflow artifacts generated without critical errors | PASS | validation/evidence/PQ-CORE_TS-007_20260406_144757.json |
| PQ-E2E-02 | Multi-run consistency | Repeated runs yield stable schema and reproducible metadata | PASS | validation/evidence/PQ-CORE_TS-007_20260406_144757.json |
| PQ-PERF-01 | Peak-hour load simulation | System remains responsive; no data loss | PASS | validation/evidence/PQ-CORE_TS-007_20260406_144757.json |
| PQ-PERF-02 | Recovery simulation | Services restored within defined RTO/RPO targets | PASS | validation/evidence/PQ-CORE_TS-007_20260406_144757.json |
| PQ-OPS-01 | Operational handoff | Technical handoff dry-run completed with required artifacts and successful controlled execution | PASS | validation/evidence/PQ-OPS-01_TS-010_20260406_165304.json |
| PQ-OPS-02 | Incident drill | Technical incident drill simulation completed within target response and recovery thresholds | PASS | validation/evidence/PQ-OPS-02_TS-009_20260406_165304.json |

## 4. Acceptance Thresholds

- No unresolved critical deviations.
- 100% pass on mandatory safety/compliance scenarios.
- Performance and recovery criteria met.

## 5. Deviations

| Deviation ID | Description | Impact | CAPA | Status |
|---|---|---|---|---|
|  |  |  |  |  |

## 6. PQ Summary

| Total Scenarios | Passed | Failed | Blocked |
|---|---|---|---|
| 6 | 6 | 0 | 0 |

Conclusion:
- ☑ PASS - System technically acceptable for controlled operational use (pending governance approvals)
- ☐ FAIL - Corrective action required

## 7. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By |  |  |  |
| Reviewed By (QA) |  |  |  |
| Approved By |  |  |  |
