# OQ Execution Quickstart

Date: 2026-04-06

## 1. Start Service (Terminal 1)

Use the project virtual environment Python executable.

PowerShell:

"g:/ai new model/.venv/Scripts/python.exe" main.py run-service --sleep-seconds 300 --host 127.0.0.1 --port 8787

## 2. Run OQ Evidence Scripts (Terminal 2)

Endpoint checks:

"g:/ai new model/.venv/Scripts/python.exe" validation/test_scripts/TS-001_Service_Endpoints.py --base-url http://127.0.0.1:8787 --output-dir validation/evidence

Pipeline functional check:

"g:/ai new model/.venv/Scripts/python.exe" validation/test_scripts/TS-002_Patient_Pipeline_Output.py --python-exe "g:/ai new model/.venv/Scripts/python.exe" --output-dir validation/evidence

Backup/restore smoke check:

"g:/ai new model/.venv/Scripts/python.exe" validation/test_scripts/TS-003_Backup_Restore_Smoke.py --source-dir outputs --output-dir validation/evidence

## 3. Record Results

- Copy generated evidence file paths into validation/OQ_EVIDENCE_LOG.md.
- Mark corresponding OQ test entries in validation/OQ_Operational_Qualification.md.
- Open deviations and CAPA entries for any failed checks.

## 4. Signoff

- Validation executor signs test execution records.
- QA reviewer signs evidence log and OQ summary.
- Approver signs OQ protocol conclusion.
