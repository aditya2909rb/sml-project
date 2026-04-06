"""
Access Control Module - HIPAA/GDPR Compliant

This module provides role-based access control (RBAC) with multi-factor
authentication for clinical-grade security.

Compliance: FDA 21 CFR Part 11, HIPAA, GDPR
"""

import json
import hashlib
import secrets
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import sqlite3
from contextlib import contextmanager
import pyotp  # For TOTP/MFA

logger = logging.getLogger(__name__)


class Role(Enum):
    """User roles with associated permissions."""
    ADMIN = "ADMIN"
    CLINICAL_RESEARCHER = "CLINICAL_RESEARCHER"
    LAB_TECHNICIAN = "LAB_TECHNICIAN"
    QA_REVIEWER = "QA_REVIEWER"
    CLINICAL_COORDINATOR = "CLINICAL_COORDINATOR"
    DATA_MANAGER = "DATA_MANAGER"
    VIEWER = "VIEWER"


class Permission(Enum):
    """System permissions."""
    # Patient Data
    PATIENT_CREATE = "PATIENT_CREATE"
    PATIENT_READ = "PATIENT_READ"
    PATIENT_UPDATE = "PATIENT_UPDATE"
    PATIENT_DELETE = "PATIENT_DELETE"
    
    # Analysis Functions
    ANALYSIS_CREATE = "ANALYSIS_CREATE"
    ANALYSIS_READ = "ANALYSIS_READ"
    ANALYSIS_APPROVE = "ANALYSIS_APPROVE"
    ANALYSIS_SIGN = "ANALYSIS_SIGN"
    
    # System Administration
    USER_MANAGE = "USER_MANAGE"
    SYSTEM_CONFIG = "SYSTEM_CONFIG"
    AUDIT_READ = "AUDIT_READ"
    BACKUP_MANAGE = "BACKUP_MANAGE"
    
    # Reports
    REPORT_CREATE = "REPORT_CREATE"
    REPORT_EXPORT = "REPORT_EXPORT"


# Role-Permission mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        Permission.PATIENT_CREATE, Permission.PATIENT_READ, Permission.PATIENT_UPDATE, Permission.PATIENT_DELETE,
        Permission.ANALYSIS_CREATE, Permission.ANALYSIS_READ, Permission.ANALYSIS_APPROVE, Permission.ANALYSIS_SIGN,
        Permission.USER_MANAGE, Permission.SYSTEM_CONFIG, Permission.AUDIT_READ, Permission.BACKUP_MANAGE,
        Permission.REPORT_CREATE, Permission.REPORT_EXPORT
    },
    Role.CLINICAL_RESEARCHER: {
        Permission.PATIENT_CREATE, Permission.PATIENT_READ, Permission.PATIENT_UPDATE,
        Permission.ANALYSIS_CREATE, Permission.ANALYSIS_READ, Permission.ANALYSIS_APPROVE, Permission.ANALYSIS_SIGN,
        Permission.AUDIT_READ,
        Permission.REPORT_CREATE, Permission.REPORT_EXPORT
    },
    Role.LAB_TECHNICIAN: {
        Permission.PATIENT_READ,
        Permission.ANALYSIS_CREATE, Permission.ANALYSIS_READ,
        Permission.REPORT_CREATE
    },
    Role.QA_REVIEWER: {
        Permission.PATIENT_READ,
        Permission.ANALYSIS_READ, Permission.ANALYSIS_APPROVE,
        Permission.AUDIT_READ,
        Permission.REPORT_CREATE, Permission.REPORT_EXPORT
    },
    Role.CLINICAL_COORDINATOR: {
        Permission.PATIENT_CREATE, Permission.PATIENT_READ, Permission.PATIENT_UPDATE,
        Permission.ANALYSIS_READ,
        Permission.REPORT_CREATE, Permission.REPORT_EXPORT
    },
    Role.DATA_MANAGER: {
        Permission.PATIENT_CREATE, Permission.PATIENT_READ, Permission.PATIENT_UPDATE,
        Permission.ANALYSIS_READ,
        Permission.AUDIT_READ,
        Permission.BACKUP_MANAGE,
        Permission.REPORT_CREATE, Permission.REPORT_EXPORT
    },
    Role.VIEWER: {
        Permission.PATIENT_READ,
        Permission.ANALYSIS_READ,
        Permission.REPORT_CREATE
    }
}


@dataclass
class User:
    """User account data."""
    user_id: str
    username: str
    full_name: str
    email: str
    role: str
    is_active: bool
    created_date: str
    last_login: Optional[str]
    mfa_enabled: bool
    failed_attempts: int
    locked_until: Optional[str]
    department: Optional[str] = None
    title: Optional[str] = None


@dataclass
class Session:
    """User session data."""
    session_id: str
    user_id: str
    username: str
    created_at: str
    expires_at: str
    ip_address: str
    user_agent: str
    is_active: bool


class AccessControlManager:
    """
    Manages access control with RBAC and MFA.
    
    Features:
    - Role-based access control
    - Multi-factor authentication (TOTP)
    - Session management
    - Account lockout
    - Password policies
    """
    
    def __init__(self, db_path: str = "access_control.db", session_timeout_minutes: int = 30):
        self.db_path = db_path
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create access control tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_date TEXT NOT NULL,
                    last_login TEXT,
                    mfa_enabled INTEGER DEFAULT 0,
                    mfa_secret TEXT,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TEXT,
                    department TEXT,
                    title TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_username 
                ON users(username)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_user 
                ON sessions(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_active 
                ON sessions(is_active)
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        return password_hash, salt
    
    def _generate_session_id(self) -> str:
        """Generate secure session ID."""
        return secrets.token_urlsafe(32)
    
    def create_user(
        self,
        user_id: str,
        username: str,
        password: str,
        full_name: str,
        email: str,
        role: Role,
        department: str = None,
        title: str = None
    ) -> Optional[User]:
        """
        Create a new user account.
        
        Password requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        # Validate password strength
        if not self._validate_password_strength(password):
            logger.warning(f"Password strength validation failed for user {username}")
            return None
        
        password_hash, salt = self._hash_password(password)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO users 
                    (user_id, username, password_hash, salt, full_name, email, role, 
                     created_date, department, title)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, username, password_hash, salt, full_name, email, role.value,
                    datetime.now(timezone.utc).isoformat(), department, title
                ))
                conn.commit()
                return self.get_user(user_id)
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to create user {username}: {e}")
                return None
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets complexity requirements."""
        if len(password) < 12:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False
        return True
    
    def authenticate(
        self,
        username: str,
        password: str,
        mfa_code: str = None,
        ip_address: str = "0.0.0.0",
        user_agent: str = "Unknown"
    ) -> Optional[Session]:
        """
        Authenticate user and create session.
        
        Args:
            username: Username
            password: Password
            mfa_code: Optional MFA code if enabled
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Session if successful, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Authentication failed: user {username} not found")
            return None
        
        columns = [desc[0] for desc in cursor.description]
        user_data = dict(zip(columns, row))
        
        # Check if account is locked
        if user_data['locked_until']:
            lock_time = datetime.fromisoformat(user_data['locked_until'])
            if datetime.now(timezone.utc) < lock_time:
                logger.warning(f"Account {username} is locked until {lock_time}")
                return None
        
        # Check if account is active
        if not user_data['is_active']:
            logger.warning(f"Account {username} is inactive")
            return None
        
        # Verify password
        password_hash, _ = self._hash_password(password, user_data['salt'])
        if password_hash != user_data['password_hash']:
            # Increment failed attempts
            self._increment_failed_attempts(user_data['user_id'])
            logger.warning(f"Authentication failed: invalid password for {username}")
            return None
        
        # Check MFA if enabled
        if user_data['mfa_enabled'] and mfa_code:
            if not self._verify_mfa(user_data['mfa_secret'], mfa_code):
                logger.warning(f"MFA verification failed for {username}")
                return None
        elif user_data['mfa_enabled'] and not mfa_code:
            logger.warning(f"MFA required but not provided for {username}")
            return None
        
        # Create session
        session_id = self._generate_session_id()
        now = datetime.now(timezone.utc)
        expires_at = now + self.session_timeout
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions 
                (session_id, user_id, username, created_at, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, user_data['user_id'], user_data['username'],
                now.isoformat(), expires_at.isoformat(), ip_address, user_agent
            ))
            
            # Update last login and reset failed attempts
            cursor.execute("""
                UPDATE users 
                SET last_login = ?, failed_attempts = 0 
                WHERE user_id = ?
            """, (now.isoformat(), user_data['user_id']))
            conn.commit()
        
        logger.info(f"User {username} authenticated successfully from {ip_address}")
        
        return Session(
            session_id=session_id,
            user_id=user_data['user_id'],
            username=user_data['username'],
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
    
    def _increment_failed_attempts(self, user_id: str, max_attempts: int = 5):
        """Increment failed login attempts and lock account if threshold reached."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET failed_attempts = failed_attempts + 1 
                WHERE user_id = ?
            """, (user_id,))
            
            if max_attempts > 0:
                cursor.execute("""
                    UPDATE users 
                    SET locked_until = ?
                    WHERE user_id = ? AND failed_attempts >= ?
                """, (
                    (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
                    user_id, max_attempts
                ))
            conn.commit()
    
    def _verify_mfa(self, secret: str, code: str) -> bool:
        """Verify TOTP MFA code."""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)
        except Exception as e:
            logger.error(f"MFA verification error: {e}")
            return False
    
    def enable_mfa(self, user_id: str) -> Optional[str]:
        """
        Enable MFA for a user.
        
        Returns:
            Provisioning URI for QR code generation
        """
        secret = pyotp.random_base32()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET mfa_enabled = 1, mfa_secret = ? 
                WHERE user_id = ?
            """, (secret, user_id))
            conn.commit()
        
        user = self.get_user(user_id)
        if user:
            totp = pyotp.TOTP(secret)
            return totp.provisioning_uri(user.email, issuer_name="OncoSML")
        return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
        
        if not row:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        data = dict(zip(columns, row))
        
        return User(
            user_id=data['user_id'],
            username=data['username'],
            full_name=data['full_name'],
            email=data['email'],
            role=data['role'],
            is_active=bool(data['is_active']),
            created_date=data['created_date'],
            last_login=data['last_login'],
            mfa_enabled=bool(data['mfa_enabled']),
            failed_attempts=data['failed_attempts'],
            locked_until=data['locked_until'],
            department=data.get('department'),
            title=data.get('title')
        )
    
    def validate_session(self, session_id: str) -> Optional[Session]:
        """Validate and refresh session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE session_id = ? AND is_active = 1
            """, (session_id,))
            row = cursor.fetchone()
        
        if not row:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        session_data = dict(zip(columns, row))
        
        # Check if session is expired
        expires_at = datetime.fromisoformat(session_data['expires_at'])
        if datetime.now(timezone.utc) > expires_at:
            self.invalidate_session(session_id)
            return None
        
        # Refresh session expiry
        new_expires = datetime.now(timezone.utc) + self.session_timeout
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions SET expires_at = ? WHERE session_id = ?
        """, (new_expires.isoformat(), session_id))
        conn.commit()
        
        return Session(
            session_id=session_data['session_id'],
            user_id=session_data['user_id'],
            username=session_data['username'],
            created_at=session_data['created_at'],
            expires_at=new_expires.isoformat(),
            ip_address=session_data['ip_address'],
            user_agent=session_data['user_agent'],
            is_active=True
        )
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate/logout session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions SET is_active = 0 WHERE session_id = ?
            """, (session_id,))
            conn.commit()
        return True
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission."""
        user = self.get_user(user_id)
        if not user:
            return False
        
        role = Role(user.role)
        allowed_permissions = ROLE_PERMISSIONS.get(role, set())
        return permission in allowed_permissions
    
    def has_access(self, user_id: str, resource_type: str, resource_id: str, action: str) -> bool:
        """
        Check if user has access to perform action on resource.
        
        This is a more granular access check that can consider resource ownership,
        patient assignment, etc.
        """
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return False
        
        # Map action to permission
        action_permission_map = {
            'create': f"{resource_type.upper()}_CREATE",
            'read': f"{resource_type.upper()}_READ",
            'update': f"{resource_type.upper()}_UPDATE",
            'delete': f"{resource_type.upper()}_DELETE",
            'approve': f"{resource_type.upper()}_APPROVE",
            'sign': f"{resource_type.upper()}_SIGN"
        }
        
        permission_str = action_permission_map.get(action.lower())
        if not permission_str:
            return False
        
        try:
            permission = Permission(permission_str)
        except ValueError:
            return False
        
        return self.check_permission(user_id, permission)
    
    def list_users(self, active_only: bool = True) -> List[User]:
        """List all users."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if active_only:
                cursor.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY username")
            else:
                cursor.execute("SELECT * FROM users ORDER BY username")
            
            columns = [desc[0] for desc in cursor.description]
            return [
                User(
                    user_id=data['user_id'],
                    username=data['username'],
                    full_name=data['full_name'],
                    email=data['email'],
                    role=data['role'],
                    is_active=bool(data['is_active']),
                    created_date=data['created_date'],
                    last_login=data['last_login'],
                    mfa_enabled=bool(data['mfa_enabled']),
                    failed_attempts=data['failed_attempts'],
                    locked_until=data['locked_until'],
                    department=data.get('department'),
                    title=data.get('title')
                )
                for data in (dict(zip(columns, row)) for row in cursor.fetchall())
            ]
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET is_active = 0 WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            return True
    
    def update_user_role(self, user_id: str, new_role: Role) -> bool:
        """Update user role."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET role = ? WHERE user_id = ?
            """, (new_role.value, user_id))
            conn.commit()
            return True


# Global access control instance
access_control = AccessControlManager()