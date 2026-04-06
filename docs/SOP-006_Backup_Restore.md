# SOP-006 Backup and Restore

Document ID: SOP-006  
Version: 1.0  
Effective Date: 2026-04-06

## 1. Purpose

Define backup and restore controls for critical system data and artifacts to maintain integrity and availability.

## 2. Scope

Covers:
- Pipeline output artifacts
- Model state and configuration
- Audit and signature records
- Operational logs relevant to investigations

## 3. Backup Policy

- Daily incremental backups
- Weekly full backups
- Immutable copy retention for regulated records
- Encryption at rest and in transit

## 4. Restore Procedure

1. Open change/incident record for restore event.
2. Select validated backup set and verify checksum.
3. Restore into controlled target environment.
4. Run integrity checks and sample verification workflow.
5. Document outcome and QA signoff.

## 5. Testing Frequency

- Restore drill at least quarterly.
- Evidence retained in validation records.

## 6. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By |  |  |  |
| Reviewed By (QA) |  |  |  |
| Approved By |  |  |  |
