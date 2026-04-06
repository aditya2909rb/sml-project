# Disaster Recovery Plan

Document ID: SML-DR-001  
Version: 1.0  
Effective Date: 2026-04-06

## 1. Purpose

Provide recovery strategy for major service disruption, infrastructure failure, or data compromise scenarios.

## 2. Recovery Objectives

- RTO: 8 hours (initial target)
- RPO: 24 hours (initial target)

## 3. DR Scenarios

- Host/system failure
- Data corruption event
- Security incident requiring environment rebuild

## 4. Recovery Steps

1. Declare disaster and appoint incident commander.
2. Isolate affected systems.
3. Restore from validated backups to recovery environment.
4. Validate integrity and required services (/health, /status, pipeline sample run).
5. Authorize cutover and communicate service restoration.

## 5. Communication Matrix

| Role | Contact | Responsibility |
|---|---|---|
| Incident Commander |  | Decision and coordination |
| QA Lead |  | Compliance oversight |
| DevOps Lead |  | Technical recovery execution |
| Security Lead |  | Security containment and review |

## 6. Test Cadence

- Tabletop drill: quarterly
- Technical failover drill: semi-annual
