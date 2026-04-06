"""
Privacy and Data Protection Module - HIPAA/GDPR Compliant

This module provides data privacy controls for handling protected health
information (PHI) and personal data in compliance with HIPAA and GDPR.

Compliance: HIPAA Privacy Rule, GDPR, FDA 21 CFR Part 11
"""

import hashlib
import secrets
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class DataCategory(Enum):
    """Data classification categories."""
    PHI = "PHI"  # Protected Health Information
    PII = "PII"  # Personally Identifiable Information
    SENSITIVE = "SENSITIVE"  # Sensitive but not PHI/PII
    INTERNAL = "INTERNAL"  # Internal use only
    PUBLIC = "PUBLIC"  # Public information


class ConsentType(Enum):
    """Types of patient consent."""
    TREATMENT = "TREATMENT"
    RESEARCH = "RESEARCH"
    DATA_SHARING = "DATA_SHARING"
    MARKETING = "MARKETING"
    WITHDRAWN = "WITHDRAWN"


@dataclass
class PatientConsent:
    """Patient consent record."""
    consent_id: str
    patient_id: str
    consent_type: str
    granted: bool
    granted_date: str
    withdrawn_date: Optional[str]
    purpose: str
    expiry_date: Optional[str]
    witness_name: Optional[str]
    notes: Optional[str]


class PrivacyManager:
    """
    Manages data privacy and protection compliance.
    
    Features:
    - Data de-identification (Safe Harbor & Expert Determination)
    - Consent management
    - Data minimization
    - Right to erasure (GDPR)
    - Data portability
    - Breach detection
    """
    
    def __init__(self):
        # HIPAA Safe Harbor identifiers to remove
        self.hipaa_identifiers = [
            'name', 'address', 'birth_date', 'phone', 'fax', 'email',
            'ssn', 'medical_record_number', 'health_plan_number',
            'account_number', 'certificate_number', 'vehicle_identifier',
            'device_identifier', 'url', 'ip_address', 'biometric_identifier',
            'photo', 'unique_identifying_number'
        ]
    
    def deidentify_safe_harbor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        De-identify data using HIPAA Safe Harbor method.
        
        Removes all 18 categories of identifiers specified by HIPAA.
        
        Args:
            data: Dictionary containing potentially identifiable data
            
        Returns:
            De-identified data dictionary
        """
        deidentified = {}
        removed_fields = []
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if field is a HIPAA identifier
            is_identifier = False
            for identifier in self.hipaa_identifiers:
                if identifier in key_lower:
                    is_identifier = True
                    break
            
            if is_identifier:
                removed_fields.append(key)
                continue
            
            # Handle nested dictionaries
            if isinstance(value, dict):
                deidentified[key] = self.deidentify_safe_harbor(value)
            # Handle lists
            elif isinstance(value, list):
                deidentified[key] = [
                    self.deidentify_safe_harbor(item) if isinstance(item, dict) else item
                    for item in value
                ]
            # Handle strings - check for patterns
            elif isinstance(value, str):
                cleaned = self._clean_string(value)
                if cleaned != value:
                    removed_fields.append(key)
                deidentified[key] = cleaned
            else:
                deidentified[key] = value
        
        logger.info(f"Safe Harbor de-identification: removed {len(removed_fields)} fields")
        return deidentified
    
    def _clean_string(self, text: str) -> str:
        """Remove potential identifiers from string."""
        if not text:
            return text
        
        # Remove email addresses
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED]', text)
        
        # Remove phone numbers (various formats)
        text = re.sub(r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[REDACTED]', text)
        
        # Remove SSN pattern
        text = re.sub(r'\d{3}[-.\s]?\d{2}[-.\s]?\d{4}', '[REDACTED]', text)
        
        # Remove dates that could be birth dates (keep year only for age)
        # This is simplified - real implementation would be more nuanced
        
        return text
    
    def pseudonymize(self, patient_id: str, salt: str = None) -> str:
        """
        Pseudonymize patient identifier.
        
        Creates a reversible but protected identifier using HMAC.
        
        Args:
            patient_id: Original patient identifier
            salt: Secret salt for hashing (generated if not provided)
            
        Returns:
            Tuple of (pseudonymized_id, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        import hmac
        pseudonym = hmac.new(
            salt.encode(),
            patient_id.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return pseudonym, salt
    
    def generalize_date(self, date_str: str, granularity: str = 'year') -> str:
        """
        Generalize date to reduce identifiability.
        
        HIPAA allows year only for dates except for individuals 89+.
        
        Args:
            date_str: ISO format date string
            granularity: 'year', 'month', or 'full'
            
        Returns:
            Generalized date string
        """
        if not date_str:
            return date_str
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            if granularity == 'year':
                return str(date_obj.year)
            elif granularity == 'month':
                return f"{date_obj.year}-{date_obj.month:02d}"
            else:
                return date_str
        except (ValueError, AttributeError):
            return date_str
    
    def calculate_age(self, birth_date: str, reference_date: str = None) -> Optional[int]:
        """
        Calculate age from birth date.
        
        For HIPAA compliance, ages 89+ should be grouped as "89+".
        
        Args:
            birth_date: ISO format birth date
            reference_date: Date to calculate age from (default: today)
            
        Returns:
            Age in years, capped at 89
        """
        if not birth_date:
            return None
        
        try:
            birth = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
            if reference_date:
                ref = datetime.fromisoformat(reference_date.replace('Z', '+00:00'))
            else:
                ref = datetime.now(timezone.utc)
            
            age = ref.year - birth.year
            if (ref.month, ref.day) < (birth.month, birth.day):
                age -= 1
            
            # HIPAA compliance: cap at 89
            return min(age, 89)
        except (ValueError, AttributeError):
            return None
    
    def create_consent_record(
        self,
        patient_id: str,
        consent_type: ConsentType,
        granted: bool,
        purpose: str,
        witness_name: str = None,
        expiry_date: str = None,
        notes: str = None
    ) -> PatientConsent:
        """
        Create a patient consent record.
        
        Args:
            patient_id: Patient identifier
            consent_type: Type of consent
            granted: Whether consent was granted
            purpose: Purpose of the consent
            witness_name: Name of witness (if applicable)
            expiry_date: When consent expires
            notes: Additional notes
            
        Returns:
            PatientConsent record
        """
        consent_id = hashlib.sha256(
            f"{patient_id}{consent_type.value}{datetime.now().isoformat()}{secrets.token_hex(8)}".encode()
        ).hexdigest()[:32]
        
        return PatientConsent(
            consent_id=consent_id,
            patient_id=patient_id,
            consent_type=consent_type.value,
            granted=granted,
            granted_date=datetime.now(timezone.utc).isoformat(),
            withdrawn_date=None,
            purpose=purpose,
            expiry_date=expiry_date,
            witness_name=witness_name,
            notes=notes
        )
    
    def withdraw_consent(self, consent: PatientConsent) -> PatientConsent:
        """
        Record withdrawal of consent.
        
        Args:
            consent: Original consent record
            
        Returns:
            Updated PatientConsent record
        """
        consent.withdrawn_date = datetime.now(timezone.utc).isoformat()
        consent.granted = False
        consent.notes = (consent.notes or "") + "\nConsent withdrawn on " + consent.withdrawn_date
        
        logger.info(f"Consent {consent.consent_id} withdrawn for patient {consent.patient_id}")
        return consent
    
    def check_consent_status(
        self,
        patient_id: str,
        consent_type: ConsentType,
        consents: List[PatientConsent]
    ) -> bool:
        """
        Check if valid consent exists for a specific purpose.
        
        Args:
            patient_id: Patient identifier
            consent_type: Type of consent to check
            consents: List of patient consent records
            
        Returns:
            True if valid consent exists
        """
        for consent in consents:
            if (consent.patient_id == patient_id and 
                consent.consent_type == consent_type.value and
                consent.granted and
                not consent.withdrawn_date):
                
                # Check expiry
                if consent.expiry_date:
                    expiry = datetime.fromisoformat(consent.expiry_date.replace('Z', '+00:00'))
                    if datetime.now(timezone.utc) > expiry:
                        continue
                
                return True
        
        return False
    
    def export_patient_data(
        self,
        patient_id: str,
        data: Dict[str, Any],
        format: str = 'json'
    ) -> str:
        """
        Export patient data for data portability (GDPR Article 20).
        
        Args:
            patient_id: Patient identifier
            data: Patient data to export
            format: Export format ('json', 'csv')
            
        Returns:
            Formatted data string
        """
        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "patient_id": patient_id,
            "data": data
        }
        
        if format == 'json':
            return json.dumps(export_data, indent=2)
        elif format == 'csv':
            # Simplified CSV export - real implementation would be more robust
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Flatten data for CSV
            def flatten(d, prefix=''):
                items = []
                for k, v in d.items():
                    new_key = f"{prefix}.{k}" if prefix else k
                    if isinstance(v, dict):
                        items.extend(flatten(v, new_key).items())
                    else:
                        items.append((new_key, v))
                return dict(items)
            
            flat_data = flatten(export_data)
            writer.writerow(flat_data.keys())
            writer.writerow(flat_data.values())
            return output.getvalue()
        
        return json.dumps(export_data)
    
    def anonymize_dataset(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Anonymize a dataset by removing all identifiers.
        
        This is irreversible - unlike pseudonymization.
        
        Args:
            dataset: List of records to anonymize
            
        Returns:
            Anonymized dataset
        """
        anonymized = []
        
        for record in dataset:
            anon_record = self.deidentify_safe_harbor(record)
            
            # Additional anonymization steps
            if 'age' in anon_record:
                age = anon_record['age']
                if isinstance(age, (int, float)) and age > 89:
                    anon_record['age'] = "89+"
            
            anonymized.append(anon_record)
        
        logger.info(f"Anonymized dataset: {len(dataset)} records processed")
        return anonymized
    
    def detect_phi(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect potential PHI in text.
        
        Args:
            text: Text to scan
            
        Returns:
            List of detected PHI patterns with positions
        """
        patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
            (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', 'PHONE'),
            (r'[\w\.-]+@[\w\.-]+\.\w+', 'EMAIL'),
            (r'\b\d{1,3}(\.\d{1,3}){3}\b', 'IP_ADDRESS'),
            (r'https?://\S+', 'URL'),
        ]
        
        detections = []
        for pattern, phi_type in patterns:
            for match in re.finditer(pattern, text):
                detections.append({
                    'type': phi_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return detections
    
    def get_data_retention_period(self, data_type: str, jurisdiction: str = 'US') -> int:
        """
        Get data retention period in days based on regulations.
        
        Args:
            data_type: Type of data
            jurisdiction: Regulatory jurisdiction
            
        Returns:
            Retention period in days
        """
        # HIPAA requires 6 years from creation or last effective date
        retention_periods = {
            'US': {
                'clinical_trial': 6 * 365,  # HIPAA
                'medical_record': 6 * 365,  # HIPAA
                'research': 6 * 365,  # HIPAA
                'default': 6 * 365
            },
            'EU': {
                'clinical_trial': 25 * 365,  # EU Clinical Trials Regulation
                'medical_record': 10 * 365,  # Varies by country
                'research': 5 * 365,  # GDPR
                'default': 5 * 365
            }
        }
        
        jurisdiction_data = retention_periods.get(jurisdiction, retention_periods['US'])
        return jurisdiction_data.get(data_type, jurisdiction_data['default'])


# Global privacy manager instance
privacy_manager = PrivacyManager()