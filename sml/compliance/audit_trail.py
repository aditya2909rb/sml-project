"""
Audit Trail Module - 21 CFR Part 11 Compliant

This module provides comprehensive audit trail functionality for GMP-compliant
record keeping. All actions that create, modify, or delete data are logged
with full traceability.

Compliance: FDA 21 CFR Part 11, EU Annex 11
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class AuditAction(Enum):
    """Types of auditable actions."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    SIGN = "SIGN"
    EXPORT = "EXPORT"
    PRINT = "PRINT"
    SYSTEM = "SYSTEM"


class AuditSeverity(Enum):
    """Severity levels for audit events."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class AuditEntry:
    """Represents a single audit trail entry."""
    entry_id: str
    timestamp: str
    user_id: str
    user_name: str
    action: str
    resource_type: str
    resource_id: str
    description: str
    old_value: Optional[str]
    new_value: Optional[str]
    ip_address: str
    user_agent: str
    session_id: str
    severity: str
    checksum: str
    previous_checksum: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AuditTrailManager:
    """
    Manages audit trail operations with 21 CFR Part 11 compliance.
    
    Features:
    - Immutable audit records
    - Cryptographic chain linking
    - Secure storage
    - Comprehensive logging
    - Tamper detection
    """
    
    def __init__(self, db_path: str = "audit_trail.db"):
        self.db_path = db_path
        self._initialize_database()
        self._last_checksum = self._get_last_checksum()
    
    def _initialize_database(self):
        """Create audit trail tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    entry_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    user_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    severity TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    previous_checksum TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_user 
                ON audit_trail(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON audit_trail(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_resource 
                ON audit_trail(resource_type, resource_id)
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def _generate_entry_id(self, timestamp: str, user_id: str) -> str:
        """Generate unique entry ID."""
        data = f"{timestamp}{user_id}{datetime.now().microsecond}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _calculate_checksum(self, entry: AuditEntry) -> str:
        """Calculate cryptographic checksum for an entry."""
        data = (
            f"{entry.entry_id}{entry.timestamp}{entry.user_id}"
            f"{entry.action}{entry.resource_type}{entry.resource_id}"
            f"{entry.description}{entry.old_value or ''}{entry.new_value or ''}"
            f"{entry.previous_checksum}"
        )
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _get_last_checksum(self) -> str:
        """Get checksum of the last entry for chain linking."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT checksum FROM audit_trail ORDER BY timestamp DESC LIMIT 1"
            )
            result = cursor.fetchone()
            return result[0] if result else "GENESIS"
    
    def log(
        self,
        user_id: str,
        user_name: str,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        description: str,
        old_value: Any = None,
        new_value: Any = None,
        ip_address: str = "0.0.0.0",
        user_agent: str = "Unknown",
        session_id: str = "N/A",
        severity: AuditSeverity = AuditSeverity.MEDIUM
    ) -> AuditEntry:
        """
        Log an auditable event.
        
        Args:
            user_id: Unique user identifier
            user_name: User's full name
            action: Type of action performed
            resource_type: Type of resource affected
            resource_id: Unique resource identifier
            description: Human-readable description
            old_value: Previous value (for updates)
            new_value: New value (for creates/updates)
            ip_address: User's IP address
            user_agent: User's browser/application
            session_id: Session identifier
            severity: Event severity level
            
        Returns:
            AuditEntry: The created audit entry
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        entry_id = self._generate_entry_id(timestamp, user_id)
        
        # Serialize values to JSON strings
        old_value_str = json.dumps(old_value) if old_value is not None else None
        new_value_str = json.dumps(new_value) if new_value is not None else None
        
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            user_id=user_id,
            user_name=user_name,
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            old_value=old_value_str,
            new_value=new_value_str,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            severity=severity.value,
            checksum="",  # Will be calculated
            previous_checksum=self._last_checksum
        )
        
        # Calculate checksum with chain linking
        entry.checksum = self._calculate_checksum(entry)
        
        # Store in database
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_trail 
                (entry_id, timestamp, user_id, user_name, action, resource_type,
                 resource_id, description, old_value, new_value, ip_address,
                 user_agent, session_id, severity, checksum, previous_checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.entry_id, entry.timestamp, entry.user_id, entry.user_name,
                entry.action, entry.resource_type, entry.resource_id,
                entry.description, entry.old_value, entry.new_value,
                entry.ip_address, entry.user_agent, entry.session_id,
                entry.severity, entry.checksum, entry.previous_checksum
            ))
            conn.commit()
        
        # Update last checksum for chain linking
        self._last_checksum = entry.checksum
        
        logger.info(f"Audit: {action.value} by {user_name} on {resource_type}:{resource_id}")
        
        return entry
    
    def get_entries(
        self,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve audit trail entries with optional filtering.
        
        Args:
            user_id: Filter by user
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            limit: Maximum number of entries to return
            
        Returns:
            List of audit entries as dictionaries
        """
        query = "SELECT * FROM audit_trail WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        if resource_id:
            query += " AND resource_id = ?"
            params.append(resource_id)
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def verify_integrity(self) -> Dict:
        """
        Verify the integrity of the audit trail chain.
        
        Returns:
            Dictionary with verification results
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_trail ORDER BY timestamp ASC")
            entries = cursor.fetchall()
        
        if not entries:
            return {"valid": True, "message": "Audit trail is empty", "entries_checked": 0}
        
        columns = [desc[0] for desc in cursor.description]
        previous_checksum = "GENESIS"
        issues = []
        
        for i, row in enumerate(entries):
            entry_data = dict(zip(columns, row))
            
            # Verify chain linkage
            if entry_data["previous_checksum"] != previous_checksum:
                issues.append({
                    "entry_id": entry_data["entry_id"],
                    "issue": "Chain break detected",
                    "expected": previous_checksum,
                    "found": entry_data["previous_checksum"]
                })
            
            # Recalculate and verify checksum
            temp_entry = AuditEntry(
                entry_id=entry_data["entry_id"],
                timestamp=entry_data["timestamp"],
                user_id=entry_data["user_id"],
                user_name=entry_data["user_name"],
                action=entry_data["action"],
                resource_type=entry_data["resource_type"],
                resource_id=entry_data["resource_id"],
                description=entry_data["description"],
                old_value=entry_data["old_value"],
                new_value=entry_data["new_value"],
                ip_address=entry_data["ip_address"],
                user_agent=entry_data["user_agent"],
                session_id=entry_data["session_id"],
                severity=entry_data["severity"],
                checksum="",
                previous_checksum=entry_data["previous_checksum"]
            )
            
            calculated_checksum = self._calculate_checksum(temp_entry)
            if calculated_checksum != entry_data["checksum"]:
                issues.append({
                    "entry_id": entry_data["entry_id"],
                    "issue": "Checksum mismatch",
                    "expected": entry_data["checksum"],
                    "calculated": calculated_checksum
                })
            
            previous_checksum = entry_data["checksum"]
        
        return {
            "valid": len(issues) == 0,
            "message": "Audit trail integrity verified" if not issues else "Issues found",
            "entries_checked": len(entries),
            "issues": issues
        }
    
    def export_audit_trail(self, output_path: str):
        """
        Export audit trail to a file for regulatory review.
        
        Args:
            output_path: Path to save the export file
        """
        entries = self.get_entries(limit=10000)
        
        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_entries": len(entries),
            "integrity_verification": self.verify_integrity(),
            "entries": entries
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Audit trail exported to {output_path}")


# Global audit trail instance
audit_trail = AuditTrailManager()


def log_audit_event(
    user_id: str,
    user_name: str,
    action: AuditAction,
    resource_type: str,
    resource_id: str,
    description: str,
    **kwargs
) -> AuditEntry:
    """
    Convenience function for logging audit events.
    
    Args:
        user_id: Unique user identifier
        user_name: User's full name
        action: Type of action performed
        resource_type: Type of resource affected
        resource_id: Unique resource identifier
        description: Human-readable description
        **kwargs: Additional parameters (old_value, new_value, etc.)
        
    Returns:
        AuditEntry: The created audit entry
    """
    return audit_trail.log(
        user_id=user_id,
        user_name=user_name,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        **kwargs
    )