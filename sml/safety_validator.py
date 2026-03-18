"""
Safety and Validation System for Cancer Vaccine AI

This module provides comprehensive safety checks, validation rules, and
quality assurance for the AI system that designs mRNA cancer vaccines.
It ensures patient safety, regulatory compliance, and scientific validity.
"""

from __future__ import annotations

import re
import hashlib
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety validation levels."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
    PASS = "PASS"


class ValidationResult:
    """Result of a safety validation check."""
    
    def __init__(self, level: SafetyLevel, message: str, details: Optional[Dict[str, Any]] = None):
        self.level = level
        self.message = message
        self.details = details or {}
        self.timestamp = None
    
    def __str__(self):
        return f"[{self.level.value}] {self.message}"


class EnhancedSafetyValidator:
    """Enhanced comprehensive safety and validation system for clinical cancer vaccine AI."""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.safety_checks = self._load_safety_checks()
        self.regulatory_guidelines = self._load_regulatory_guidelines()
        self.clinical_safety_rules = self._load_clinical_safety_rules()
        self.ethical_guidelines = self._load_ethical_guidelines()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for different components."""
        return {
            'dna_sequence': {
                'min_length': 100,
                'max_length': 100000000,
                'allowed_bases': set('ACGTN'),
                'max_n_percentage': 0.05,
                'min_gc_content': 0.2,
                'max_gc_content': 0.8
            },
            'neoantigen': {
                'min_length': 8,
                'max_length': 15,
                'allowed_amino_acids': set('ACDEFGHIKLMNPQRSTVWY'),
                'max_hydrophobicity': 3.0,
                'min_stability_score': 0.3
            },
            'mrna_sequence': {
                'min_length': 100,
                'max_length': 10000,
                'allowed_bases': set('ACGU'),
                'min_gc_content': 0.3,
                'max_gc_content': 0.7,
                'max_repeated_motifs': 3,
                'max_self_complementarity': 0.1
            },
            'vaccine_construct': {
                'max_total_length': 50000,
                'min_stability_score': 0.4,
                'max_immunogenicity_score': 0.8,
                'required_elements': ['5_utr', 'kozak', 'coding_sequence', '3_utr', 'poly_a']
            }
        }
    
    def _load_safety_checks(self) -> Dict[str, Any]:
        """Load safety check configurations."""
        return {
            'oncogenic_sequences': [
                'KRAS', 'BRAF', 'MYC', 'EGFR', 'PIK3CA', 'AKT1', 'NRAS', 'HRAS',
                'TP53', 'BRCA1', 'BRCA2', 'VHL', 'APC', 'CTNNB1'
            ],
            'autoimmune_risks': [
                'MYH9', 'GAD65', 'INS', 'HBA1', 'HBB', 'TPM3', 'ACTA1'
            ],
            'toxic_sequences': [
                'RTA', 'ETA', 'DTA', 'PE', 'DT', 'TT', 'CT'
            ],
            'pathogen_sequences': [
                'HIV', 'HCV', 'HBV', 'EBV', 'CMV', 'HPV', 'HTLV', 'HTL'
            ]
        }
    
    def _load_regulatory_guidelines(self) -> Dict[str, Any]:
        """Load regulatory guidelines and limits."""
        return {
            'fda_guidelines': {
                'max_dose': 1000,  # micrograms
                'min_purity': 0.95,
                'max_endotoxin': 5.0,  # EU/mg
                'storage_temperature': -80,
                'shelf_life_days': 365
            },
            'ema_guidelines': {
                'max_dose': 800,
                'min_purity': 0.90,
                'max_endotoxin': 10.0,
                'storage_temperature': -70,
                'shelf_life_days': 300
            }
        }
    
    def validate_dna_sequence(self, sequence: str, sample_id: str) -> List[ValidationResult]:
        """Validate DNA sequence quality and safety."""
        results = []
        
        # Basic format validation
        sequence_upper = sequence.upper().strip()

        # Check base composition first so invalid alphabet issues are prioritized.
        allowed_bases = self.validation_rules['dna_sequence']['allowed_bases']
        invalid_bases = set(sequence_upper) - allowed_bases
        if invalid_bases:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Invalid DNA bases found: {invalid_bases}",
                {'invalid_bases': list(invalid_bases), 'allowed_bases': list(allowed_bases)}
            ))
        
        # Check length
        if len(sequence_upper) < self.validation_rules['dna_sequence']['min_length']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"DNA sequence too short: {len(sequence_upper)} < {self.validation_rules['dna_sequence']['min_length']}",
                {'length': len(sequence_upper), 'min_length': self.validation_rules['dna_sequence']['min_length']}
            ))
        
        if len(sequence_upper) > self.validation_rules['dna_sequence']['max_length']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"DNA sequence too long: {len(sequence_upper)} > {self.validation_rules['dna_sequence']['max_length']}",
                {'length': len(sequence_upper), 'max_length': self.validation_rules['dna_sequence']['max_length']}
            ))
        
        # Check N content
        n_count = sequence_upper.count('N')
        n_percentage = n_count / len(sequence_upper)
        if n_percentage > self.validation_rules['dna_sequence']['max_n_percentage']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"Too many ambiguous bases (N): {n_percentage:.2%} > {self.validation_rules['dna_sequence']['max_n_percentage']:.2%}",
                {'n_percentage': n_percentage, 'max_n_percentage': self.validation_rules['dna_sequence']['max_n_percentage']}
            ))
        
        # Check GC content
        gc_count = sequence_upper.count('G') + sequence_upper.count('C')
        gc_content = gc_count / len(sequence_upper)
        
        if gc_content < self.validation_rules['dna_sequence']['min_gc_content']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"GC content too low: {gc_content:.2%} < {self.validation_rules['dna_sequence']['min_gc_content']:.2%}",
                {'gc_content': gc_content, 'min_gc_content': self.validation_rules['dna_sequence']['min_gc_content']}
            ))
        
        if gc_content > self.validation_rules['dna_sequence']['max_gc_content']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"GC content too high: {gc_content:.2%} > {self.validation_rules['dna_sequence']['max_gc_content']:.2%}",
                {'gc_content': gc_content, 'max_gc_content': self.validation_rules['dna_sequence']['max_gc_content']}
            ))
        
        # Check for repetitive sequences
        repetitive_score = self._calculate_repetitive_score(sequence_upper)
        if repetitive_score > 0.3:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"High repetitive sequence content: {repetitive_score:.2%}",
                {'repetitive_score': repetitive_score}
            ))
        
        # Check for homopolymers
        homopolymer_score = self._calculate_homopolymer_score(sequence_upper)
        if homopolymer_score > 0.1:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"High homopolymer content: {homopolymer_score:.2%}",
                {'homopolymer_score': homopolymer_score}
            ))
        
        return results
    
    def validate_neoantigen(self, neoantigen: str, mutation_info: Dict[str, Any]) -> List[ValidationResult]:
        """Validate neoantigen safety and quality."""
        results = []
        
        # Basic validation
        if len(neoantigen) < self.validation_rules['neoantigen']['min_length']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Neoantigen too short: {len(neoantigen)} < {self.validation_rules['neoantigen']['min_length']}",
                {'length': len(neoantigen), 'min_length': self.validation_rules['neoantigen']['min_length']}
            ))
        
        if len(neoantigen) > self.validation_rules['neoantigen']['max_length']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Neoantigen too long: {len(neoantigen)} > {self.validation_rules['neoantigen']['max_length']}",
                {'length': len(neoantigen), 'max_length': self.validation_rules['neoantigen']['max_length']}
            ))

        # --- Stricter biological gates ---

        # MHC-I optimal presentation length (8-11 aa); warn outside this range.
        if not (8 <= len(neoantigen) <= 11):
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"Neoantigen length {len(neoantigen)} aa is outside optimal MHC-I range (8-11 aa)",
                {'length': len(neoantigen), 'optimal_range': '8-11'}
            ))

        # Predicted MHC binding affinity gate (IC50, nM; lower is stronger).
        binding_affinity = mutation_info.get('binding_affinity_nm')
        if binding_affinity is not None:
            if binding_affinity > 500.0:
                results.append(ValidationResult(
                    SafetyLevel.CRITICAL,
                    f"Predicted MHC binding affinity too weak for immune presentation: "
                    f"{binding_affinity:.1f} nM > 500 nM threshold",
                    {'binding_affinity_nm': binding_affinity, 'threshold_nm': 500.0}
                ))
            elif binding_affinity > 200.0:
                results.append(ValidationResult(
                    SafetyLevel.WARNING,
                    f"Moderate MHC binding affinity; weak immune presentation predicted: "
                    f"{binding_affinity:.1f} nM (200-500 nM range)",
                    {'binding_affinity_nm': binding_affinity, 'strong_threshold_nm': 200.0}
                ))

        # Predicted immunogenicity gate.
        immunogenicity = mutation_info.get('immunogenicity_score')
        if immunogenicity is not None:
            if immunogenicity < 0.3:
                results.append(ValidationResult(
                    SafetyLevel.CRITICAL,
                    f"Predicted immunogenicity score below minimum threshold: "
                    f"{immunogenicity:.3f} < 0.30",
                    {'immunogenicity_score': immunogenicity, 'min_threshold': 0.3}
                ))
            elif immunogenicity < 0.5:
                results.append(ValidationResult(
                    SafetyLevel.WARNING,
                    f"Borderline immunogenicity score: {immunogenicity:.3f} (0.30-0.50 range)",
                    {'immunogenicity_score': immunogenicity, 'strong_threshold': 0.5}
                ))
        
        # Check amino acid composition
        allowed_aas = self.validation_rules['neoantigen']['allowed_amino_acids']
        invalid_aas = set(neoantigen.upper()) - allowed_aas
        if invalid_aas:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Invalid amino acids in neoantigen: {invalid_aas}",
                {'invalid_aas': list(invalid_aas), 'allowed_aas': list(allowed_aas)}
            ))
        
        # Check for self-similarity (autoimmune risk)
        if self._check_self_similarity(neoantigen):
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                "Neoantigen shows high similarity to human proteins (autoimmune risk)",
                {'neoantigen': neoantigen}
            ))
        
        # Check for oncogenic sequences
        if self._check_oncogenic_sequences(neoantigen):
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                "Neoantigen contains oncogenic sequences",
                {'neoantigen': neoantigen}
            ))
        
        # Check for toxic sequences
        if self._check_toxic_sequences(neoantigen):
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                "Neoantigen contains toxic sequences",
                {'neoantigen': neoantigen}
            ))
        
        # Check hydrophobicity
        hydrophobicity = self._calculate_hydrophobicity(neoantigen)
        if hydrophobicity > self.validation_rules['neoantigen']['max_hydrophobicity']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"Neoantigen too hydrophobic: {hydrophobicity:.2f} > {self.validation_rules['neoantigen']['max_hydrophobicity']:.2f}",
                {'hydrophobicity': hydrophobicity, 'max_hydrophobicity': self.validation_rules['neoantigen']['max_hydrophobicity']}
            ))
        
        # Check stability
        stability_score = self._calculate_peptide_stability(neoantigen)
        if stability_score < self.validation_rules['neoantigen']['min_stability_score']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"Neoantigen stability too low: {stability_score:.2f} < {self.validation_rules['neoantigen']['min_stability_score']:.2f}",
                {'stability_score': stability_score, 'min_stability_score': self.validation_rules['neoantigen']['min_stability_score']}
            ))
        
        return results
    
    def validate_mrna_sequence(self, sequence: str, construct_info: Dict[str, Any]) -> List[ValidationResult]:
        """Validate mRNA sequence safety and quality."""
        results = []

        sequence_upper = sequence.upper().strip()

        if len(sequence_upper) < self.validation_rules['mrna_sequence']['min_length']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"mRNA sequence too short: {len(sequence_upper)} < {self.validation_rules['mrna_sequence']['min_length']}",
                {'length': len(sequence_upper), 'min_length': self.validation_rules['mrna_sequence']['min_length']}
            ))

        if len(sequence_upper) > self.validation_rules['mrna_sequence']['max_length']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"mRNA sequence too long: {len(sequence_upper)} > {self.validation_rules['mrna_sequence']['max_length']}",
                {'length': len(sequence_upper), 'max_length': self.validation_rules['mrna_sequence']['max_length']}
            ))

        # Check base composition
        allowed_bases = self.validation_rules['mrna_sequence']['allowed_bases']
        invalid_bases = set(sequence_upper) - allowed_bases
        if invalid_bases:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Invalid RNA bases found: {invalid_bases}",
                {'invalid_bases': list(invalid_bases), 'allowed_bases': list(allowed_bases)}
            ))

        if not sequence_upper:
            return results

        # Check GC content
        gc_count = sequence_upper.count('G') + sequence_upper.count('C')
        gc_content = gc_count / len(sequence_upper)

        if gc_content < self.validation_rules['mrna_sequence']['min_gc_content']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"mRNA GC content too low: {gc_content:.2%} < {self.validation_rules['mrna_sequence']['min_gc_content']:.2%}",
                {'gc_content': gc_content, 'min_gc_content': self.validation_rules['mrna_sequence']['min_gc_content']}
            ))

        if gc_content > self.validation_rules['mrna_sequence']['max_gc_content']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"mRNA GC content too high: {gc_content:.2%} > {self.validation_rules['mrna_sequence']['max_gc_content']:.2%}",
                {'gc_content': gc_content, 'max_gc_content': self.validation_rules['mrna_sequence']['max_gc_content']}
            ))

        # Check for repetitive motifs
        repeated_motifs = self._count_repeated_motifs(sequence_upper)
        if repeated_motifs > self.validation_rules['mrna_sequence']['max_repeated_motifs']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"Too many repeated motifs: {repeated_motifs} > {self.validation_rules['mrna_sequence']['max_repeated_motifs']}",
                {'repeated_motifs': repeated_motifs, 'max_repeated_motifs': self.validation_rules['mrna_sequence']['max_repeated_motifs']}
            ))

        # Check self-complementarity
        self_comp = self._calculate_self_complementarity(sequence_upper)
        if self_comp > self.validation_rules['mrna_sequence']['max_self_complementarity']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"High self-complementarity: {self_comp:.2%} > {self.validation_rules['mrna_sequence']['max_self_complementarity']:.2%}",
                {'self_complementarity': self_comp, 'max_self_complementarity': self.validation_rules['mrna_sequence']['max_self_complementarity']}
            ))

        # Check for cryptic splice sites
        if self._check_splice_sites(sequence_upper):
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                "mRNA contains potential cryptic splice sites",
                {'sequence': sequence_upper[:100] + "..." if len(sequence_upper) > 100 else sequence_upper}
            ))

        # Check for internal ribosome entry sites (IRES)
        if self._check_ires(sequence_upper):
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                "mRNA contains potential IRES elements",
                {'sequence': sequence_upper[:100] + "..." if len(sequence_upper) > 100 else sequence_upper}
            ))

        # --- Stricter biological gates ---

        # CpG density: high obs/expected ratio triggers TLR9-mediated innate immune activation.
        cpg_count = sequence_upper.count('CG')
        c_freq = sequence_upper.count('C') / len(sequence_upper)
        g_freq = sequence_upper.count('G') / len(sequence_upper)
        expected_cpg = c_freq * g_freq * len(sequence_upper)
        if expected_cpg > 0:
            cpg_oe_ratio = cpg_count / expected_cpg
            if cpg_oe_ratio > 0.6:
                results.append(ValidationResult(
                    SafetyLevel.WARNING,
                    f"High CpG dinucleotide density (obs/exp {cpg_oe_ratio:.2f} > 0.60); "
                    "may trigger innate immune activation via TLR9",
                    {'cpg_count': cpg_count, 'cpg_oe_ratio': round(cpg_oe_ratio, 4)}
                ))

        # Internal stop codon detection across all three reading frames.
        stop_codons = {'UAA', 'UAG', 'UGA'}
        premature_stops = []
        for frame in range(3):
            for pos in range(frame, len(sequence_upper) - 5, 3):
                codon = sequence_upper[pos : pos + 3]
                if codon in stop_codons and pos + 3 < len(sequence_upper) - 3:
                    premature_stops.append((pos, codon))
        if premature_stops:
            first_pos, first_codon = premature_stops[0]
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"Premature stop codon {first_codon} at position {first_pos} "
                f"({len(premature_stops)} occurrence(s) across all frames)",
                {'premature_stop_count': len(premature_stops),
                 'first_occurrence': {'position': first_pos, 'codon': first_codon}}
            ))

        return results

    
    def validate_vaccine_construct(self, construct_info: Dict[str, Any]) -> List[ValidationResult]:
        """Validate complete vaccine construct."""
        results = []
        
        # Check total length
        total_length = construct_info.get('length', 0)
        if total_length > self.validation_rules['vaccine_construct']['max_total_length']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Vaccine construct too long: {total_length} > {self.validation_rules['vaccine_construct']['max_total_length']}",
                {'length': total_length, 'max_length': self.validation_rules['vaccine_construct']['max_total_length']}
            ))
        
        # Check stability score
        stability_score = construct_info.get('stability_score', 0)
        if stability_score < self.validation_rules['vaccine_construct']['min_stability_score']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"Vaccine stability too low: {stability_score:.2f} < {self.validation_rules['vaccine_construct']['min_stability_score']:.2f}",
                {'stability_score': stability_score, 'min_stability_score': self.validation_rules['vaccine_construct']['min_stability_score']}
            ))
        
        # Check immunogenicity score
        immunogenicity_score = construct_info.get('immunogenicity_score', 0)
        if immunogenicity_score > self.validation_rules['vaccine_construct']['max_immunogenicity_score']:
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                f"Vaccine immunogenicity too high: {immunogenicity_score:.2f} > {self.validation_rules['vaccine_construct']['max_immunogenicity_score']:.2f}",
                {'immunogenicity_score': immunogenicity_score, 'max_immunogenicity_score': self.validation_rules['vaccine_construct']['max_immunogenicity_score']}
            ))
        
        # Check required elements
        required_elements = self.validation_rules['vaccine_construct']['required_elements']
        missing_elements = []
        for element in required_elements:
            if not construct_info.get(element, False):
                missing_elements.append(element)
        
        if missing_elements:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Missing required vaccine elements: {missing_elements}",
                {'missing_elements': missing_elements, 'required_elements': required_elements}
            ))
        
        # Check for off-target effects
        if self._check_off_target_effects(construct_info):
            results.append(ValidationResult(
                SafetyLevel.WARNING,
                "Potential off-target effects detected",
                {'construct_info': construct_info}
            ))
        
        # Check dosage recommendations
        dose_recommendation = construct_info.get('dose_recommendation', 0)
        if dose_recommendation > self.regulatory_guidelines['fda_guidelines']['max_dose']:
            results.append(ValidationResult(
                SafetyLevel.CRITICAL,
                f"Recommended dose exceeds FDA limits: {dose_recommendation}ug > {self.regulatory_guidelines['fda_guidelines']['max_dose']}ug",
                {'dose': dose_recommendation, 'max_dose': self.regulatory_guidelines['fda_guidelines']['max_dose']}
            ))
        
        return results
    
    def _calculate_repetitive_score(self, sequence: str) -> float:
        """Calculate repetitive sequence score."""
        if len(sequence) < 10:
            return 0.0
        
        repeats = 0
        total_windows = 0
        
        for window_size in range(2, 6):  # Check 2-5 base repeats
            for i in range(len(sequence) - window_size):
                window = sequence[i:i+window_size]
                if window in sequence[i+window_size:]:
                    repeats += 1
                total_windows += 1
        
        return repeats / total_windows if total_windows > 0 else 0.0
    
    def _calculate_homopolymer_score(self, sequence: str) -> float:
        """Calculate homopolymer content score."""
        if len(sequence) == 0:
            return 0.0
        
        homopolymer_bases = 0
        current_base = None
        current_count = 0
        
        for base in sequence:
            if base == current_base:
                current_count += 1
                if current_count >= 3:  # Homopolymer of 3 or more
                    homopolymer_bases += 1
            else:
                current_base = base
                current_count = 1
        
        return homopolymer_bases / len(sequence)
    
    def _check_self_similarity(self, neoantigen: str) -> bool:
        """Check for similarity to human proteins (simplified)."""
        # This would normally check against a human proteome database
        # For now, use a simplified heuristic
        human_like_patterns = ['AAAA', 'PPPP', 'GGGG', 'LLLL']
        return any(pattern in neoantigen for pattern in human_like_patterns)
    
    def _check_oncogenic_sequences(self, neoantigen: str) -> bool:
        """Check for oncogenic sequence patterns."""
        oncogenic_patterns = [seq.lower() for seq in self.safety_checks['oncogenic_sequences']]
        neoantigen_lower = neoantigen.lower()
        return any(pattern in neoantigen_lower for pattern in oncogenic_patterns)
    
    def _check_toxic_sequences(self, neoantigen: str) -> bool:
        """Check for toxic sequence patterns."""
        toxic_patterns = [seq.lower() for seq in self.safety_checks['toxic_sequences']]
        neoantigen_lower = neoantigen.lower()
        return any(pattern in neoantigen_lower for pattern in toxic_patterns)
    
    def _calculate_hydrophobicity(self, peptide: str) -> float:
        """Calculate peptide hydrophobicity using Kyte-Doolittle scale."""
        kd_scale = {
            'I': 4.5, 'V': 4.2, 'L': 3.8, 'F': 2.8, 'C': 2.5, 'M': 1.9,
            'A': 1.8, 'G': -0.4, 'T': -0.7, 'S': -0.8, 'W': -0.9,
            'Y': -1.3, 'P': -1.6, 'H': -3.2, 'E': -3.5, 'Q': -3.5,
            'D': -3.5, 'N': -3.5, 'K': -3.9, 'R': -4.5
        }
        
        total_hydrophobicity = sum(kd_scale.get(aa, 0) for aa in peptide.upper())
        return total_hydrophobicity / len(peptide) if peptide else 0.0
    
    def _calculate_peptide_stability(self, peptide: str) -> float:
        """Calculate peptide stability score."""
        # Simplified stability calculation
        # In practice, this would use more sophisticated algorithms
        
        # Penalize unstable amino acids
        unstable_aas = set('DE')
        unstable_count = sum(1 for aa in peptide.upper() if aa in unstable_aas)
        
        # Penalize very short or very long peptides
        length_penalty = 0
        if len(peptide) < 9:
            length_penalty = (9 - len(peptide)) * 0.1
        elif len(peptide) > 12:
            length_penalty = (len(peptide) - 12) * 0.05
        
        stability_score = 1.0 - (unstable_count / len(peptide)) - length_penalty
        return max(0.0, min(1.0, stability_score))
    
    def _count_repeated_motifs(self, sequence: str) -> int:
        """Count repeated sequence motifs."""
        motifs = ['AAAA', 'CCCC', 'GGGG', 'UUUU', 'AUAU', 'CGCG', 'UAUA']
        count = sum(sequence.count(motif) for motif in motifs)
        return count
    
    def _calculate_self_complementarity(self, sequence: str) -> float:
        """Calculate self-complementarity score."""
        complement_map = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C'}
        
        complementary_count = 0
        for i in range(len(sequence) // 2):
            if sequence[i] == complement_map.get(sequence[-(i+1)], ''):
                complementary_count += 1
        
        return complementary_count / (len(sequence) // 2) if sequence else 0.0
    
    def _check_splice_sites(self, sequence: str) -> bool:
        """Check for potential cryptic splice sites."""
        splice_donor = r'GT[AGCT]{5}'
        splice_acceptor = r'[AGCT]{5}AG'
        
        return (bool(re.search(splice_donor, sequence)) or 
                bool(re.search(splice_acceptor, sequence)))
    
    def _check_ires(self, sequence: str) -> bool:
        """Check for potential IRES elements."""
        # Simplified IRES pattern check
        ires_patterns = ['AAAAAC', 'GGGAGG', 'UUUUCC']
        return any(pattern in sequence for pattern in ires_patterns)
    
    def _check_off_target_effects(self, construct_info: Dict[str, Any]) -> bool:
        """Check for potential off-target effects."""
        # This would normally check against a comprehensive database
        # For now, use simplified heuristics
        
        sequence = construct_info.get('sequence', '')
        if len(sequence) < 20:
            return False
        
        # Check for high similarity to common human sequences
        human_sequences = ['ACTB', 'GAPDH', 'HPRT1', 'RPLP0']
        return any(human_seq in sequence for human_seq in human_sequences)
    
    def _load_clinical_safety_rules(self) -> Dict[str, Any]:
        """Load clinical safety rules for patient care."""
        return {
            'patient_safety': {
                'max_treatment_intensity': 3,  # 1=low, 2=medium, 3=high
                'min_response_threshold': 0.3,
                'max_adverse_event_risk': 0.1,
                'required_monitoring_frequency': 'weekly'
            },
            'data_privacy': {
                'hipaa_compliance': True,
                'gdpr_compliance': True,
                'data_encryption_required': True,
                'access_logging_required': True
            },
            'clinical_trial_safety': {
                'max_patient_risk_score': 0.7,
                'required_informed_consent': True,
                'independent_review_board_required': True,
                'stopping_rules_required': True
            }
        }
    
    def _load_ethical_guidelines(self) -> Dict[str, Any]:
        """Load ethical guidelines for AI in healthcare."""
        return {
            'beneficence': {
                'maximize_benefits': True,
                'minimize_harms': True,
                'patient_welfare_first': True
            },
            'non_maleficence': {
                'do_no_harm': True,
                'avoid_unnecessary_risks': True,
                'respect_patient_autonomy': True
            },
            'justice': {
                'fair_resource_allocation': True,
                'avoid_discrimination': True,
                'equitable_access': True
            },
            'transparency': {
                'explainable_decisions': True,
                'audit_trail_required': True,
                'bias_monitoring_required': True
            }
        }
    
    def validate_complete_pipeline(
        self,
        dna_sequence: str,
        neoantigens: list,
        mrna_construct: dict,
        neoantigen_metadata=None,
    ):
        """Validate the complete vaccine design pipeline.

        Args:
            neoantigen_metadata: Optional list of per-neoantigen dicts with
                ``binding_affinity_nm`` and/or ``immunogenicity_score`` keys
                so stricter per-peptide biological gates can be applied.
        """
        validation_results = {
            'dna_validation': self.validate_dna_sequence(dna_sequence, "sample_001"),
            'neoantigen_validation': [],
            'mrna_validation': self.validate_mrna_sequence(
                mrna_construct.get('sequence', ''), mrna_construct
            ),
            'construct_validation': self.validate_vaccine_construct(mrna_construct),
        }
        for i, neoantigen in enumerate(neoantigens):
            meta = {'index': i}
            if neoantigen_metadata and i < len(neoantigen_metadata):
                meta.update(neoantigen_metadata[i])
            validation_results['neoantigen_validation'].extend(
                self.validate_neoantigen(neoantigen, meta)
            )
        return validation_results

    def generate_safety_report(self, validation_results):
        """Generate a JSON-serializable safety report from pipeline validation results."""
        total_checks = 0
        critical_issues = 0
        warnings = 0
        passed_checks = 0
        serializable_details = {}

        for category, results in validation_results.items():
            serializable_details[category] = []
            for result in results:
                total_checks += 1
                if result.level == SafetyLevel.CRITICAL:
                    critical_issues += 1
                elif result.level == SafetyLevel.WARNING:
                    warnings += 1
                else:
                    passed_checks += 1
                serializable_details[category].append({
                    'level': result.level.value,
                    'message': result.message,
                    'details': result.details,
                })

        if critical_issues > 0:
            overall_status = 'CRITICAL'
        elif warnings > 5:
            overall_status = 'WARNING'
        else:
            overall_status = 'PASS'

        recommendations = []
        if critical_issues > 0:
            recommendations.append("Address all critical safety issues before proceeding")
        if warnings > 0:
            recommendations.append("Review and address safety warnings")
        if total_checks == 0:
            recommendations.append("No validation checks performed")

        return {
            'summary': {
                'total_checks': total_checks,
                'critical_issues': critical_issues,
                'warnings': warnings,
                'passed_checks': passed_checks,
                'overall_status': overall_status,
            },
            'detailed_results': serializable_details,
            'recommendations': recommendations,
        }

def main():
    """Example of using the safety validator."""
    validator = EnhancedSafetyValidator()

    # Example validation data
    dna_seq = "ATCGATCGATCG" * 100  # 1200 bases
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

    validation_results = validator.validate_complete_pipeline(
        dna_sequence=dna_seq,
        neoantigens=neoantigens,
        mrna_construct=mrna_construct,
    )
    report = validator.generate_safety_report(validation_results)

    logger.info("Safety Report Summary: %s", report["summary"])


if __name__ == "__main__":
    main()
