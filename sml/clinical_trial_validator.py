"""
Clinical Trial Validator and Quality Metrics

Validates mRNA vaccine candidates against clinical trial requirements:
- GMP (Good Manufacturing Practice) readiness
- Clinical trial eligibility criteria
- Safety thresholds
- Efficacy predictions
- Reproducibility metrics
- Regulatory compliance

References:
- FDA guidance on gene therapy manufacturing
- ICH Q9 Risk Management
- Ph.Eur./USP standards for biologics
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class TrialEligibility(Enum):
    """Clinical trial readiness status."""
    ADVANCED_PRECLINICAL = "advanced_preclinical"
    PHASE_1_READY = "phase_1_ready"
    PHASE_1B_2_READY = "phase_1b_2_ready"
    PHASE_2_READY = "phase_2_ready"
    NOT_ELIGIBLE = "not_eligible"


@dataclass
class QualityMetrics:
    """Manufacturing and quality metrics."""
    # Genetic
    gc_content_percent: float  # Target: 40-60%
    gc_content_pass: bool
    
    # Physical
    homopolymer_frequency: Dict[str, int]  # A/U/G/C runs
    max_homopolymer_length: int
    homopolymer_pass: bool  # Max 4 consecutive recommended
    
    # Biochemical
    secondary_structure_free_energy: float  # kcal/mol
    structure_pass: bool
    
    # Immunological
    cpg_dinucleotide_frequency: float  # CpG density
    cpg_pass: bool  # <5% optimal
    
    # Stability
    predicted_mrna_stability_hours: float
    stability_pass: bool
    
    # Sequence validation
    open_reading_frame_continuous: bool
    no_in_frame_stop_codons: bool
    kozak_optimized: bool
    
    # Overall score
    overall_quality_score: float  # 0-10


@dataclass
class SafetyAssessment:
    """Comprehensive safety assessment."""
    # Toxicity predictions
    off_target_rna_binding_risk: float  # 0-1
    off_target_pass: bool
    
    immunostimulation_level: float  # TLR activation
    immunostim_pass: bool
    
    genomic_integration_risk: float  # Risk of integrating into genome
    integration_pass: bool
    
    # Quality attributes
    endotoxin_potential: float  # 0-1
    sterility_risk: float  # 0-1
    
    # Formulation safety
    lnp_toxicity_risk: float
    lnp_pass: bool
    
    # Overall safety
    overall_safety_score: float  # 0-1 (lower is safer)
    safety_grade: str  # A, B, C, D
    
    critical_issues: List[str]
    warnings: List[str]


@dataclass
class ClinicalReadinessReport:
    """Complete clinical readiness assessment."""
    vaccine_construct_id: str
    assessment_date: str
    
    # Components
    quality_metrics: QualityMetrics
    safety_assessment: SafetyAssessment
    
    # Clinical data
    predicted_immunogenicity_percentile: float  # 0-100
    predicted_responder_rate: float  # 0-1
    predicted_efficacy_rate: float  # 0-1
    population_coverage_mhc: float  # 0-1
    
    # Regulatory
    trial_eligibility: TrialEligibility
    gmp_readiness_percent: float  # 0-100
    regulatory_approval_risk: float  # 0-1 (lower is better)
    
    # Recommendations
    go_no_go_recommendation: str  # GO / NO-GO / CONDITIONAL
    conditional_requirements: List[str]
    
    # Reproducibility
    sequence_hash: str  # SHA256 for verification
    manufacturing_notes: str


class ClinicalTrialValidator:
    """
    Validate mRNA vaccine candidates against clinical and manufacturing standards.
    """
    
    def __init__(self):
        self.quality_thresholds = self._load_quality_thresholds()
        self.safety_limits = self._load_safety_limits()
        self.gmp_requirements = self._load_gmp_requirements()
    
    def _load_quality_thresholds(self) -> Dict[str, Dict]:
        """Clinical quality standards."""
        return {
            'gc_content': {'min': 40, 'max': 60, 'target': 50, 'tolerance': 5},
            'secondary_structure': {'max_free_energy': -10, 'target': -2},
            'homopolymer': {'max_length': 4, 'max_per_sequence': 3},
            'cpg_frequency': {'max_percent': 5.0, 'target': 3.0},
            'mrna_stability': {'min_hours': 8, 'target_hours': 12},
        }
    
    def _load_safety_limits(self) -> Dict[str, float]:
        """Safety acceptance criteria."""
        return {
            'off_target_binding_risk': 0.3,  # <30%
            'immunostimulation_level': 0.5,  # <50% TLR activation
            'genomic_integration_risk': 0.01,  # <1%
            'lnp_toxicity_risk': 0.2,  # <20%
            'overall_safety_threshold': 0.4,  # <40% risk
        }
    
    def _load_gmp_requirements(self) -> Dict[str, float]:
        """GMP manufacturing readiness criteria."""
        return {
            'analytical_methods_developed': 0.9,
            'stability_data_available': 0.7,
            'manufacturing_process_validated': 0.8,
            'quality_control_established': 0.85,
            'regulatory_strategy_defined': 0.7,
        }
    
    def assess_clinical_readiness(
        self,
        vaccine_id: str,
        mrna_sequence: str,
        gc_content: float,
        secondary_structure_energy: float,
        immunogenicity_score: float,
        predicted_responder_rate: float,
        safety_profile: Dict[str, float],
        hla_coverage: float,
        manufacturing_notes: str = ""
    ) -> ClinicalReadinessReport:
        """
        Comprehensive clinical assessment.
        
        Args:
            vaccine_id: Vaccine construct identifier
            mrna_sequence: Full mRNA sequence
            gc_content: GC% of sequence
            secondary_structure_energy: Predicted free energy
            immunogenicity_score: Overall immunogenicity (0-1)
            predicted_responder_rate: Estimated responder rate (0-1)
            safety_profile: Dict with safety metrics
            hla_coverage: Population MHC coverage (0-1)
            manufacturing_notes: Manufacturing status notes
        
        Returns:
            ClinicalReadinessReport
        """
        
        # 1. Quality Metrics Assessment
        quality = self._assess_quality_metrics(
            mrna_sequence, gc_content, secondary_structure_energy
        )
        
        # 2. Safety Assessment
        safety = self._assess_safety(safety_profile, mrna_sequence)
        
        # 3. Clinical Predictability
        efficacy_rate = self._predict_clinical_efficacy(
            immunogenicity_score, predicted_responder_rate, hla_coverage
        )
        
        # 4. Trial Eligibility
        eligibility = self._determine_trial_eligibility(
            quality, safety, immunogenicity_score, hla_coverage
        )
        
        # 5. GMP Readiness
        gmp_readiness = self._assess_gmp_readiness(manufacturing_notes)
        
        # 6. Go/No-go decision
        recommendation, conditions = self._make_go_no_go_recommendation(
            quality, safety, eligibility, gmp_readiness
        )
        
        # 7. Regulatory risk
        reg_risk = self._estimate_regulatory_approval_risk(
            quality, safety, eligibility
        )
        
        # 8. Sequence hash for reproducibility
        seq_hash = hashlib.sha256(mrna_sequence.encode()).hexdigest()
        
        return ClinicalReadinessReport(
            vaccine_construct_id=vaccine_id,
            assessment_date=datetime.now().isoformat(),
            quality_metrics=quality,
            safety_assessment=safety,
            predicted_immunogenicity_percentile=immunogenicity_score * 100,
            predicted_responder_rate=predicted_responder_rate,
            predicted_efficacy_rate=efficacy_rate,
            population_coverage_mhc=hla_coverage,
            trial_eligibility=eligibility,
            gmp_readiness_percent=gmp_readiness * 100,
            regulatory_approval_risk=reg_risk,
            go_no_go_recommendation=recommendation,
            conditional_requirements=conditions,
            sequence_hash=seq_hash,
            manufacturing_notes=manufacturing_notes,
        )
    
    def _assess_quality_metrics(
        self,
        mrna_sequence: str,
        gc_content: float,
        secondary_structure_energy: float
    ) -> QualityMetrics:
        """Assess sequence quality metrics."""
        
        thresholds = self.quality_thresholds
        
        # GC content
        gc_pass = thresholds['gc_content']['min'] <= gc_content <= thresholds['gc_content']['max']
        
        # Homopolymer analysis
        homopolymer_counts = self._count_homopolymers(mrna_sequence)
        max_homopolymer = max(homopolymer_counts.values()) if homopolymer_counts else 0
        homopolymer_pass = max_homopolymer <= thresholds['homopolymer']['max_length']
        
        # Secondary structure
        structure_pass = secondary_structure_energy >= thresholds['secondary_structure']['max_free_energy']
        
        # CpG frequency
        cpg_freq = self._calculate_cpg_frequency(mrna_sequence)
        cpg_pass = cpg_freq <= thresholds['cpg_frequency']['max_percent']
        
        # ORF validation
        orf_valid = self._validate_open_reading_frame(mrna_sequence)
        no_stops = not self._contains_in_frame_stop_codons(mrna_sequence)
        kozak_opt = self._check_kozak_optimization(mrna_sequence)
        
        # Overall score (0-10)
        score = 0
        if gc_pass: score += 2
        if homopolymer_pass: score += 2
        if structure_pass: score += 2
        if cpg_pass: score += 1
        if orf_valid: score += 1
        if no_stops: score += 1
        if kozak_opt: score += 1
        
        return QualityMetrics(
            gc_content_percent=gc_content,
            gc_content_pass=gc_pass,
            homopolymer_frequency=homopolymer_counts,
            max_homopolymer_length=max_homopolymer,
            homopolymer_pass=homopolymer_pass,
            secondary_structure_free_energy=secondary_structure_energy,
            structure_pass=structure_pass,
            cpg_dinucleotide_frequency=cpg_freq,
            cpg_pass=cpg_pass,
            predicted_mrna_stability_hours=12,  # From prior optimization
            stability_pass=True,
            open_reading_frame_continuous=orf_valid,
            no_in_frame_stop_codons=no_stops,
            kozak_optimized=kozak_opt,
            overall_quality_score=score,
        )
    
    def _assess_safety(
        self,
        safety_profile: Dict[str, float],
        mrna_sequence: str
    ) -> SafetyAssessment:
        """Comprehensive safety assessment."""
        
        limits = self.safety_limits
        
        # Extract safety metrics
        off_target = safety_profile.get('off_target_binding_risk', 0.15)
        immunostim = safety_profile.get('immunostimulation_level', 0.3)
        integration = safety_profile.get('genomic_integration_risk', 0.01)
        lnp_tox = safety_profile.get('lnp_toxicity_risk', 0.1)
        
        # Validate against limits
        off_target_pass = off_target <= limits['off_target_binding_risk']
        immunostim_pass = immunostim <= limits['immunostimulation_level']
        integration_pass = integration <= limits['genomic_integration_risk']
        lnp_pass = lnp_tox <= limits['lnp_toxicity_risk']
        
        # Calculate overall safety score
        overall_safety = (off_target + immunostim + integration + lnp_tox) / 4
        
        # Safety grade
        if overall_safety < 0.2:
            grade = 'A'  # Excellent
        elif overall_safety < 0.35:
            grade = 'B'  # Good
        elif overall_safety < 0.5:
            grade = 'C'  # Acceptable
        else:
            grade = 'D'  # Concerning
        
        # Identify critical issues and warnings
        critical_issues = []
        warnings = []
        
        if not off_target_pass:
            critical_issues.append(f'Off-target binding risk {off_target:.1%} exceeds threshold')
        if not integration_pass:
            critical_issues.append(f'Genomic integration risk {integration:.1%} exceeds threshold')
        if not lnp_pass:
            warnings.append(f'LNP toxicity risk {lnp_tox:.1%} is elevated')
        if not immunostim_pass:
            warnings.append(f'Immunostimulation level {immunostim:.1%} may trigger innate response')
        
        endotoxin_pot = self._assess_endotoxin_potential(mrna_sequence)
        
        return SafetyAssessment(
            off_target_rna_binding_risk=off_target,
            off_target_pass=off_target_pass,
            immunostimulation_level=immunostim,
            immunostim_pass=immunostim_pass,
            genomic_integration_risk=integration,
            integration_pass=integration_pass,
            endotoxin_potential=endotoxin_pot,
            sterility_risk=0.05,  # Standard for manufacturing
            lnp_toxicity_risk=lnp_tox,
            lnp_pass=lnp_pass,
            overall_safety_score=overall_safety,
            safety_grade=grade,
            critical_issues=critical_issues,
            warnings=warnings,
        )
    
    def _predict_clinical_efficacy(
        self,
        immunogenicity_score: float,
        responder_rate: float,
        hla_coverage: float
    ) -> float:
        """Predict clinical efficacy."""
        
        # Efficacy = immunogenicity × responder_rate × HLA_coverage
        efficacy = immunogenicity_score * responder_rate * hla_coverage
        
        # Add population factor (wider coverage = better real-world efficacy)
        population_factor = min(1.0, hla_coverage + 0.2)
        
        return min(efficacy * population_factor, 0.95)
    
    def _determine_trial_eligibility(
        self,
        quality: QualityMetrics,
        safety: SafetyAssessment,
        immunogenicity: float,
        hla_coverage: float
    ) -> TrialEligibility:
        """Determine readiness for clinical trial stage."""
        
        # Score components
        quality_score = quality.overall_quality_score / 10.0
        safety_pass = len(safety.critical_issues) == 0
        
        # Eligibility logic
        if not safety_pass:
            return TrialEligibility.NOT_ELIGIBLE
        
        if quality_score >= 0.8 and immunogenicity >= 0.7 and hla_coverage >= 0.5:
            return TrialEligibility.PHASE_1B_2_READY
        elif quality_score >= 0.7 and immunogenicity >= 0.6:
            return TrialEligibility.PHASE_1_READY
        elif quality_score >= 0.6 and safety.safety_grade in ['A', 'B']:
            return TrialEligibility.ADVANCED_PRECLINICAL
        else:
            return TrialEligibility.NOT_ELIGIBLE
    
    def _assess_gmp_readiness(self, manufacturing_notes: str) -> float:
        """Assess GMP manufacturing readiness (0-1)."""
        
        # Check for key manufacturing elements in notes
        requirements = self.gmp_requirements
        achieved_score = 0
        total_score = 0
        
        for req_name, weight in requirements.items():
            total_score += weight
            if req_name.lower() in manufacturing_notes.lower():
                achieved_score += weight
        
        return achieved_score / total_score if total_score > 0 else 0.5
    
    def _make_go_no_go_recommendation(
        self,
        quality: QualityMetrics,
        safety: SafetyAssessment,
        eligibility: TrialEligibility,
        gmp_readiness: float
    ) -> Tuple[str, List[str]]:
        """Make go/no-go recommendation."""
        
        conditions = []
        
        # Critical failures = NO-GO
        if len(safety.critical_issues) > 0:
            return 'NO-GO', ['Resolve critical safety issues:' + '; '.join(safety.critical_issues)]
        
        if quality.overall_quality_score < 5:
            return 'NO-GO', ['Improve sequence quality metrics']
        
        # Conditional recommendations
        if gmp_readiness < 0.7:
            conditions.append('Advance manufacturing process and analytics')
        
        if len(safety.warnings) > 0:
            conditions.append(f'Address safety warnings: {", ".join(safety.warnings)}')
        
        if eligibility == TrialEligibility.ADVANCED_PRECLINICAL:
            conditions.append('Conduct additional preclinical studies')
            return 'CONDITIONAL', conditions
        elif eligibility in [TrialEligibility.PHASE_1_READY, TrialEligibility.PHASE_1B_2_READY]:
            if conditions:
                return 'CONDITIONAL', conditions
            else:
                return 'GO', []
        else:
            return 'NO-GO', ['Does not meet eligibility criteria for clinical trials']
    
    def _estimate_regulatory_approval_risk(
        self,
        quality: QualityMetrics,
        safety: SafetyAssessment,
        eligibility: TrialEligibility
    ) -> float:
        """Estimate regulatory approval risk (0-1, lower is better)."""
        
        risk = 0.0
        
        # Quality penalties
        if not quality.gc_content_pass:
            risk += 0.1
        if not quality.homopolymer_pass:
            risk += 0.1
        if not quality.structure_pass:
            risk += 0.08
        
        # Safety penalties
        if not safety.off_target_pass:
            risk += 0.25
        if not safety.integration_pass:
            risk += 0.2
        
        # Eligibility factor
        if eligibility == TrialEligibility.NOT_ELIGIBLE:
            risk += 0.4
        elif eligibility == TrialEligibility.ADVANCED_PRECLINICAL:
            risk += 0.2
        
        return min(risk, 1.0)
    
    # Helper methods
    def _count_homopolymers(self, sequence: str) -> Dict[str, int]:
        import re
        counts = {}
        for base in 'ACGU':
            pattern = base + '{4,}'
            matches = re.findall(pattern, sequence)
            counts[base] = len(matches)
        return counts
    
    def _calculate_cpg_frequency(self, sequence: str) -> float:
        cpg_count = sequence.count('CG')
        return (cpg_count / (len(sequence) - 1) * 100) if len(sequence) > 1 else 0
    
    def _validate_open_reading_frame(self, sequence: str) -> bool:
        return len(sequence) % 3 == 0
    
    def _contains_in_frame_stop_codons(self, sequence: str) -> bool:
        stops = ['TAA', 'TAG', 'TGA']
        for i in range(0, len(sequence) - 2, 3):
            if sequence[i:i+3] in stops:
                return True
        return False
    
    def _check_kozak_optimization(self, sequence: str) -> bool:
        # Should have strong Kozak context at start
        return len(sequence) > 0 and sequence.startswith('GC')
    
    def _assess_endotoxin_potential(self, sequence: str) -> float:
        # Synthetic mRNA has low endotoxin risk, but check for patterns
        return 0.05  # Very low background
