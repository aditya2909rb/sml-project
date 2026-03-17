"""
Clinical Data Integration System for Cancer Research

This module provides comprehensive integration with clinical data sources,
electronic health records (EHR), clinical trial databases, and patient
management systems to create a complete clinical research pipeline.
"""

from __future__ import annotations

import json
import csv
import requests
import pandas as pd
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from enum import Enum
import hashlib
import uuid
import io
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClinicalDataSource(Enum):
    """Types of clinical data sources."""
    EHR = "EHR"
    CLINICAL_TRIALS = "CLINICAL_TRIALS"
    CANCER_REGISTRIES = "CANCER_REGISTRIES"
    BIOMEDICAL_DATABASES = "BIOMEDICAL_DATABASES"
    IMAGING_DATA = "IMAGING_DATA"
    LAB_RESULTS = "LAB_RESULTS"


@dataclass
class PatientDemographics:
    """Patient demographic information."""
    patient_id: str
    age: int
    sex: str
    ethnicity: str
    race: str
    medical_record_number: str
    date_of_birth: str
    enrollment_date: str


@dataclass
class ClinicalDiagnosis:
    """Clinical diagnosis information."""
    diagnosis_id: str
    patient_id: str
    cancer_type: str
    cancer_subtype: str
    stage: str
    grade: str
    diagnosis_date: str
    primary_site: str
    laterality: str
    histology: str


@dataclass
class TreatmentHistory:
    """Patient treatment history."""
    treatment_id: str
    patient_id: str
    treatment_type: str  # surgery, chemotherapy, radiation, immunotherapy, targeted therapy
    treatment_line: int
    start_date: str
    end_date: Optional[str]
    response: str  # complete_response, partial_response, stable_disease, progressive_disease
    adverse_events: List[str]
    dosage: Optional[str]


@dataclass
class BiomarkerData:
    """Molecular biomarker information."""
    biomarker_id: str
    patient_id: str
    test_date: str
    test_type: str  # genomic, proteomic, transcriptomic
    gene_mutations: Dict[str, str]  # gene: mutation
    protein_expression: Dict[str, float]  # protein: expression_level
    copy_number_variations: Dict[str, int]  # gene: copy_number
    fusion_genes: List[str]
    microsatellite_status: str
    tumor_mutational_burden: float
    pd_l1_expression: float


@dataclass
class ClinicalTrialData:
    """Clinical trial participation data."""
    trial_id: str
    patient_id: str
    trial_name: str
    phase: str
    sponsor: str
    start_date: str
    end_date: Optional[str]
    arm: str
    eligibility_criteria_met: List[str]
    outcomes: Dict[str, Any]


@dataclass
class ImagingData:
    """Medical imaging data."""
    imaging_id: str
    patient_id: str
    imaging_type: str  # CT, MRI, PET, XRAY, Ultrasound
    date_performed: str
    body_part: str
    findings: Dict[str, Any]
    response_criteria: str  # RECIST, iRECIST, etc.
    tumor_measurements: List[Dict[str, float]]


@dataclass
class LabResults:
    """Laboratory test results."""
    lab_id: str
    patient_id: str
    test_date: str
    test_type: str
    results: Dict[str, Any]
    reference_range: Dict[str, Any]
    abnormal_flags: List[str]


@dataclass
class ClinicalDataRecord:
    """Complete clinical data record for a patient."""
    patient_demographics: PatientDemographics
    diagnosis: ClinicalDiagnosis
    treatment_history: List[TreatmentHistory]
    biomarkers: BiomarkerData
    trials: List[ClinicalTrialData]
    imaging: List[ImagingData]
    labs: List[LabResults]
    data_source: ClinicalDataSource
    data_quality_score: float
    last_updated: str


class ClinicalDataIntegrator:
    """Integrates multiple clinical data sources for comprehensive patient profiles."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_sources = self._initialize_data_sources()
        self.patient_cache = {}
        self.data_quality_threshold = 0.7
        
    def _initialize_data_sources(self) -> Dict[ClinicalDataSource, Dict[str, Any]]:
        """Initialize configuration for different data sources."""
        return {
            ClinicalDataSource.EHR: {
                'api_endpoint': self.config.get('ehr_api_endpoint'),
                'api_key': self.config.get('ehr_api_key'),
                'patient_mapping': self.config.get('ehr_patient_mapping', {}),
                'data_fields': ['demographics', 'diagnosis', 'treatment', 'labs']
            },
            ClinicalDataSource.CLINICAL_TRIALS: {
                'api_endpoint': self.config.get('clinical_trials_api', 'https://clinicaltrials.gov/api/v2/studies'),
                'api_key': self.config.get('clinical_trials_api_key'),
                'data_fields': ['trials', 'eligibility', 'outcomes']
            },
            ClinicalDataSource.CANCER_REGISTRIES: {
                'api_endpoint': self.config.get('cancer_registry_api'),
                'api_key': self.config.get('cancer_registry_api_key'),
                'data_fields': ['incidence', 'mortality', 'survival']
            },
            ClinicalDataSource.BIOMEDICAL_DATABASES: {
                'api_endpoints': {
                    'cbioportal': self.config.get('cbioportal_api', 'https://www.cbioportal.org/api'),
                    'tcga': self.config.get('tcga_api', 'https://api.gdc.cancer.gov'),
                    'icgc': self.config.get('icgc_api', 'https://dcc.icgc.org/api/v1')
                },
                'data_fields': ['genomics', 'transcriptomics', 'proteomics']
            },
            ClinicalDataSource.IMAGING_DATA: {
                'dicom_server': self.config.get('dicom_server'),
                'pacs_endpoint': self.config.get('pacs_endpoint'),
                'data_fields': ['images', 'measurements', 'reports']
            },
            ClinicalDataSource.LAB_RESULTS: {
                'lab_api': self.config.get('lab_api_endpoint'),
                'data_fields': ['chemistry', 'hematology', 'microbiology']
            }
        }
    
    def integrate_patient_data(self, patient_id: str) -> Optional[ClinicalDataRecord]:
        """Integrate comprehensive clinical data for a patient."""
        logger.info(f"Integrating clinical data for patient: {patient_id}")
        
        # Check cache first
        if patient_id in self.patient_cache:
            cached_record = self.patient_cache[patient_id]
            if self._is_cache_valid(cached_record):
                logger.info(f"Returning cached data for patient: {patient_id}")
                return cached_record
        
        # Collect data from all sources
        data_sources = {}
        quality_scores = {}
        
        for source_type, source_config in self.data_sources.items():
            try:
                source_data = self._fetch_from_source(source_type, source_config, patient_id)
                if source_data:
                    data_sources[source_type] = source_data
                    quality_scores[source_type] = self._calculate_data_quality(source_data)
                    logger.info(f"Successfully fetched data from {source_type.value}")
            except Exception as e:
                logger.error(f"Failed to fetch data from {source_type.value}: {e}")
                continue
        
        # Integrate data if we have data from at least one source
        if data_sources:
            integrated_record = self._integrate_data_sources(data_sources, quality_scores, patient_id)
            self.patient_cache[patient_id] = integrated_record
            return integrated_record
        else:
            logger.warning(f"No clinical data found for patient: {patient_id}")
            return None
    
    def _fetch_from_source(self, source_type: ClinicalDataSource, config: Dict[str, Any], patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch data from a specific clinical data source."""
        if source_type == ClinicalDataSource.EHR:
            return self._fetch_ehr_data(config, patient_id)
        elif source_type == ClinicalDataSource.CLINICAL_TRIALS:
            return self._fetch_clinical_trial_data(config, patient_id)
        elif source_type == ClinicalDataSource.CANCER_REGISTRIES:
            return self._fetch_cancer_registry_data(config, patient_id)
        elif source_type == ClinicalDataSource.BIOMEDICAL_DATABASES:
            return self._fetch_biomedical_data(config, patient_id)
        elif source_type == ClinicalDataSource.IMAGING_DATA:
            return self._fetch_imaging_data(config, patient_id)
        elif source_type == ClinicalDataSource.LAB_RESULTS:
            return self._fetch_lab_results(config, patient_id)
        else:
            return None
    
    def _fetch_ehr_data(self, config: Dict[str, Any], patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Electronic Health Record system."""
        try:
            api_endpoint = config.get('api_endpoint') or config.get('ehr_api_endpoint')
            if not api_endpoint:
                return None
            api_key = config.get('api_key') or config.get('ehr_api_key')
            headers = {'Authorization': f"Bearer {api_key}"} if api_key else {}
            response = requests.get(f"{api_endpoint}/patients/{patient_id}", headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"EHR data fetch failed for patient {patient_id}: {e}")
            return None
    
    def _fetch_clinical_trial_data(self, config: Dict[str, Any], patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch clinical trial participation data."""
        try:
            # Search for trials involving this patient
            params = {'query': f'patient_id:{patient_id}', 'format': 'json'}
            response = requests.get(config['api_endpoint'], params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Clinical trial data fetch failed for patient {patient_id}: {e}")
            return None
    
    def _fetch_cancer_registry_data(self, config: Dict[str, Any], patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch data from cancer registries."""
        try:
            api_endpoint = config.get('api_endpoint') or config.get('cancer_registry_api')
            if not api_endpoint:
                return None
            api_key = config.get('api_key') or config.get('cancer_registry_api_key')
            headers = {'Authorization': f"Bearer {api_key}"} if api_key else {}
            response = requests.get(f"{api_endpoint}/patients/{patient_id}", headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Cancer registry data fetch failed for patient {patient_id}: {e}")
            return None
    
    def _fetch_biomedical_data(self, config: Dict[str, Any], patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch genomic and molecular data from biomedical databases."""
        biomedical_data = {}
        
        for db_name, endpoint in config['api_endpoints'].items():
            try:
                # Search for patient data in each database
                search_params = {'patient_id': patient_id, 'format': 'json'}
                response = requests.get(f"{endpoint}/search", params=search_params, timeout=30)
                if response.status_code == 200:
                    biomedical_data[db_name] = response.json()
            except Exception as e:
                logger.error(f"Biomedical database {db_name} fetch failed for patient {patient_id}: {e}")
                continue
        
        return biomedical_data if biomedical_data else None
    
    def _fetch_imaging_data(self, config: Dict[str, Any], patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch medical imaging data."""
        try:
            # This would typically connect to a PACS system
            # For now, return mock data structure
            return {
                'images': [],
                'measurements': {},
                'reports': []
            }
        except Exception as e:
            logger.error(f"Imaging data fetch failed for patient {patient_id}: {e}")
            return None
    
    def _fetch_lab_results(self, config: Dict[str, Any], patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch laboratory test results."""
        try:
            lab_api = config.get('lab_api') or config.get('lab_api_endpoint')
            if not lab_api:
                return None
            api_key = config.get('api_key') or config.get('lab_api_key')
            headers = {'Authorization': f"Bearer {api_key}"} if api_key else {}
            response = requests.get(f"{lab_api}/patients/{patient_id}/labs", headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Lab results fetch failed for patient {patient_id}: {e}")
            return None
    
    def _calculate_data_quality(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score for a data source."""
        quality_factors = {
            'completeness': self._assess_completeness(data),
            'timeliness': self._assess_timeliness(data),
            'consistency': self._assess_consistency(data),
            'accuracy': self._assess_accuracy(data)
        }
        
        # Weighted average of quality factors
        weights = {'completeness': 0.4, 'timeliness': 0.2, 'consistency': 0.2, 'accuracy': 0.2}
        quality_score = sum(quality_factors[factor] * weights[factor] for factor in quality_factors)
        
        return quality_score
    
    def _assess_completeness(self, data: Dict[str, Any]) -> float:
        """Assess data completeness (0.0 to 1.0)."""        # Check for required fields based on data source type
        required_fields = ['patient_id', 'timestamp', 'data_type']
        present_fields = sum(1 for field in required_fields if field in data)
        completeness = present_fields / len(required_fields)
        
        # Additional completeness checks for specific data types
        if 'demographics' in data:
            demo_fields = ['age', 'sex', 'ethnicity']
            present_demo = sum(1 for field in demo_fields if field in data['demographics'])
            completeness += (present_demo / len(demo_fields)) * 0.5
        
        return min(1.0, completeness)
    
    def _assess_timeliness(self, data: Dict[str, Any]) -> float:
        """Assess data timeliness (0.0 to 1.0)."""
        if 'timestamp' not in data:
            return 0.0
        
        try:
            data_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            time_diff = datetime.now() - data_time.replace(tzinfo=None)
            
            # Score based on age of data (newer is better)
            if time_diff.days < 1:
                return 1.0
            elif time_diff.days < 7:
                return 0.8
            elif time_diff.days < 30:
                return 0.6
            elif time_diff.days < 365:
                return 0.4
            else:
                return 0.2
        except:
            return 0.0
    
    def _assess_consistency(self, data: Dict[str, Any]) -> float:
        """Assess data consistency (0.0 to 1.0)."""
        # Check for consistent data formats and values
        consistency_score = 1.0
        
        # Check for consistent date formats
        date_fields = ['diagnosis_date', 'treatment_start', 'lab_date']
        date_count = sum(1 for field in date_fields if field in data and self._is_valid_date(data.get(field, '')))
        consistency_score *= (date_count / len(date_fields)) if date_fields else 1.0
        
        # Check for consistent value ranges
        if 'age' in data:
            age = data['age']
            if not (0 <= age <= 120):
                consistency_score *= 0.5
        
        return consistency_score
    
    def _assess_accuracy(self, data: Dict[str, Any]) -> float:
        """Assess data accuracy (0.0 to 1.0)."""
        # Cross-reference data with other sources if available
        # For now, use heuristics based on data patterns
        accuracy_score = 1.0
        
        # Check for suspicious patterns
        if 'patient_id' in data and len(data['patient_id']) < 5:
            accuracy_score *= 0.5
        
        # Check for valid medical codes
        if 'diagnosis_code' in data:
            code = data['diagnosis_code']
            if not self._is_valid_diagnosis_code(code):
                accuracy_score *= 0.7
        
        return accuracy_score
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if date string is valid."""
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except:
            return False
    
    def _is_valid_diagnosis_code(self, code: str) -> bool:
        """Check if diagnosis code follows standard format."""
        # Simple validation for ICD-10 format
        if not code or len(code) < 3:
            return False
        return True
    
    def _integrate_data_sources(self, data_sources: Dict[ClinicalDataSource, Dict[str, Any]], 
                               quality_scores: Dict[ClinicalDataSource, float], 
                               patient_id: str) -> ClinicalDataRecord:
        """Integrate data from multiple sources into a unified record."""
        # Extract and merge patient demographics
        demographics = self._extract_demographics(data_sources)
        
        # Extract and merge diagnosis information
        diagnosis = self._extract_diagnosis(data_sources)
        
        # Extract treatment history
        treatment_history = self._extract_treatment_history(data_sources)
        
        # Extract biomarker data
        biomarkers = self._extract_biomarker_data(data_sources)
        
        # Extract clinical trial data
        trials = self._extract_clinical_trials(data_sources)
        
        # Extract imaging data
        imaging = self._extract_imaging_data(data_sources)
        
        # Extract lab results
        labs = self._extract_lab_results(data_sources)
        
        # Calculate overall data quality score
        overall_quality = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0.0
        
        return ClinicalDataRecord(
            patient_demographics=demographics,
            diagnosis=diagnosis,
            treatment_history=treatment_history,
            biomarkers=biomarkers,
            trials=trials,
            imaging=imaging,
            labs=labs,
            data_source=next(iter(data_sources.keys())),
            data_quality_score=overall_quality,
            last_updated=datetime.now().isoformat()
        )
    
    def _extract_demographics(self, data_sources: Dict[ClinicalDataSource, Dict[str, Any]]) -> PatientDemographics:
        """Extract patient demographic information from data sources."""
        # Priority order for demographic data
        priority_sources = [ClinicalDataSource.EHR, ClinicalDataSource.CANCER_REGISTRIES, ClinicalDataSource.CLINICAL_TRIALS]
        
        for source in priority_sources:
            if source in data_sources and 'demographics' in data_sources[source]:
                demo_data = data_sources[source]['demographics']
                return PatientDemographics(
                    patient_id=demo_data.get('patient_id', str(uuid.uuid4())),
                    age=demo_data.get('age', 0),
                    sex=demo_data.get('sex', 'Unknown'),
                    ethnicity=demo_data.get('ethnicity', 'Unknown'),
                    race=demo_data.get('race', 'Unknown'),
                    medical_record_number=demo_data.get('mrn', ''),
                    date_of_birth=demo_data.get('dob', ''),
                    enrollment_date=demo_data.get('enrollment_date', datetime.now().isoformat())
                )
        
        # Return default if no demographic data found
        return PatientDemographics(
            patient_id=str(uuid.uuid4()),
            age=0,
            sex='Unknown',
            ethnicity='Unknown',
            race='Unknown',
            medical_record_number='',
            date_of_birth='',
            enrollment_date=datetime.now().isoformat()
        )
    
    def _extract_diagnosis(self, data_sources: Dict[ClinicalDataSource, Dict[str, Any]]) -> ClinicalDiagnosis:
        """Extract clinical diagnosis information."""
        for source in [ClinicalDataSource.EHR, ClinicalDataSource.CANCER_REGISTRIES]:
            if source in data_sources and 'diagnosis' in data_sources[source]:
                diag_data = data_sources[source]['diagnosis']
                return ClinicalDiagnosis(
                    diagnosis_id=diag_data.get('diagnosis_id', str(uuid.uuid4())),
                    patient_id=diag_data.get('patient_id', ''),
                    cancer_type=diag_data.get('cancer_type', 'Unknown'),
                    cancer_subtype=diag_data.get('cancer_subtype', 'Unknown'),
                    stage=diag_data.get('stage', 'Unknown'),
                    grade=diag_data.get('grade', 'Unknown'),
                    diagnosis_date=diag_data.get('diagnosis_date', datetime.now().isoformat()),
                    primary_site=diag_data.get('primary_site', 'Unknown'),
                    laterality=diag_data.get('laterality', 'Unknown'),
                    histology=diag_data.get('histology', 'Unknown')
                )
        
        return ClinicalDiagnosis(
            diagnosis_id=str(uuid.uuid4()),
            patient_id='',
            cancer_type='Unknown',
            cancer_subtype='Unknown',
            stage='Unknown',
            grade='Unknown',
            diagnosis_date=datetime.now().isoformat(),
            primary_site='Unknown',
            laterality='Unknown',
            histology='Unknown'
        )
    
    def _extract_treatment_history(self, data_sources: Dict[ClinicalDataSource, Dict[str, Any]]) -> List[TreatmentHistory]:
        """Extract treatment history from data sources."""
        treatments = []
        
        for source in data_sources.values():
            if 'treatment_history' in source:
                for treatment_data in source['treatment_history']:
                    treatments.append(TreatmentHistory(
                        treatment_id=treatment_data.get('treatment_id', str(uuid.uuid4())),
                        patient_id=treatment_data.get('patient_id', ''),
                        treatment_type=treatment_data.get('treatment_type', 'Unknown'),
                        treatment_line=treatment_data.get('treatment_line', 1),
                        start_date=treatment_data.get('start_date', datetime.now().isoformat()),
                        end_date=treatment_data.get('end_date'),
                        response=treatment_data.get('response', 'Unknown'),
                        adverse_events=treatment_data.get('adverse_events', []),
                        dosage=treatment_data.get('dosage')
                    ))
        
        return treatments
    
    def _extract_biomarker_data(self, data_sources: Dict[ClinicalDataSource, Dict[str, Any]]) -> BiomarkerData:
        """Extract biomarker data from data sources."""
        for source in [ClinicalDataSource.BIOMEDICAL_DATABASES, ClinicalDataSource.EHR]:
            if source in data_sources and 'biomarkers' in data_sources[source]:
                bio_data = data_sources[source]['biomarkers']
                return BiomarkerData(
                    biomarker_id=bio_data.get('biomarker_id', str(uuid.uuid4())),
                    patient_id=bio_data.get('patient_id', ''),
                    test_date=bio_data.get('test_date', datetime.now().isoformat()),
                    test_type=bio_data.get('test_type', 'genomic'),
                    gene_mutations=bio_data.get('gene_mutations', {}),
                    protein_expression=bio_data.get('protein_expression', {}),
                    copy_number_variations=bio_data.get('copy_number_variations', {}),
                    fusion_genes=bio_data.get('fusion_genes', []),
                    microsatellite_status=bio_data.get('microsatellite_status', 'Unknown'),
                    tumor_mutational_burden=bio_data.get('tumor_mutational_burden', 0.0),
                    pd_l1_expression=bio_data.get('pd_l1_expression', 0.0)
                )
        
        return BiomarkerData(
            biomarker_id=str(uuid.uuid4()),
            patient_id='',
            test_date=datetime.now().isoformat(),
            test_type='genomic',
            gene_mutations={},
            protein_expression={},
            copy_number_variations={},
            fusion_genes=[],
            microsatellite_status='Unknown',
            tumor_mutational_burden=0.0,
            pd_l1_expression=0.0
        )
    
    def _extract_clinical_trials(self, data_sources: Dict[ClinicalDataSource, Dict[str, Any]]) -> List[ClinicalTrialData]:
        """Extract clinical trial participation data."""
        trials = []
        
        if ClinicalDataSource.CLINICAL_TRIALS in data_sources:
            for trial_data in data_sources[ClinicalDataSource.CLINICAL_TRIALS].get('trials', []):
                trials.append(ClinicalTrialData(
                    trial_id=trial_data.get('trial_id', str(uuid.uuid4())),
                    patient_id=trial_data.get('patient_id', ''),
                    trial_name=trial_data.get('trial_name', 'Unknown'),
                    phase=trial_data.get('phase', 'Unknown'),
                    sponsor=trial_data.get('sponsor', 'Unknown'),
                    start_date=trial_data.get('start_date', datetime.now().isoformat()),
                    end_date=trial_data.get('end_date'),
                    arm=trial_data.get('arm', 'Unknown'),
                    eligibility_criteria_met=trial_data.get('eligibility_criteria_met', []),
                    outcomes=trial_data.get('outcomes', {})
                ))
        
        return trials
    
    def _extract_imaging_data(self, data_sources: Dict[ClinicalDataSource, Dict[str, Any]]) -> List[ImagingData]:
        """Extract imaging data from data sources."""
        imaging = []
        
        if ClinicalDataSource.IMAGING_DATA in data_sources:
            for image_data in data_sources[ClinicalDataSource.IMAGING_DATA].get('images', []):
                imaging.append(ImagingData(
                    imaging_id=image_data.get('imaging_id', str(uuid.uuid4())),
                    patient_id=image_data.get('patient_id', ''),
                    imaging_type=image_data.get('imaging_type', 'Unknown'),
                    date_performed=image_data.get('date_performed', datetime.now().isoformat()),
                    body_part=image_data.get('body_part', 'Unknown'),
                    findings=image_data.get('findings', {}),
                    response_criteria=image_data.get('response_criteria', 'Unknown'),
                    tumor_measurements=image_data.get('tumor_measurements', [])
                ))
        
        return imaging
    
    def _extract_lab_results(self, data_sources: Dict[ClinicalDataSource, Dict[str, Any]]) -> List[LabResults]:
        """Extract laboratory results from data sources."""
        labs = []
        
        if ClinicalDataSource.LAB_RESULTS in data_sources:
            for lab_data in data_sources[ClinicalDataSource.LAB_RESULTS].get('results', []):
                labs.append(LabResults(
                    lab_id=lab_data.get('lab_id', str(uuid.uuid4())),
                    patient_id=lab_data.get('patient_id', ''),
                    test_date=lab_data.get('test_date', datetime.now().isoformat()),
                    test_type=lab_data.get('test_type', 'Unknown'),
                    results=lab_data.get('results', {}),
                    reference_range=lab_data.get('reference_range', {}),
                    abnormal_flags=lab_data.get('abnormal_flags', [])
                ))
        
        return labs
    
    def _is_cache_valid(self, record: ClinicalDataRecord) -> bool:
        """Check if cached clinical data is still valid."""
        try:
            last_updated = datetime.fromisoformat(record.last_updated.replace('Z', '+00:00'))
            time_diff = datetime.now() - last_updated.replace(tzinfo=None)
            # Cache is valid for 1 hour
            return time_diff.total_seconds() < 3600
        except:
            return False
    
    def export_clinical_data(self, patient_id: str, format: str = 'json') -> Optional[str]:
        """Export clinical data in specified format."""
        record = self.integrate_patient_data(patient_id)
        if not record:
            return None
        
        if format.lower() == 'json':
            return json.dumps(asdict(record), indent=2, default=str)
        elif format.lower() == 'csv':
            return self._export_to_csv(record)
        elif format.lower() == 'xml':
            return self._export_to_xml(record)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_csv(self, record: ClinicalDataRecord) -> str:
        """Export clinical data to CSV format."""
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write demographics
        writer.writerow(['Patient Demographics'])
        writer.writerow(['Field', 'Value'])
        writer.writerow(['Patient ID', record.patient_demographics.patient_id])
        writer.writerow(['Age', record.patient_demographics.age])
        writer.writerow(['Sex', record.patient_demographics.sex])
        writer.writerow(['Ethnicity', record.patient_demographics.ethnicity])
        writer.writerow(['Race', record.patient_demographics.race])
        writer.writerow([])
        
        # Write diagnosis
        writer.writerow(['Clinical Diagnosis'])
        writer.writerow(['Field', 'Value'])
        writer.writerow(['Cancer Type', record.diagnosis.cancer_type])
        writer.writerow(['Cancer Subtype', record.diagnosis.cancer_subtype])
        writer.writerow(['Stage', record.diagnosis.stage])
        writer.writerow(['Grade', record.diagnosis.grade])
        writer.writerow([])
        
        return output.getvalue()
    
    def _export_to_xml(self, record: ClinicalDataRecord) -> str:
        """Export clinical data to XML format."""
        import xml.etree.ElementTree as ET
        
        root = ET.Element("ClinicalDataRecord")
        
        # Add demographics
        demo_elem = ET.SubElement(root, "PatientDemographics")
        ET.SubElement(demo_elem, "PatientID").text = record.patient_demographics.patient_id
        ET.SubElement(demo_elem, "Age").text = str(record.patient_demographics.age)
        ET.SubElement(demo_elem, "Sex").text = record.patient_demographics.sex
        ET.SubElement(demo_elem, "Ethnicity").text = record.patient_demographics.ethnicity
        
        # Add diagnosis
        diag_elem = ET.SubElement(root, "ClinicalDiagnosis")
        ET.SubElement(diag_elem, "CancerType").text = record.diagnosis.cancer_type
        ET.SubElement(diag_elem, "CancerSubtype").text = record.diagnosis.cancer_subtype
        ET.SubElement(diag_elem, "Stage").text = record.diagnosis.stage
        ET.SubElement(diag_elem, "Grade").text = record.diagnosis.grade
        
        return ET.tostring(root, encoding='unicode')
    
    def get_data_quality_report(self, patient_id: str) -> Dict[str, Any]:
        """Generate data quality report for a patient."""
        record = self.integrate_patient_data(patient_id)
        if not record:
            return {"error": f"No data found for patient {patient_id}"}
        
        return {
            "patient_id": patient_id,
            "data_quality_score": record.data_quality_score,
            "data_sources": list(self.data_sources.keys()),
            "last_updated": record.last_updated,
            "quality_threshold": self.data_quality_threshold,
            "meets_threshold": record.data_quality_score >= self.data_quality_threshold,
            "recommendations": self._generate_quality_recommendations(record.data_quality_score)
        }
    
    def _generate_quality_recommendations(self, quality_score: float) -> List[str]:
        """Generate recommendations based on data quality score."""
        recommendations = []
        
        if quality_score < 0.5:
            recommendations.append("Data quality is very low. Consider collecting additional data sources.")
        elif quality_score < 0.7:
            recommendations.append("Data quality is moderate. Review data completeness and accuracy.")
        elif quality_score < 0.9:
            recommendations.append("Data quality is good. Minor improvements may be beneficial.")
        else:
            recommendations.append("Data quality is excellent.")
        
        return recommendations
    
    def validate_clinical_data(self, record: ClinicalDataRecord) -> Dict[str, Any]:
        """Validate clinical data for completeness and consistency."""
        validation_results = {
            "patient_id": self._validate_patient_id(record.patient_demographics.patient_id),
            "demographics": self._validate_demographics(record.patient_demographics),
            "diagnosis": self._validate_diagnosis(record.diagnosis),
            "biomarkers": self._validate_biomarkers(record.biomarkers),
            "treatment_history": self._validate_treatment_history(record.treatment_history),
            "overall_valid": True
        }
        
        # Check if any validation failed
        validation_results["overall_valid"] = all(
            result["valid"] for result in validation_results.values() 
            if isinstance(result, dict) and "valid" in result
        )
        
        return validation_results
    
    def _validate_patient_id(self, patient_id: str) -> Dict[str, Any]:
        """Validate patient ID format and uniqueness."""
        if not patient_id or len(patient_id) < 5:
            return {"valid": False, "error": "Patient ID is too short or missing"}
        return {"valid": True, "patient_id": patient_id}
    
    def _validate_demographics(self, demographics: PatientDemographics) -> Dict[str, Any]:
        """Validate patient demographic information."""
        errors = []
        
        if not demographics.age or demographics.age < 0 or demographics.age > 120:
            errors.append("Invalid age")
        
        if demographics.sex not in ['Male', 'Female', 'Other', 'Unknown']:
            errors.append("Invalid sex value")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "demographics": asdict(demographics)
        }
    
    def _validate_diagnosis(self, diagnosis: ClinicalDiagnosis) -> Dict[str, Any]:
        """Validate clinical diagnosis information."""
        errors = []
        
        if not diagnosis.cancer_type or diagnosis.cancer_type == 'Unknown':
            errors.append("Cancer type is missing or unknown")
        
        allowed_stages = {
            '0', 'I', 'IA', 'IB', 'IC',
            'II', 'IIA', 'IIB', 'IIC',
            'III', 'IIIA', 'IIIB', 'IIIC',
            'IV', 'IVA', 'IVB', 'IVC',
            'Unknown'
        }
        if diagnosis.stage not in allowed_stages:
            errors.append("Invalid cancer stage")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "diagnosis": asdict(diagnosis)
        }
    
    def _validate_biomarkers(self, biomarkers: BiomarkerData) -> Dict[str, Any]:
        """Validate biomarker data."""
        errors = []
        
        if biomarkers.tumor_mutational_burden < 0:
            errors.append("Invalid tumor mutational burden")
        
        if not (0.0 <= biomarkers.pd_l1_expression <= 100.0):
            errors.append("Invalid PD-L1 expression value")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "biomarkers": asdict(biomarkers)
        }
    
    def _validate_treatment_history(self, treatment_history: List[TreatmentHistory]) -> Dict[str, Any]:
        """Validate treatment history."""
        errors = []
        
        for i, treatment in enumerate(treatment_history):
            if not treatment.treatment_type or treatment.treatment_type == 'Unknown':
                errors.append(f"Invalid treatment type for treatment {i+1}")
            
            if treatment.response not in ['complete_response', 'partial_response', 'stable_disease', 'progressive_disease', 'Unknown']:
                errors.append(f"Invalid response for treatment {i+1}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "treatment_count": len(treatment_history)
        }