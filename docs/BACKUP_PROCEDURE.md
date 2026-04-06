# Backup Procedure

Document ID: SML-BKP-001  
Version: 1.0  
Effective Date: 2026-04-06

## 1. Objective

Operational instructions for executing and verifying scheduled backups.

## 2. Backup Targets

- outputs/
- model_store/
- audit and signature storage paths
- configured database files/dumps

## 3. Procedure

1. Confirm backup window and target system state.
2. Run backup job per approved schedule.
3. Capture checksums and job logs.
4. Verify backup completeness.
5. Store copy in secondary location.

## 4. Verification Checklist

- [ ] Backup job completed without error.
- [ ] Checksums recorded.
- [ ] Artifact inventory matches source.
- [ ] Secondary copy available.

## 5. Record

| Run ID | Date/Time | Operator | Status | Checksum File | Notes |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
