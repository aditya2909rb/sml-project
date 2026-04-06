"""
GMP Compliance Package - 21 CFR Part 11

This package provides GMP-compliant functionality for clinical deployment:
- Audit trails with cryptographic chain linking
- Electronic signatures
- Access control
- Data integrity controls

Compliance: FDA 21 CFR Part 11, EU Annex 11, HIPAA, GDPR
"""

from sml.compliance.audit_trail import (
    AuditTrailManager,
    AuditEntry,
    AuditAction,
    AuditSeverity,
    audit_trail,
    log_audit_event
)

__all__ = [
    "AuditTrailManager",
    "AuditEntry",
    "AuditAction",
    "AuditSeverity",
    "audit_trail",
    "log_audit_event"
]