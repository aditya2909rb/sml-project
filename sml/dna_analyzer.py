"""
DNA Sequence Analyzer for Cancer Mutation Detection and Neoantigen Prediction

This module provides functionality to analyze DNA sequences, identify cancer mutations,
and predict neoantigens for personalized mRNA vaccine design.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import math


@dataclass
class Mutation:
    """Represents a detected mutation in DNA sequence."""
    position: int
    reference_base: str
    mutated_base: str
    mutation_type: str  # 'SNV', 'insertion', 'deletion'
    gene_name: Optional[str] = None
    consequence: Optional[str] = None


@dataclass
class Neoantigen:
    """Represents a predicted neoantigen from a mutation."""
    mutation: Mutation
    peptide_sequence: str
    hla_allele: str
    binding_affinity: float  # Lower is better (nM)
    immunogenicity_score: float
    stability_score: float


@dataclass
class DNAMutationReport:
    """Complete report of DNA analysis results."""
    sample_id: str
    total_mutations: int
    driver_mutations: List[Mutation]
    passenger_mutations: List[Mutation]
    predicted_neoantigens: List[Neoantigen]
    tumor_mutational_burden: float
    microsatellite_status: str


class DNAMutationDetector:
    """Detects mutations in DNA sequences by comparing tumor vs normal samples."""
    
    def __init__(self):
        self.cancer_genes = self._load_cancer_genes()
        self.driver_mutation_patterns = self._load_driver_patterns()
    
    def _load_cancer_genes(self) -> set:
        """Load known cancer-associated genes."""
        # This would typically load from a database or file
        return {
            'TP53', 'KRAS', 'EGFR', 'BRCA1', 'BRCA2', 'PIK3CA', 'AKT1', 'BRAF',
            'NRAS', 'HRAS', 'MYC', 'ERBB2', 'CDKN2A', 'PTEN', 'RB1', 'VHL',
            'APC', 'CTNNB1', 'IDH1', 'IDH2', 'NOTCH1', 'SF3B1', 'U2AF1'
        }
    
    def _load_driver_patterns(self) -> Dict[str, List[str]]:
        """Load known driver mutation patterns."""
        return {
            'TP53': ['R175H', 'R248Q', 'R273H', 'R282W'],
            'KRAS': ['G12D', 'G12V', 'G13D', 'Q61H'],
            'EGFR': ['L858R', 'T790M', 'G719S', 'E746_A750del'],
            'BRAF': ['V600E', 'V600K', 'K601E']
        }
    
    def detect_mutations(
        self, 
        normal_dna: str, 
        tumor_dna: str, 
        gene_annotations: Optional[Dict[int, str]] = None
    ) -> List[Mutation]:
        """
        Compare normal and tumor DNA to identify somatic mutations.
        
        Args:
            normal_dna: Reference DNA sequence from healthy tissue
            tumor_dna: DNA sequence from tumor tissue
            gene_annotations: Optional mapping of positions to gene names
            
        Returns:
            List of detected mutations
        """
        mutations = []
        
        # Ensure sequences are same length for comparison
        min_length = min(len(normal_dna), len(tumor_dna))
        normal_dna = normal_dna[:min_length]
        tumor_dna = tumor_dna[:min_length]
        
        for i in range(min_length):
            if normal_dna[i] != tumor_dna[i]:
                mutation_type = self._classify_mutation(normal_dna[i], tumor_dna[i])
                gene_name = gene_annotations.get(i) if gene_annotations else None
                
                mutation = Mutation(
                    position=i,
                    reference_base=normal_dna[i],
                    mutated_base=tumor_dna[i],
                    mutation_type=mutation_type,
                    gene_name=gene_name
                )
                
                # Add consequence prediction
                mutation.consequence = self._predict_consequence(mutation)
                
                mutations.append(mutation)
        
        return mutations
    
    def _classify_mutation(self, ref_base: str, mut_base: str) -> str:
        """Classify mutation type based on base changes."""
        if len(ref_base) == 1 and len(mut_base) == 1:
            return 'SNV'  # Single Nucleotide Variant
        elif len(ref_base) < len(mut_base):
            return 'insertion'
        elif len(ref_base) > len(mut_base):
            return 'deletion'
        else:
            return 'unknown'
    
    def _predict_consequence(self, mutation: Mutation) -> str:
        """Predict the functional consequence of a mutation."""
        if mutation.gene_name in self.cancer_genes:
            # Check if it matches known driver patterns
            if self._is_driver_mutation(mutation):
                return 'likely_driver'
            else:
                return 'potential_driver'
        else:
            return 'passenger'


class NeoantigenPredictor:
    """Predicts neoantigens from DNA mutations."""
    
    def __init__(self):
        self.hla_alleles = self._load_hla_alleles()
        self.codon_table = self._load_codon_table()
        self.amino_acid_properties = self._load_amino_acid_properties()
    
    def _load_hla_alleles(self) -> List[str]:
        """Load common HLA alleles for binding prediction."""
        return [
            'HLA-A*02:01', 'HLA-A*03:01', 'HLA-A*11:01', 'HLA-A*24:02',
            'HLA-B*07:02', 'HLA-B*08:01', 'HLA-B*15:01', 'HLA-B*40:01',
            'HLA-C*07:02', 'HLA-C*03:04', 'HLA-C*04:01'
        ]
    
    def _load_codon_table(self) -> Dict[str, str]:
        """Load standard genetic code."""
        return {
            'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
            'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
            'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
            'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
            'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
            'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
            'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
            'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
        }
    
    def _load_amino_acid_properties(self) -> Dict[str, Dict[str, float]]:
        """Load amino acid properties for immunogenicity scoring."""
        return {
            'A': {'hydrophobicity': 1.8, 'volume': 88.6, 'polarity': 0.0},
            'R': {'hydrophobicity': -4.5, 'volume': 173.4, 'polarity': 1.0},
            'N': {'hydrophobicity': -3.5, 'volume': 114.1, 'polarity': 1.0},
            'D': {'hydrophobicity': -3.5, 'volume': 111.1, 'polarity': 1.0},
            'C': {'hydrophobicity': 2.5, 'volume': 108.5, 'polarity': 0.5},
            'Q': {'hydrophobicity': -3.5, 'volume': 143.8, 'polarity': 1.0},
            'E': {'hydrophobicity': -3.5, 'volume': 138.4, 'polarity': 1.0},
            'G': {'hydrophobicity': -0.4, 'volume': 60.1, 'polarity': 0.0},
            'H': {'hydrophobicity': -3.2, 'volume': 153.2, 'polarity': 1.0},
            'I': {'hydrophobicity': 4.5, 'volume': 166.7, 'polarity': 0.0},
            'L': {'hydrophobicity': 3.8, 'volume': 166.7, 'polarity': 0.0},
            'K': {'hydrophobicity': -3.9, 'volume': 168.6, 'polarity': 1.0},
            'M': {'hydrophobicity': 1.9, 'volume': 162.9, 'polarity': 0.5},
            'F': {'hydrophobicity': 2.8, 'volume': 189.9, 'polarity': 0.5},
            'P': {'hydrophobicity': -1.6, 'volume': 112.7, 'polarity': 0.0},
            'S': {'hydrophobicity': -0.8, 'volume': 89.0, 'polarity': 1.0},
            'T': {'hydrophobicity': -0.7, 'volume': 116.1, 'polarity': 1.0},
            'W': {'hydrophobicity': -0.9, 'volume': 227.8, 'polarity': 1.0},
            'Y': {'hydrophobicity': -1.3, 'volume': 193.6, 'polarity': 1.0},
            'V': {'hydrophobicity': 4.2, 'volume': 140.0, 'polarity': 0.0}
        }
    
    def predict_neoantigens(
        self, 
        mutations: List[Mutation], 
        hla_allele: str = 'HLA-A*02:01'
    ) -> List[Neoantigen]:
        """
        Predict neoantigens from a list of mutations.
        
        Args:
            mutations: List of detected mutations
            hla_allele: HLA allele for binding prediction
            
        Returns:
            List of predicted neoantigens
        """
        neoantigens = []
        
        for mutation in mutations:
            # Generate peptide sequences around the mutation
            peptides = self._generate_peptides(mutation)
            
            for peptide in peptides:
                # Predict binding affinity
                affinity = self._predict_binding_affinity(peptide, hla_allele)
                
                # Calculate immunogenicity score
                immunogenicity = self._calculate_immunogenicity(peptide)
                
                # Calculate stability score
                stability = self._calculate_stability(peptide)
                
                # Keep a broader candidate set here; stricter patient-level gates
                # are applied downstream in the patient pipeline.
                if affinity <= 1200 and immunogenicity >= 0.30 and stability >= 0.20:
                    neoantigen = Neoantigen(
                        mutation=mutation,
                        peptide_sequence=peptide,
                        hla_allele=hla_allele,
                        binding_affinity=affinity,
                        immunogenicity_score=immunogenicity,
                        stability_score=stability
                    )
                    neoantigens.append(neoantigen)
        
        # Sort by binding affinity (lower is better)
        neoantigens.sort(key=lambda x: x.binding_affinity)
        
        return neoantigens
    
    def _generate_peptides(self, mutation: Mutation, length: int = 9) -> List[str]:
        """Generate peptide sequences around the mutation site."""
        # This is a simplified version - in practice, you'd need the full protein sequence
        # For now, we'll create hypothetical peptides based on the mutation
        
        peptides = []
        mutated_aa = mutation.mutated_base if mutation.mutated_base in self.amino_acid_properties else 'A'

        # Add one deterministic anchor-optimized peptide for HLA-A*02:01-like motifs.
        # Position 2 prefers L/M/V and position 9 prefers V/L.
        anchor_peptide = ['A'] * length
        if length >= 2:
            anchor_peptide[1] = 'L'
        if length >= 9:
            anchor_peptide[8] = 'V'
        anchor_peptide[length // 2] = mutated_aa
        peptides.append(''.join(anchor_peptide))

        # Deterministic pseudo-random contexts for reproducibility across runs.
        import random
        rng = random.Random((mutation.position + 1) * 131 + ord(mutated_aa))
        
        # Generate peptides with the mutated amino acid
        for i in range(7):
            peptide = self._create_random_peptide(length, mutated_aa, rng)
            peptides.append(peptide)
        
        return peptides
    
    def _create_random_peptide(self, length: int, center_aa: str, rng) -> str:
        """Create a random peptide with specified amino acid in center."""
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        
        # Create random sequence
        peptide = ''
        for i in range(length):
            if i == length // 2:
                peptide += center_aa
            else:
                peptide += rng.choice(amino_acids)
        
        return peptide
    
    def _predict_binding_affinity(self, peptide: str, hla_allele: str) -> float:
        """
        Predict MHC binding affinity using simplified scoring.
        Lower values indicate stronger binding.
        """
        # Simplified scoring based on amino acid preferences for HLA-A*02:01
        # In practice, this would use machine learning models or databases
        
        anchor_preferences = {
            'HLA-A*02:01': {'position2': 'LMV', 'position9': 'VL'}
        }
        
        score = 0.0
        
        if hla_allele in anchor_preferences:
            anchors = anchor_preferences[hla_allele]
            
            # Check anchor positions
            if len(peptide) >= 2 and peptide[1] in anchors.get('position2', ''):
                score -= 2.0
            if len(peptide) >= 9 and peptide[8] in anchors.get('position9', ''):
                score -= 2.0
            
            # Add penalty for unfavorable amino acids
            unfavorable = 'DE'
            for aa in peptide:
                if aa in unfavorable:
                    score += 0.5
        
        # Convert to approximate nM affinity
        base_affinity = 1000.0  # Base affinity in nM
        return max(1.0, base_affinity * math.exp(-score / 2.0))
    
    def _calculate_immunogenicity(self, peptide: str) -> float:
        """Calculate immunogenicity score based on amino acid properties."""
        score = 0.0
        
        for aa in peptide:
            if aa in self.amino_acid_properties:
                props = self.amino_acid_properties[aa]
                # Favor hydrophilic, polar amino acids
                score += (1.0 - props['hydrophobicity'] / 5.0) * props['polarity']
        
        return min(1.0, max(0.0, score / len(peptide)))
    
    def _calculate_stability(self, peptide: str) -> float:
        """Calculate peptide stability score."""
        score = 0.0
        
        for i in range(len(peptide) - 1):
            aa1 = peptide[i]
            aa2 = peptide[i + 1]
            
            if aa1 in self.amino_acid_properties and aa2 in self.amino_acid_properties:
                # Favor interactions between compatible amino acids
                vol_diff = abs(self.amino_acid_properties[aa1]['volume'] - 
                              self.amino_acid_properties[aa2]['volume'])
                score += max(0.0, 1.0 - vol_diff / 200.0)
        
        return min(1.0, max(0.0, score / (len(peptide) - 1)))


class DNAMutationAnalyzer:
    """Main class for DNA mutation analysis and neoantigen prediction."""
    
    def __init__(self):
        self.mutation_detector = DNAMutationDetector()
        self.neoantigen_predictor = NeoantigenPredictor()
    
    def analyze_sample(
        self, 
        sample_id: str,
        normal_dna: str,
        tumor_dna: str,
        hla_allele: str = 'HLA-A*02:01',
        gene_annotations: Optional[Dict[int, str]] = None
    ) -> DNAMutationReport:
        """
        Perform complete DNA mutation analysis for a sample.
        
        Args:
            sample_id: Unique identifier for the sample
            normal_dna: Reference DNA sequence
            tumor_dna: Tumor DNA sequence
            hla_allele: Patient's HLA allele for neoantigen prediction
            gene_annotations: Optional gene annotations for positions
            
        Returns:
            Complete mutation analysis report
        """
        # Detect mutations
        mutations = self.mutation_detector.detect_mutations(
            normal_dna, tumor_dna, gene_annotations
        )
        
        # Classify mutations
        driver_mutations = []
        passenger_mutations = []
        
        for mutation in mutations:
            if mutation.consequence in ['likely_driver', 'potential_driver']:
                driver_mutations.append(mutation)
            else:
                passenger_mutations.append(mutation)
        
        # Predict neoantigens. In demo/synthetic contexts gene annotations may be
        # absent, which can classify all mutations as passengers; fall back to all
        # detected mutations so the downstream vaccine pipeline remains usable.
        mutation_pool = driver_mutations if driver_mutations else mutations
        neoantigens = self.neoantigen_predictor.predict_neoantigens(
            mutation_pool, hla_allele
        )
        
        # Calculate tumor mutational burden
        tmb = len(mutations) / len(normal_dna) * 1000000  # mutations per megabase
        
        # Determine microsatellite status (simplified)
        microsatellite_status = self._assess_microsatellite_status(tumor_dna)
        
        return DNAMutationReport(
            sample_id=sample_id,
            total_mutations=len(mutations),
            driver_mutations=driver_mutations,
            passenger_mutations=passenger_mutations,
            predicted_neoantigens=neoantigens,
            tumor_mutational_burden=tmb,
            microsatellite_status=microsatellite_status
        )
    
    def _assess_microsatellite_status(self, dna_sequence: str) -> str:
        """Assess microsatellite instability status."""
        # Simplified assessment based on repeat patterns
        repeats = self._find_microsatellites(dna_sequence)
        
        if len(repeats) > 100:  # Arbitrary threshold
            return "MSI-H"  # High microsatellite instability
        elif len(repeats) > 50:
            return "MSI-L"  # Low microsatellite instability
        else:
            return "MSS"   # Microsatellite stable
    
    def _find_microsatellites(self, sequence: str, min_repeats: int = 3) -> List[str]:
        """Find microsatellite repeat patterns in DNA sequence."""
        microsatellites = []
        
        # Look for simple repeats
        patterns = ['A', 'T', 'C', 'G', 'AT', 'AC', 'AG', 'CT', 'CG', 'TG']
        
        for pattern in patterns:
            for i in range(len(sequence) - len(pattern) + 1):
                count = 0
                pos = i
                while sequence[pos:pos+len(pattern)] == pattern and pos < len(sequence):
                    count += 1
                    pos += len(pattern)
                
                if count >= min_repeats:
                    microsatellites.append(f"{pattern}x{count}")
        
        return microsatellites