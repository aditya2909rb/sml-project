# Clinical Readiness Action Plan (Execution Checklist)

Date: 2026-04-06
Current Gate Status: NO_GO
Target: Reach CONDITIONAL_GO with objective evidence

## 1. Regulatory and Ethics

Owner: Regulatory Lead

- [ ] Define IND/CTA strategy and jurisdiction scope.
  Evidence: Signed strategy memo, approval date, reviewer list.
- [ ] Complete pre-IND/scientific advice package and meeting.
  Evidence: Agency meeting minutes and action items.
- [ ] Draft protocol + investigator brochure + informed consent package.
  Evidence: Versioned docs with controlled approvals.
- [ ] Prepare IRB/IEC submission package.
  Evidence: Submission receipt and committee response.
- [ ] Prepare trial registration package.
  Evidence: Draft ClinicalTrials.gov/EUCTR record.

## 2. Quality System and Controlled Docs

Owner: QA Lead

- [x] Create draft URS, Design Specification, and Risk Assessment documents.
  Evidence: docs/USER_REQUIREMENTS_SPECIFICATION.md, docs/DESIGN_SPECIFICATION.md, docs/RISK_ASSESSMENT.md.
- [x] Create draft SOP-003 through SOP-006 documents.
  Evidence: docs/SOP-003_Document_Control.md through docs/SOP-006_Backup_Restore.md.
- [ ] Finalize and approve URS.
  Evidence: docs/USER_REQUIREMENTS_SPECIFICATION.md (approved version).
- [ ] Finalize and approve Design Specification.
  Evidence: docs/DESIGN_SPECIFICATION.md (approved version).
- [ ] Finalize and approve Risk Assessment.
  Evidence: docs/RISK_ASSESSMENT.md (GAMP 5 aligned).
- [ ] Add SOP-003 through SOP-006.
  Evidence: Controlled SOP files with signatures.
- [x] Build draft requirements traceability matrix (URS -> tests -> reports).
  Evidence: docs/REQUIREMENTS_TRACEABILITY_MATRIX.md.
- [ ] Finalize and approve requirements traceability matrix.
  Evidence: Signed RTM artifact.
- [x] Prepare signoff packet and approval forms.
  Evidence: docs/SIGNOFF_PACKET.md, docs/QA_APPROVAL_SHEET.md, docs/INCIDENT_DRILL_WORKSHEET.md.

## 3. CSV (Computer System Validation)

Owner: Validation Lead

- [ ] Execute IQ protocol with objective evidence and signatures.
  Evidence: Completed validation/IQ_Installation_Qualification.md.
- [x] Execute IQ technical baseline (software/security prerequisites).
  Evidence: validation/evidence/IQ-TECH-BASELINE_TS-008_20260406_164711.json, validation/IQ_EVIDENCE_LOG.md.
- [x] Author OQ protocol.
  Evidence: validation/OQ_Operational_Qualification.md.
- [x] Execute OQ protocol (technical execution complete; pending QA signatures).
  Evidence: validation/OQ_Operational_Qualification.md, validation/OQ_EVIDENCE_LOG.md.
- [x] Prepare OQ execution assets (scripts, evidence log, quickstart).
  Evidence: validation/test_scripts/, validation/OQ_EVIDENCE_LOG.md, docs/OQ_EXECUTION_QUICKSTART.md.
- [x] Author PQ protocol.
  Evidence: validation/PQ_Performance_Qualification.md.
- [x] Execute PQ protocol technical scenarios.
  Evidence: validation/PQ_Performance_Qualification.md, validation/evidence/PQ-CORE_TS-007_20260406_144757.json.
- [x] Complete PQ technical operational scenarios (handoff dry-run and incident drill simulation).
  Evidence: validation/evidence/PQ-OPS-01_TS-010_20260406_165304.json, validation/evidence/PQ-OPS-02_TS-009_20260406_165304.json.
- [ ] Add protocol deviations/CAPA log.
  Evidence: deviation tracker with closure evidence.
- [x] Prepare incident drill worksheet for manual execution.
  Evidence: docs/INCIDENT_DRILL_WORKSHEET.md.

## 4. Security, Privacy, and Data Integrity

Owner: Security and Data Protection Lead

- [x] Verify RBAC in integrated runtime path.
  Evidence: validation/evidence/OQ-SEC-01_02_TS-004_20260406_143655.json.
- [x] Verify audit trail immutability and review workflow.
  Evidence: validation/evidence/OQ-COMP-01_02_TS-005_20260406_143602.json.
- [x] Verify e-signature workflow with re-authentication controls.
  Evidence: validation/evidence/OQ-COMP-01_02_TS-005_20260406_143602.json.
- [x] Verify privacy controls for PHI/PII handling.
  Evidence: validation/evidence/OQ-PRIV-01_TS-006_20260406_143603.json.
- [x] Execute backup and restore validation.
  Evidence: validation/evidence/OQ-DR-01_02_TS-003_20260406_142152.json.

## 5. Infrastructure and Deployment

Owner: DevOps Lead

- [x] Add docker-compose.clinical.yml.
  Evidence: docker-compose.clinical.yml present.
- [x] Fix clinical image runtime command and healthcheck alignment.
  Evidence: Dockerfile.clinical and docker-entrypoint.sh updates.
- [x] Add DR/BCP procedures.
  Evidence: docs/BACKUP_PROCEDURE.md, docs/DISASTER_RECOVERY_PLAN.md, docs/BUSINESS_CONTINUITY_PLAN.md.
- [x] Add environment separation and release controls baseline.
  Evidence: docs/ENVIRONMENT_RELEASE_CONTROLS.md, validation/deployment_records/*.md.

## 6. Gate Criteria to Move from NO_GO

All mandatory items in docs/PHASE1_READINESS_CHECKLIST.md must be DONE:

- IND/CTA strategy and ethics package completed.
- CMC/GMP assay validation + release specs + QA approvals completed.
- GLP toxicology + biodistribution completed.
- DSMB/safety governance finalized.

No gate transition should occur without signed objective evidence.
