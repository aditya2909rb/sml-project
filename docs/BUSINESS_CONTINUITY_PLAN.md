# Business Continuity Plan

Document ID: SML-BCP-001  
Version: 1.0  
Effective Date: 2026-04-06

## 1. Purpose

Ensure continuity of trial-support software operations during disruptions.

## 2. Critical Functions

- Artifact generation for patient workflow runs
- Compliance record retention and retrieval
- Status visibility for operations and QA

## 3. Continuity Strategies

- Alternate personnel coverage and on-call rota
- Controlled fallback execution environment
- Prioritized service restoration order

## 4. Minimum Operational Mode

If full platform is unavailable:
1. Restore status and evidence access.
2. Resume controlled pipeline execution for critical cases.
3. Maintain audit and incident records throughout degraded operation.

## 5. Dependencies

- Cloud/on-prem compute availability
- Backup repository access
- Security and identity services

## 6. Review and Maintenance

- Review quarterly or after major incident.
- Update contact lists and dependency map each cycle.
