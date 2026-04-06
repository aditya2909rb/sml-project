"""
mRNA Vaccine Designer for Personalized Cancer Immunotherapy

This module designs optimized mRNA sequences for neoantigens identified from
DNA mutation analysis, including codon optimization, stability enhancement,
and delivery optimization.
"""

from __future__ import annotations

import re
import random
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import math


@dataclass
class MRNAConstruct:
    """Represents a complete mRNA vaccine construct."""
    sequence: str
    length: int
    gc_content: float
    stability_score: float
    immunogenicity_score: float
    delivery_efficiency: float
    neoantigens: List[str]
    u_tr_regions: Dict[str, str]
    optimizations_applied: List[str]


@dataclass
class CodonOptimization:
    """Represents codon optimization results."""
    original_sequence: str
    optimized_sequence: str
    codon_usage_improvement: float
    expression_score: float


class CodonOptimizer:
    """Optimizes codon usage for human expression systems."""
    
    def __init__(self):
        self.human_codon_usage = self._load_human_codon_usage()
        self.rare_codons = self._identify_rare_codons()
        self.optimal_codons = self._identify_optimal_codons()
    
    def _load_human_codon_usage(self) -> Dict[str, float]:
        """Load human codon usage frequencies (per 1000 codons)."""
        # Source: https://www.kazusa.or.jp/codon/
        return {
            'TTT': 18.4, 'TTC': 19.6, 'TTA': 12.2, 'TTG': 12.6,
            'TCT': 16.0, 'TCC': 17.0, 'TCA': 12.2, 'TCG': 4.8,
            'TAT': 12.2, 'TAC': 15.1, 'TAA': 0.7, 'TAG': 0.3,
            'TGT': 9.8, 'TGC': 13.7, 'TGA': 1.2, 'TGG': 12.8,
            'CTT': 12.6, 'CTC': 19.6, 'CTA': 6.2, 'CTG': 39.6,
            'CCT': 17.5, 'CCC': 19.8, 'CCA': 16.0, 'CCG': 6.9,
            'CAT': 10.9, 'CAC': 15.3, 'CAA': 12.3, 'CAG': 34.2,
            'CGT': 4.2, 'CGC': 18.8, 'CGA': 4.6, 'CGG': 11.0,
            'ATT': 15.2, 'ATC': 20.8, 'ATA': 4.5, 'ATG': 22.0,
            'ACT': 12.4, 'ACC': 28.1, 'ACA': 15.4, 'ACG': 6.1,
            'AAT': 16.1, 'AAC': 20.5, 'AAA': 24.4, 'AAG': 33.2,
            'AGT': 12.1, 'AGC': 19.2, 'AGA': 6.8, 'AGG': 12.1,
            'GTT': 14.7, 'GTC': 18.5, 'GTA': 7.1, 'GTG': 29.5,
            'GCT': 18.9, 'GCC': 27.0, 'GCA': 19.4, 'GCG': 7.1,
            'GAT': 22.8, 'GAC': 25.1, 'GAA': 29.0, 'GAG': 40.1,
            'GGT': 11.9, 'GGC': 33.8, 'GGA': 16.5, 'GGG': 16.0
        }
    
    def _identify_rare_codons(self, threshold: float = 10.0) -> set:
        """Identify rare codons (low usage frequency)."""
        return {codon for codon, freq in self.human_codon_usage.items() if freq < threshold}
    
    def _identify_optimal_codons(self) -> Dict[str, str]:
        """Identify optimal codons for each amino acid."""
        amino_acids = {
            'F': ['TTT', 'TTC'], 'L': ['TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG'],
            'I': ['ATT', 'ATC', 'ATA'], 'M': ['ATG'], 'V': ['GTT', 'GTC', 'GTA', 'GTG'],
            'S': ['TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC'], 'P': ['CCT', 'CCC', 'CCA', 'CCG'],
            'T': ['ACT', 'ACC', 'ACA', 'ACG'], 'A': ['GCT', 'GCC', 'GCA', 'GCG'],
            'Y': ['TAT', 'TAC'], '*': ['TAA', 'TAG', 'TGA'], 'H': ['CAT', 'CAC'],
            'Q': ['CAA', 'CAG'], 'N': ['AAT', 'AAC'], 'K': ['AAA', 'AAG'],
            'D': ['GAT', 'GAC'], 'E': ['GAA', 'GAG'], 'C': ['TGT', 'TGC'],
            'W': ['TGG'], 'R': ['CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
            'G': ['GGT', 'GGC', 'GGA', 'GGG']
        }
        
        optimal = {}
        for aa, codons in amino_acids.items():
            best_codon = max(codons, key=lambda c: self.human_codon_usage.get(c, 0))
            optimal[aa] = best_codon
        
        return optimal
    
    def optimize_sequence(self, amino_acid_sequence: str) -> CodonOptimization:
        """
        Optimize amino acid sequence for human expression.
        
        Args:
            amino_acid_sequence: Input amino acid sequence
            
        Returns:
            Codon optimization results
        """
        # Convert amino acids to optimal codons
        optimized_codons = []
        original_codons = []
        
        for aa in amino_acid_sequence:
            if aa in self.optimal_codons:
                optimized_codons.append(self.optimal_codons[aa])
                # For original, pick a random codon for that amino acid
                possible_codons = [c for c, freq in self.human_codon_usage.items() 
                                 if self._codon_to_aa(c) == aa]
                original_codons.append(random.choice(possible_codons))
            else:
                # Unknown amino acid, skip
                continue
        
        original_seq = ''.join(original_codons)
        optimized_seq = ''.join(optimized_codons)
        
        # Calculate improvement score
        improvement = self._calculate_codon_usage_improvement(original_seq, optimized_seq)
        expression_score = self._calculate_expression_score(optimized_seq)
        
        return CodonOptimization(
            original_sequence=original_seq,
            optimized_sequence=optimized_seq,
            codon_usage_improvement=improvement,
            expression_score=expression_score
        )
    
    def _codon_to_aa(self, codon: str) -> str:
        """Convert codon to amino acid."""
        codon_table = {
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
        return codon_table.get(codon, 'X')
    
    def _calculate_codon_usage_improvement(self, original: str, optimized: str) -> float:
        """Calculate improvement in codon usage."""
        def calculate_score(sequence):
            score = 0.0
            for i in range(0, len(sequence), 3):
                codon = sequence[i:i+3]
                if codon in self.human_codon_usage:
                    score += self.human_codon_usage[codon]
            return score / (len(sequence) // 3) if sequence else 0
        
        orig_score = calculate_score(original)
        opt_score = calculate_score(optimized)
        
        return (opt_score - orig_score) / orig_score if orig_score > 0 else 0
    
    def _calculate_expression_score(self, sequence: str) -> float:
        """Calculate predicted expression score based on codon usage."""
        score = 0.0
        count = 0
        
        for i in range(0, len(sequence), 3):
            codon = sequence[i:i+3]
            if codon in self.human_codon_usage:
                freq = self.human_codon_usage[codon]
                # Normalize to 0-1 scale
                score += min(1.0, freq / 50.0)
                count += 1
        
        return score / count if count > 0 else 0


class StabilityOptimizer:
    """Optimizes mRNA stability through various modifications."""
    
    def __init__(self, gc_content_target: float = 0.50, gc_content_bounds: Tuple[float, float] = (0.40, 0.60)):
        self.gc_content_target = gc_content_target
        self.gc_content_bounds = gc_content_bounds
        self.unstable_motifs = ['AUUUA', 'UAUAU', 'UUUUU']  # AU-rich elements
        self.stable_motifs = ['GGG', 'CCC', 'GCG']  # GC-rich stabilizing elements
    
    def optimize_stability(self, sequence: str) -> str:
        """
        Optimize mRNA sequence for stability.
        
        Args:
            sequence: Input mRNA sequence
            
        Returns:
            Stability-optimized sequence
        """
        # Normalize DNA alphabet to RNA for mRNA optimization steps.
        optimized = sequence.replace('T', 'U')
        
        # 1. Optimize GC content
        optimized = self._adjust_gc_content(optimized)
        
        # 2. Remove unstable motifs
        optimized = self._remove_unstable_motifs(optimized)
        
        # 3. Add stabilizing elements
        optimized = self._add_stabilizing_elements(optimized)
        
        # 4. Optimize secondary structure
        optimized = self._optimize_secondary_structure(optimized)

        # 5. Enforce deploy-time GC operating window.
        optimized = self._enforce_gc_window(optimized)
        
        return optimized
    
    def _adjust_gc_content(self, sequence: str) -> str:
        """Adjust GC content toward target levels."""
        current_gc = self._calculate_gc_content(sequence)
        
        if current_gc < self.gc_content_target:
            # Add G/C bases
            return self._increase_gc_content(sequence)
        elif current_gc > self.gc_content_target:
            # Add A/U bases
            return self._decrease_gc_content(sequence)
        else:
            return sequence
    
    def _calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content percentage."""
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence) if sequence else 0
    
    def _increase_gc_content(self, sequence: str) -> str:
        """Increase GC content by deterministic A/U -> G/C substitution."""
        result = list(sequence)

        current_gc = self._calculate_gc_content(sequence)
        target_gc = max(self.gc_content_target, self.gc_content_bounds[0])
        substitutions = max(0, math.ceil((target_gc - current_gc) * len(sequence)))

        changed = 0
        for pos, base in enumerate(result):
            if changed >= substitutions:
                break
            if base in ['A', 'U']:
                result[pos] = 'G' if (pos % 2 == 0) else 'C'
                changed += 1
        
        return ''.join(result)
    
    def _decrease_gc_content(self, sequence: str) -> str:
        """Decrease GC content by deterministic G/C -> A/U substitution."""
        result = list(sequence)

        current_gc = self._calculate_gc_content(sequence)
        target_gc = min(self.gc_content_target, self.gc_content_bounds[1])
        substitutions = max(0, math.ceil((current_gc - target_gc) * len(sequence)))

        changed = 0
        for pos, base in enumerate(result):
            if changed >= substitutions:
                break
            if base in ['G', 'C']:
                result[pos] = 'A' if (pos % 2 == 0) else 'U'
                changed += 1
        
        return ''.join(result)

    def _enforce_gc_window(self, sequence: str) -> str:
        """Clamp sequence GC into configured deployment window."""
        min_gc, max_gc = self.gc_content_bounds
        current_gc = self._calculate_gc_content(sequence)

        if current_gc < min_gc:
            return self._increase_gc_content_to(sequence, min_gc)
        if current_gc > max_gc:
            return self._decrease_gc_content_to(sequence, max_gc)
        return sequence

    def _increase_gc_content_to(self, sequence: str, target_gc: float) -> str:
        result = list(sequence)
        needed = max(0, math.ceil((target_gc - self._calculate_gc_content(sequence)) * len(sequence)))
        changed = 0
        for pos, base in enumerate(result):
            if changed >= needed:
                break
            if base in ['A', 'U']:
                result[pos] = 'G' if (pos % 2 == 0) else 'C'
                changed += 1
        return ''.join(result)

    def _decrease_gc_content_to(self, sequence: str, target_gc: float) -> str:
        result = list(sequence)
        needed = max(0, math.ceil((self._calculate_gc_content(sequence) - target_gc) * len(sequence)))
        changed = 0
        for pos, base in enumerate(result):
            if changed >= needed:
                break
            if base in ['G', 'C']:
                result[pos] = 'A' if (pos % 2 == 0) else 'U'
                changed += 1
        return ''.join(result)
    
    def _remove_unstable_motifs(self, sequence: str) -> str:
        """Remove AU-rich unstable motifs."""
        result = sequence
        
        for motif in self.unstable_motifs:
            result = result.replace(motif, self._replace_motif(motif))
        
        return result
    
    def _replace_motif(self, motif: str) -> str:
        """Replace unstable motif with stable alternative."""
        replacements = {
            'AUUUA': 'AGGUA',
            'UAUAU': 'UGGUA', 
            'UUUUU': 'UGCGU'
        }
        return replacements.get(motif, motif)
    
    def _add_stabilizing_elements(self, sequence: str) -> str:
        """Add stabilizing GC-rich elements."""
        # Add stabilizing elements at strategic positions
        stabilizing_seq = 'GGGCGG'
        positions = [len(sequence) // 4, len(sequence) // 2, 3 * len(sequence) // 4]
        
        result = list(sequence)
        for pos in sorted(positions, reverse=True):
            result.insert(pos, stabilizing_seq)
        
        return ''.join(result)
    
    def _optimize_secondary_structure(self, sequence: str) -> str:
        """Optimize secondary structure to reduce self-complementarity."""
        # Simplified secondary structure optimization
        # In practice, this would use RNA folding algorithms
        
        result = list(sequence)
        
        # Reduce long stretches of complementary sequences
        for i in range(len(result) - 10):
            window = ''.join(result[i:i+10])
            complement = self._get_complement(window)
            
            # Check if complement appears nearby
            for j in range(i+20, min(i+100, len(result)-10)):
                if ''.join(result[j:j+10]) == complement:
                    # Introduce mutations to break complementarity
                    for k in range(5):
                        if i+k < len(result):
                            result[i+k] = random.choice(['A', 'C', 'G', 'U'])
        
        return ''.join(result)
    
    def _get_complement(self, sequence: str) -> str:
        """Get RNA complement of sequence."""
        complement_map = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C'}
        return ''.join(complement_map.get(base, base) for base in sequence)
    
    def calculate_stability_score(self, sequence: str) -> float:
        """Calculate stability score for sequence."""
        score = 0.0
        
        # GC content contribution
        gc_content = self._calculate_gc_content(sequence)
        gc_score = 1.0 - abs(gc_content - self.gc_content_target)
        score += gc_score * 0.4
        
        # Unstable motif penalty
        unstable_count = sum(sequence.count(motif) for motif in self.unstable_motifs)
        unstable_penalty = min(1.0, unstable_count * 0.1)
        score -= unstable_penalty * 0.3
        
        # Stable motif bonus
        stable_count = sum(sequence.count(motif) for motif in self.stable_motifs)
        stable_bonus = min(1.0, stable_count * 0.05)
        score += stable_bonus * 0.3
        
        return max(0.0, min(1.0, score))


class DeliveryOptimizer:
    """Optimizes mRNA for delivery and translation efficiency."""
    
    def __init__(self):
        self.utr_sequences = self._load_utr_sequences()
        self.kozak_sequence = 'GCCACC'
        self.poly_a_tail = 'A' * 100  # 100-200 A's typical
    
    def _load_utr_sequences(self) -> Dict[str, str]:
        """Load optimized UTR sequences."""
        return {
            '5_prime_utr': 'GCCGCCACC',
            '3_prime_utr': 'AAUAAA'  # Polyadenylation signal
        }
    
    def design_construct(
        self, 
        coding_sequence: str, 
        neoantigens: List[str]
    ) -> MRNAConstruct:
        """
        Design complete mRNA construct with all optimizations.
        
        Args:
            coding_sequence: Optimized coding sequence
            neoantigens: List of neoantigen sequences
            
        Returns:
            Complete mRNA construct
        """
        optimizations_applied = []
        
        # 1. Add UTRs
        utr_construct = self._add_utrs(coding_sequence)
        optimizations_applied.append("Added optimized UTRs")
        
        # 2. Add Kozak sequence
        kozak_construct = self._add_kozak_sequence(utr_construct)
        optimizations_applied.append("Added Kozak sequence")
        
        # 3. Add poly-A tail
        poly_a_construct = self._add_poly_a_tail(kozak_construct)
        optimizations_applied.append("Added poly-A tail")
        
        # 4. Optimize for delivery
        delivery_construct = self._optimize_for_delivery(poly_a_construct)
        optimizations_applied.append("Optimized for delivery")
        
        # Calculate scores
        gc_content = self._calculate_gc_content(delivery_construct)
        stability_score = StabilityOptimizer().calculate_stability_score(delivery_construct)
        immunogenicity_score = self._calculate_immunogenicity_score(delivery_construct, neoantigens)
        delivery_efficiency = self._calculate_delivery_efficiency(delivery_construct)
        
        return MRNAConstruct(
            sequence=delivery_construct,
            length=len(delivery_construct),
            gc_content=gc_content,
            stability_score=stability_score,
            immunogenicity_score=immunogenicity_score,
            delivery_efficiency=delivery_efficiency,
            neoantigens=neoantigens,
            u_tr_regions=self.utr_sequences,
            optimizations_applied=optimizations_applied
        )
    
    def _add_utrs(self, sequence: str) -> str:
        """Add 5' and 3' UTR sequences."""
        return self.utr_sequences['5_prime_utr'] + sequence + self.utr_sequences['3_prime_utr']
    
    def _add_kozak_sequence(self, sequence: str) -> str:
        """Add Kozak sequence for translation initiation."""
        # Insert after 5' UTR
        utr_len = len(self.utr_sequences['5_prime_utr'])
        return sequence[:utr_len] + self.kozak_sequence + sequence[utr_len:]
    
    def _add_poly_a_tail(self, sequence: str) -> str:
        """Add poly-A tail for stability."""
        return sequence + self.poly_a_tail
    
    def _optimize_for_delivery(self, sequence: str) -> str:
        """Optimize sequence for lipid nanoparticle delivery."""
        # Simplified optimization - in practice would use more sophisticated methods
        optimizer = StabilityOptimizer()
        return optimizer.optimize_stability(sequence)
    
    def _calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content percentage."""
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence) if sequence else 0
    
    def _calculate_immunogenicity_score(self, sequence: str, neoantigens: List[str]) -> float:
        """Calculate immunogenicity score based on sequence and neoantigens."""
        score = 0.0
        
        # Base score from neoantigens
        score += min(1.0, len(neoantigens) * 0.2)
        
        # Sequence-based immunogenicity
        u_content = sequence.count('U') / len(sequence)
        score += u_content * 0.3
        
        # Avoid excessive immunogenicity (to prevent cytokine storm)
        if score > 0.8:
            score = 0.8
        
        return score
    
    def _calculate_delivery_efficiency(self, sequence: str) -> float:
        """Calculate predicted delivery efficiency."""
        # Factors affecting delivery efficiency
        length_factor = min(1.0, len(sequence) / 3000)  # Optimal length ~3kb
        gc_factor = 1.0 - abs(self._calculate_gc_content(sequence) - 0.55) * 2
        stability_factor = StabilityOptimizer().calculate_stability_score(sequence)
        
        return (length_factor + gc_factor + stability_factor) / 3


class MRNAVaccineDesigner:
    """Main class for designing personalized mRNA cancer vaccines."""
    
    def __init__(self):
        self.codon_optimizer = CodonOptimizer()
        self.stability_optimizer = StabilityOptimizer()
        self.delivery_optimizer = DeliveryOptimizer()
    
    def design_vaccine(
        self, 
        neoantigens: List[str],
        include_self_learning: bool = True
    ) -> MRNAConstruct:
        """
        Design personalized mRNA vaccine for neoantigens.
        
        Args:
            neoantigens: List of neoantigen peptide sequences
            include_self_learning: Whether to include self-learning optimizations
            
        Returns:
            Designed mRNA construct
        """
        # Combine neoantigens into single sequence with linkers
        combined_sequence = self._combine_neoantigens(neoantigens)
        
        # Optimize codons
        codon_opt = self.codon_optimizer.optimize_sequence(combined_sequence)
        optimized_sequence = codon_opt.optimized_sequence
        
        # Optimize stability
        stable_sequence = self.stability_optimizer.optimize_stability(optimized_sequence)
        
        # Design complete construct
        construct = self.delivery_optimizer.design_construct(stable_sequence, neoantigens)
        
        # Apply self-learning optimizations if enabled
        if include_self_learning:
            construct = self._apply_self_learning_optimizations(construct, neoantigens)
        
        return construct
    
    def _combine_neoantigens(self, neoantigens: List[str]) -> str:
        """Combine multiple neoantigens into single coding sequence."""
        if not neoantigens:
            return ""
        
        # Use flexible linkers between neoantigens
        linker = "GGGGS"  # (Gly-Gly-Gly-Gly-Ser) flexible linker
        
        combined = neoantigens[0]
        for neoantigen in neoantigens[1:]:
            combined += linker + neoantigen
        
        return combined
    
    def _apply_self_learning_optimizations(
        self, 
        construct: MRNAConstruct, 
        neoantigens: List[str]
    ) -> MRNAConstruct:
        """Apply self-learning based optimizations."""
        # This would integrate with the SML system for continuous improvement
        # For now, apply additional optimizations based on construct properties
        
        sequence = construct.sequence
        
        # Additional stability optimization
        if construct.stability_score < 0.7:
            sequence = self.stability_optimizer.optimize_stability(sequence)
        
        # Additional codon optimization if expression score is low
        if construct.immunogenicity_score < 0.5:
            # This is a simplified approach - in practice would use ML models
            sequence = self._enhance_expression(sequence)
        
        # Recalculate scores
        gc_content = self.delivery_optimizer._calculate_gc_content(sequence)
        stability_score = self.stability_optimizer.calculate_stability_score(sequence)
        immunogenicity_score = self.delivery_optimizer._calculate_immunogenicity_score(sequence, neoantigens)
        delivery_efficiency = self.delivery_optimizer._calculate_delivery_efficiency(sequence)
        
        construct.sequence = sequence
        construct.gc_content = gc_content
        construct.stability_score = stability_score
        construct.immunogenicity_score = immunogenicity_score
        construct.delivery_efficiency = delivery_efficiency
        construct.optimizations_applied.append("Self-learning optimizations applied")
        
        return construct
    
    def _enhance_expression(self, sequence: str) -> str:
        """Enhance expression through additional optimizations."""
        # Add internal ribosome entry sites (IRES) if needed
        # Add additional stabilizing elements
        # This is a simplified version
        
        result = list(sequence)
        
        # Add stabilizing elements at regular intervals
        for i in range(0, len(result), 500):
            if i < len(result):
                result.insert(i, "GGGCGG")
        
        return ''.join(result)
    
    def generate_vaccine_report(self, construct: MRNAConstruct) -> Dict[str, any]:
        """Generate comprehensive vaccine design report."""
        return {
            'construct_length': construct.length,
            'gc_content': f"{construct.gc_content:.2%}",
            'stability_score': f"{construct.stability_score:.2f}",
            'immunogenicity_score': f"{construct.immunogenicity_score:.2f}",
            'delivery_efficiency': f"{construct.delivery_efficiency:.2f}",
            'neoantigen_count': len(construct.neoantigens),
            'optimizations_applied': construct.optimizations_applied,
            'sequence_preview': construct.sequence[:100] + "..." if len(construct.sequence) > 100 else construct.sequence,
            'recommended_dose': self._calculate_recommended_dose(construct),
            'storage_conditions': "Store at -80 degC, avoid freeze-thaw cycles"
        }
    
    def _calculate_recommended_dose(self, construct: MRNAConstruct) -> str:
        """Calculate recommended vaccine dose."""
        # Simplified dose calculation based on construct properties
        base_dose = 50  # micrograms
        
        # Adjust based on immunogenicity
        dose_factor = 1.0 + (1.0 - construct.immunogenicity_score)
        
        # Adjust based on delivery efficiency
        dose_factor *= 1.0 + (1.0 - construct.delivery_efficiency)
        
        recommended_dose = base_dose * dose_factor
        
        return f"{recommended_dose:.0f} ug per dose"