#!/usr/bin/env python3
"""
Integration tests for the clinical cancer research system.

This module tests the integration between clinical data integration,
enhanced biological modeling, and safety validation components.
"""

import unittest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sml.config import load_config
from sml.clinical_data_integration import (
    ClinicalDataIntegrator,
    PatientDemographics,
    ClinicalDiagnosis,
    BiomarkerData,
    ClinicalDataRecord
)
from sml.enhanced_biological_model import (
    EnhancedBiologicalModel,
    GenomicProfile,
    ImmuneProfile,
    CancerType,
    ImmuneCellType
)
from sml.safety_validator import (
    EnhancedSafetyValidator,
    SafetyLevel,
    ValidationResult
)


class TestClinicalIntegration(unittest.TestCase):
    """Test clinical data integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'ehr_api_endpoint': 'https://api.ehr.example.com',
            'ehr_api_key': 'test_key',
            'clinical_trials_api': 'https://clinicaltrials.gov/api',
            'cancer_registry_api': 'https://cancerregistry.example.com',
            'cbioportal_api': 'https://www.cbioportal.org/api',
            'tcga_api': 'https://api.gdc.cancer.gov',
            'icgc_api': 'https://dcc.icgc.org/api/v1'
        }
        self.integrator = ClinicalDataIntegrator(self.config)
    
    def test_patient_demographics_creation(self):
        """Test patient demographics data structure."""
        demographics = PatientDemographics(
            patient_id="test_patient_001",
            age=55,
            sex="Female",
            ethnicity="Caucasian",
            race="White",
            medical_record_number="MRN123456",
            date_of_birth="1969-01-15",
            enrollment_date="2024-01-01"
        )
        
        self.assertEqual(demographics.patient_id, "test_patient_001")
        self.assertEqual(demographics.age, 55)
        self.assertEqual(demographics.sex, "Female")
        self.assertEqual(demographics.ethnicity, "Caucasian")
    
    def test_clinical_diagnosis_creation(self):
        """Test clinical diagnosis data structure."""
        diagnosis = ClinicalDiagnosis(
            diagnosis_id="dx_001",
            patient_id="test_patient_001",
            cancer_type="Non-Small Cell Lung Cancer",
            cancer_subtype="Adenocarcinoma",
            stage="IIIA",
            grade="2",
            diagnosis_date="2024-01-15",
            primary_site="Lung",
            laterality="Right",
            histology="Adenocarcinoma"
        )
        
        self.assertEqual(diagnosis.cancer_type, "Non-Small Cell Lung Cancer")
        self.assertEqual(diagnosis.stage, "IIIA")
        self.assertEqual(diagnosis.grade, "2")
    
    def test_biomarker_data_creation(self):
        """Test biomarker data structure."""
        biomarkers = BiomarkerData(
            biomarker_id="bio_001",
            patient_id="test_patient_001",
            test_date="2024-01-20",
            test_type="genomic",
            gene_mutations={"KRAS": "G12C", "TP53": "R175H"},
            protein_expression={"PD-L1": 45.0},
            copy_number_variations={"EGFR": 3},
            fusion_genes=["EML4-ALK"],
            microsatellite_status="MSS",
            tumor_mutational_burden=12.5,
            pd_l1_expression=45.0
        )
        
        self.assertEqual(biomarkers.gene_mutations["KRAS"], "G12C")
        self.assertEqual(biomarkers.tumor_mutational_burden, 12.5)
        self.assertEqual(biomarkers.pd_l1_expression, 45.0)
    
    @patch('sml.clinical_data_integration.requests.get')
    def test_ehr_data_fetching(self, mock_get):
        """Test EHR data fetching functionality."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'patient_id': 'test_patient_001',
            'demographics': {
                'age': 55,
                'sex': 'Female',
                'ethnicity': 'Caucasian'
            },
            'diagnosis': {
                'cancer_type': 'Lung Cancer',
                'stage': 'IIIA'
            }
        }
        mock_get.return_value = mock_response
        
        # Test data fetching
        result = self.integrator._fetch_ehr_data(
            self.config, 'test_patient_001'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['patient_id'], 'test_patient_001')
        self.assertEqual(result['demographics']['age'], 55)
    
    @patch('sml.clinical_data_integration.requests.get')
    def test_ehr_data_fetching_failure(self, mock_get):
        """Test EHR data fetching failure handling."""
        # Mock failed API response
        mock_get.side_effect = Exception("API Error")
        
        # Test error handling
        result = self.integrator._fetch_ehr_data(
            self.config, 'test_patient_001'
        )
        
        self.assertIsNone(result)
    
    def test_data_quality_calculation(self):
        """Test data quality assessment."""
        test_data = {
            'patient_id': 'test_patient_001',
            'timestamp': '2024-01-01T10:00:00Z',
            'data_type': 'clinical',
            'demographics': {
                'age': 55,
                'sex': 'Female',
                'ethnicity': 'Caucasian'
            }
        }
        
        quality_score = self.integrator._calculate_data_quality(test_data)
        
        # Quality score should be between 0 and 1
        self.assertGreaterEqual(quality_score, 0.0)
        self.assertLessEqual(quality_score, 1.0)
        # Should be relatively high for complete data
        self.assertGreater(quality_score, 0.5)
    
    def test_data_validation(self):
        """Test clinical data validation."""
        # Create test clinical data record
        demographics = PatientDemographics(
            patient_id="test_patient_001",
            age=55,
            sex="Female",
            ethnicity="Caucasian",
            race="White",
            medical_record_number="MRN123456",
            date_of_birth="1969-01-15",
            enrollment_date="2024-01-01"
        )
        
        diagnosis = ClinicalDiagnosis(
            diagnosis_id="dx_001",
            patient_id="test_patient_001",
            cancer_type="Non-Small Cell Lung Cancer",
            cancer_subtype="Adenocarcinoma",
            stage="IIIA",
            grade="2",
            diagnosis_date="2024-01-15",
            primary_site="Lung",
            laterality="Right",
            histology="Adenocarcinoma"
        )
        
        biomarkers = BiomarkerData(
            biomarker_id="bio_001",
            patient_id="test_patient_001",
            test_date="2024-01-20",
            test_type="genomic",
            gene_mutations={"KRAS": "G12C"},
            protein_expression={},
            copy_number_variations={},
            fusion_genes=[],
            microsatellite_status="MSS",
            tumor_mutational_burden=12.5,
            pd_l1_expression=45.0
        )
        
        record = ClinicalDataRecord(
            patient_demographics=demographics,
            diagnosis=diagnosis,
            treatment_history=[],
            biomarkers=biomarkers,
            trials=[],
            imaging=[],
            labs=[],
            data_source=None,
            data_quality_score=0.8,
            last_updated="2024-01-01T10:00:00Z"
        )
        
        # Test validation
        validation_results = self.integrator.validate_clinical_data(record)
        
        self.assertTrue(validation_results['overall_valid'])
        self.assertTrue(validation_results['patient_id']['valid'])
        self.assertTrue(validation_results['demographics']['valid'])
        self.assertTrue(validation_results['diagnosis']['valid'])
        self.assertTrue(validation_results['biomarkers']['valid'])


class TestEnhancedBiologicalModel(unittest.TestCase):
    """Test enhanced biological modeling functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model = EnhancedBiologicalModel()
    
    def test_genomic_profile_creation(self):
        """Test genomic profile data structure."""
        genomic_profile = GenomicProfile(
            sample_id="sample_001",
            cancer_type=CancerType.LUNG,
            mutation_count=150,
            tumor_mutational_burden=5.0,
            microsatellite_status="MSS",
            gene_mutations={"KRAS": "G12C", "TP53": "R175H"},
            copy_number_variations={"EGFR": 3},
            fusion_genes=["EML4-ALK"],
            hla_alleles=["HLA-A*02:01"],
            pd_l1_expression=45.0
        )
        
        self.assertEqual(genomic_profile.sample_id, "sample_001")
        self.assertEqual(genomic_profile.cancer_type, CancerType.LUNG)
        self.assertEqual(genomic_profile.mutation_count, 150)
        self.assertEqual(genomic_profile.tumor_mutational_burden, 5.0)
    
    def test_immune_profile_creation(self):
        """Test immune profile data structure."""
        immune_profile = ImmuneProfile(
            patient_id="patient_001",
            t_cell_infiltration=0.65,
            immune_cell_counts={
                ImmuneCellType.CD8_TCELL: 500,
                ImmuneCellType.CD4_TCELL: 300,
                ImmuneCellType.DENDRITIC_CELL: 50
            },
            cytokine_levels={
                'IL-2': 0.5,
                'IFN-gamma': 0.8,
                'IL-10': 0.2
            },
            tcr_diversity=0.7,
            immune_exhaustion=0.3
        )
        
        self.assertEqual(immune_profile.patient_id, "patient_001")
        self.assertEqual(immune_profile.t_cell_infiltration, 0.65)
        self.assertEqual(immune_profile.tcr_diversity, 0.7)
        self.assertEqual(immune_profile.immune_exhaustion, 0.3)
    
    def test_genomic_analysis(self):
        """Test genomic data analysis."""
        genomic_data = {
            'sample_id': 'test_sample',
            'cancer_type': 'lung_adenocarcinoma',
            'mutations': {
                'KRAS': 'G12C',
                'TP53': 'R175H',
                'EGFR': 'L858R'
            },
            'sequenced_bases': 30000000,
            'hla_alleles': ['HLA-A*02:01', 'HLA-A*03:01']
        }
        
        profile = self.model.genomic_analyzer.analyze_genomic_profile(genomic_data)
        
        self.assertEqual(profile.sample_id, 'test_sample')
        self.assertEqual(profile.cancer_type, CancerType.LUNG)
        self.assertGreater(profile.mutation_count, 0)
        self.assertGreater(profile.tumor_mutational_burden, 0)
        self.assertIn('KRAS', profile.gene_mutations)
    
    def test_immune_response_simulation(self):
        """Test immune response simulation."""
        immune_profile = ImmuneProfile(
            patient_id="test_patient",
            t_cell_infiltration=0.6,
            immune_cell_counts={ImmuneCellType.DENDRITIC_CELL: 100},
            cytokine_levels={'IL-2': 0.5, 'IFN-gamma': 0.8},
            tcr_diversity=0.7,
            immune_exhaustion=0.3
        )
        
        # Simulate immune response
        response = self.model.immune_model.simulate_immune_response(
            vaccine_dose=100.0,
            patient_profile=immune_profile,
            duration_days=30
        )
        
        self.assertIn('time', response)
        self.assertIn('t_cells', response)
        self.assertIn('dendritic_cells', response)
        self.assertIn('tumor_cells', response)
        self.assertIn('cytokines', response)
        
        # Check that simulation ran for correct duration
        self.assertEqual(len(response['time']), 30)
        self.assertEqual(len(response['t_cells']), 30)
    
    def test_treatment_response_prediction(self):
        """Test treatment response prediction."""
        immune_profile = ImmuneProfile(
            patient_id="test_patient",
            t_cell_infiltration=0.7,
            immune_cell_counts={ImmuneCellType.DENDRITIC_CELL: 200},
            cytokine_levels={'IL-2': 0.8, 'IFN-gamma': 0.9},
            tcr_diversity=0.8,
            immune_exhaustion=0.2
        )
        
        treatment_params = {'vaccine_potency': 1.2}
        
        prediction = self.model.immune_model.predict_treatment_response(
            immune_profile, treatment_params
        )
        
        self.assertIn('response_score', prediction)
        self.assertIn('tumor_regression_probability', prediction)
        self.assertIn('duration_of_response', prediction)
        
        # Response score should be between 0 and 1
        self.assertGreaterEqual(prediction['response_score'], 0.0)
        self.assertLessEqual(prediction['response_score'], 1.0)
        
        # Higher infiltration should lead to better response
        self.assertGreater(prediction['response_score'], 0.5)
    
    def test_patient_sample_analysis(self):
        """Test complete patient sample analysis."""
        genomic_data = {
            'sample_id': 'test_sample',
            'cancer_type': 'lung_adenocarcinoma',
            'mutations': {'KRAS': 'G12C', 'TP53': 'R175H'},
            'sequenced_bases': 30000000,
            'hla_alleles': ['HLA-A*02:01']
        }
        
        immune_data = {
            'patient_id': 'test_patient',
            't_cell_infiltration': 0.65,
            'immune_cell_counts': {},
            'cytokine_levels': {'IL-2': 0.5, 'IFN-gamma': 0.8},
            'tcr_diversity': 0.7,
            'immune_exhaustion': 0.3
        }
        
        result = self.model.analyze_patient_sample(genomic_data, immune_data)
        
        self.assertIn('genomic_profile', result)
        self.assertIn('immune_profile', result)
        self.assertIn('response_prediction', result)
        self.assertIn('treatment_plan', result)
        self.assertIn('analysis_timestamp', result)
        
        # Check that response prediction was generated
        self.assertIn('response_score', result['response_prediction'])
        
        # Check that treatment plan was generated
        self.assertIn('treatment_strategy', result['treatment_plan'])
        self.assertIn('recommended_dose', result['treatment_plan'])


class TestSafetyValidator(unittest.TestCase):
    """Test safety validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = EnhancedSafetyValidator()
    
    def test_dna_sequence_validation(self):
        """Test DNA sequence safety validation."""
        # Test valid sequence
        valid_sequence = "ATCGATCGATCG" * 100  # 1200 bases
        results = self.validator.validate_dna_sequence(valid_sequence, "test_sample")
        
        # Should have no critical issues for valid sequence
        critical_issues = [r for r in results if r.level == SafetyLevel.CRITICAL]
        self.assertEqual(len(critical_issues), 0)
        
        # Test invalid sequence (too short)
        short_sequence = "ATCG" * 10  # 40 bases
        results = self.validator.validate_dna_sequence(short_sequence, "test_sample")
        
        critical_issues = [r for r in results if r.level == SafetyLevel.CRITICAL]
        self.assertGreater(len(critical_issues), 0)
        self.assertIn("too short", critical_issues[0].message)
    
    def test_neoantigen_validation(self):
        """Test neoantigen safety validation."""
        # Test valid neoantigen
        valid_neoantigen = "SIINFEKL"  # 8 amino acids
        results = self.validator.validate_neoantigen(valid_neoantigen, {})
        
        # Should have no critical issues for valid neoantigen
        critical_issues = [r for r in results if r.level == SafetyLevel.CRITICAL]
        self.assertEqual(len(critical_issues), 0)
        
        # Test invalid neoantigen (too short)
        short_neoantigen = "SIIN"  # 4 amino acids
        results = self.validator.validate_neoantigen(short_neoantigen, {})
        
        critical_issues = [r for r in results if r.level == SafetyLevel.CRITICAL]
        self.assertGreater(len(critical_issues), 0)
        self.assertIn("too short", critical_issues[0].message)
    
    def test_mrna_sequence_validation(self):
        """Test mRNA sequence safety validation."""
        # Test valid mRNA sequence
        valid_sequence = "AUGCGAUC" * 200  # 1600 bases
        construct_info = {
            'sequence': valid_sequence,
            'length': 1600,
            'stability_score': 0.6,
            'immunogenicity_score': 0.4
        }
        
        results = self.validator.validate_mrna_sequence(valid_sequence, construct_info)
        
        # Should have no critical issues for valid sequence
        critical_issues = [r for r in results if r.level == SafetyLevel.CRITICAL]
        self.assertEqual(len(critical_issues), 0)
    
    def test_vaccine_construct_validation(self):
        """Test complete vaccine construct validation."""
        construct_info = {
            'length': 5000,
            'stability_score': 0.6,
            'immunogenicity_score': 0.4,
            '5_utr': True,
            'kozak': True,
            'coding_sequence': True,
            '3_utr': True,
            'poly_a': True,
            'dose_recommendation': 100
        }
        
        results = self.validator.validate_vaccine_construct(construct_info)
        
        # Should have no critical issues for valid construct
        critical_issues = [r for r in results if r.level == SafetyLevel.CRITICAL]
        self.assertEqual(len(critical_issues), 0)
        
        # Test construct with missing elements
        incomplete_construct = construct_info.copy()
        incomplete_construct['poly_a'] = False
        
        results = self.validator.validate_vaccine_construct(incomplete_construct)
        
        critical_issues = [r for r in results if r.level == SafetyLevel.CRITICAL]
        self.assertGreater(len(critical_issues), 0)
        self.assertIn("Missing required", critical_issues[0].message)
    
    def test_complete_pipeline_validation(self):
        """Test complete pipeline validation."""
        dna_sequence = "ATCGATCGATCG" * 100  # 1200 bases
        neoantigens = ["SIINFEKL", "GILGFVFTL"]
        mrna_construct = {
            "sequence": "AUGCGAUC" * 400,  # 3200 bases
            "length": 3200,
            "stability_score": 0.6,
            "immunogenicity_score": 0.4,
            "5_utr": True,
            "kozak": True,
            "coding_sequence": True,
            "3_utr": True,
            "poly_a": True,
            "dose_recommendation": 120,
        }
        
        validation_results = self.validator.validate_complete_pipeline(
            dna_sequence, neoantigens, mrna_construct
        )
        
        # Should have results for all validation categories
        self.assertIn('dna_validation', validation_results)
        self.assertIn('neoantigen_validation', validation_results)
        self.assertIn('mrna_validation', validation_results)
        self.assertIn('construct_validation', validation_results)
        
        # Generate safety report
        safety_report = self.validator.generate_safety_report(validation_results)
        
        self.assertIn('summary', safety_report)
        self.assertIn('detailed_results', safety_report)
        self.assertIn('recommendations', safety_report)
        
        summary = safety_report['summary']
        self.assertIn('total_checks', summary)
        self.assertIn('critical_issues', summary)
        self.assertIn('warnings', summary)
        self.assertIn('passed_checks', summary)
        self.assertIn('overall_status', summary)
    
    def test_safety_report_generation(self):
        """Test safety report generation."""
        # Create validation results with known issues
        validation_results = {
            'dna_validation': [
                ValidationResult(SafetyLevel.CRITICAL, "Critical issue"),
                ValidationResult(SafetyLevel.WARNING, "Warning issue")
            ],
            'neoantigen_validation': [
                ValidationResult(SafetyLevel.PASS, "Passed check")
            ],
            'mrna_validation': [],
            'construct_validation': [
                ValidationResult(SafetyLevel.CRITICAL, "Another critical issue")
            ]
        }
        
        safety_report = self.validator.generate_safety_report(validation_results)
        
        summary = safety_report['summary']
        
        # Should count issues correctly
        self.assertEqual(summary['total_checks'], 4)
        self.assertEqual(summary['critical_issues'], 2)
        self.assertEqual(summary['warnings'], 1)
        self.assertEqual(summary['passed_checks'], 1)
        
        # Overall status should be CRITICAL due to critical issues
        self.assertEqual(summary['overall_status'], 'CRITICAL')


class TestEndToEndIntegration(unittest.TestCase):
    """Test end-to-end integration of all clinical components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = load_config()
        self.validator = EnhancedSafetyValidator()
        self.model = EnhancedBiologicalModel()
    
    def test_full_clinical_workflow(self):
        """Test complete clinical workflow from data integration to safety validation."""
        # 1. Create sample patient data
        patient_id = "test_patient_e2e"
        
        # 2. Create sample genomic and immune data for modeling
        genomic_data = {
            'sample_id': patient_id,
            'cancer_type': 'lung_adenocarcinoma',
            'mutations': {'KRAS': 'G12C', 'TP53': 'R175H'},
            'sequenced_bases': 30000000,
            'hla_alleles': ['HLA-A*02:01', 'HLA-A*03:01']
        }
        
        immune_data = {
            'patient_id': patient_id,
            't_cell_infiltration': 0.65,
            'immune_cell_counts': {},
            'cytokine_levels': {'IL-2': 0.5, 'IFN-gamma': 0.8},
            'tcr_diversity': 0.7,
            'immune_exhaustion': 0.3
        }
        
        # 3. Run biological analysis
        analysis_result = self.model.analyze_patient_sample(genomic_data, immune_data)
        
        # Verify analysis completed successfully
        self.assertIn('genomic_profile', analysis_result)
        self.assertIn('immune_profile', analysis_result)
        self.assertIn('response_prediction', analysis_result)
        self.assertIn('treatment_plan', analysis_result)
        
        # 4. Extract treatment plan details for safety validation
        treatment_plan = analysis_result['treatment_plan']
        
        # 5. Create synthetic sequences for safety validation
        dna_sequence = "ATCGATCGATCG" * 100  # 1200 bases
        neoantigens = ["SIINFEKL", "GILGFVFTL", "KRAS_G12C"]
        mrna_construct = {
            "sequence": "AUGCGAUC" * 400,  # 3200 bases
            "length": 3200,
            "stability_score": 0.6,
            "immunogenicity_score": 0.4,
            "5_utr": True,
            "kozak": True,
            "coding_sequence": True,
            "3_utr": True,
            "poly_a": True,
            "dose_recommendation": 120,
        }
        
        # 6. Run safety validation
        validation_results = self.validator.validate_complete_pipeline(
            dna_sequence, neoantigens, mrna_construct
        )
        
        # 7. Generate safety report
        safety_report = self.validator.generate_safety_report(validation_results)
        
        # Verify safety validation completed
        self.assertIn('summary', safety_report)
        self.assertIn('detailed_results', safety_report)
        
        summary = safety_report['summary']
        self.assertIn('total_checks', summary)
        self.assertIn('critical_issues', summary)
        self.assertIn('warnings', summary)
        self.assertIn('passed_checks', summary)
        self.assertIn('overall_status', summary)
        
        # 8. Verify integration points
        # The biological model should provide data that can be validated by safety system
        response_prediction = analysis_result['response_prediction']
        self.assertIn('response_score', response_prediction)
        self.assertGreaterEqual(response_prediction['response_score'], 0.0)
        self.assertLessEqual(response_prediction['response_score'], 1.0)
        
        # The treatment plan should contain actionable information
        self.assertIn('treatment_strategy', treatment_plan)
        self.assertIn('recommended_dose', treatment_plan)
        self.assertIn('dosing_schedule', treatment_plan)
        self.assertIn('route_of_administration', treatment_plan)
    
    def test_error_handling_integration(self):
        """Test error handling across integrated components."""
        # Test with invalid data
        invalid_genomic_data = {
            'sample_id': 'invalid_sample',
            'cancer_type': 'invalid_cancer',
            'mutations': {},
            'sequenced_bases': 0,  # Invalid
            'hla_alleles': []
        }
        
        invalid_immune_data = {
            'patient_id': 'invalid_patient',
            't_cell_infiltration': -1.0,  # Invalid (negative)
            'immune_cell_counts': {},
            'cytokine_levels': {},
            'tcr_diversity': 1.5,  # Invalid (greater than 1)
            'immune_exhaustion': -0.5  # Invalid (negative)
        }
        
        # Biological model should handle invalid data gracefully
        try:
            result = self.model.analyze_patient_sample(invalid_genomic_data, invalid_immune_data)
            # Should still return a result, possibly with warnings
            self.assertIn('genomic_profile', result)
            self.assertIn('immune_profile', result)
        except Exception as e:
            # If an exception occurs, it should be handled gracefully
            self.assertIsInstance(e, (ValueError, TypeError))
        
        # Safety validator should handle invalid sequences
        invalid_sequence = "INVALID_SEQUENCE"  # Invalid DNA bases
        results = self.validator.validate_dna_sequence(invalid_sequence, "test_sample")
        
        # Should generate appropriate validation errors
        critical_issues = [r for r in results if r.level == SafetyLevel.CRITICAL]
        self.assertGreater(len(critical_issues), 0)
        self.assertIn("Invalid DNA bases", critical_issues[0].message)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)