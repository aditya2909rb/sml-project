# Environment Separation and Release Controls

Date: 2026-04-06

## 1. Environment Model

- DEV: Active development and feature changes
- TEST: Functional and integration testing
- VAL: Controlled validation execution (IQ/OQ/PQ evidence)
- PROD: Restricted production environment for approved releases only

## 2. Release Promotion Rules

1. DEV -> TEST requires successful unit/integration tests.
2. TEST -> VAL requires frozen build hash and approved change record.
3. VAL -> PROD requires IQ/OQ/PQ evidence package and QA approval.
4. Emergency change path requires documented incident and post-release CAPA.

## 3. Controlled Artifacts

- Source tag or commit hash
- Container image digest
- Requirements lock/version list
- Validation evidence references
- Approval records

## 4. Deployment Record Locations

- validation/deployment_records/DEV_RELEASE_RECORD.md
- validation/deployment_records/TEST_RELEASE_RECORD.md
- validation/deployment_records/VAL_RELEASE_RECORD.md
- validation/deployment_records/PROD_RELEASE_RECORD.md

## 5. Rollback Requirements

- Previous stable artifact reference
- Rollback trigger criteria
- Verification checklist after rollback
