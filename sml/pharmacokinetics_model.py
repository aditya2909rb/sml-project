"""
Pharmacokinetics and Clinical Delivery Modeling

Implements mRNA vaccine delivery and pharmacokinetics:
- Lipid nanoparticle (LNP) formulation optimization
- Biodistribution prediction
- Protein expression kinetics
- Duration of immune response
- Dosing schedules
- Clinical trial design support

References:
- Kon et al. (2021) - LNP-mRNA biodistribution
- Pardi et al. (2018) - mRNA vaccine design strategies
- Moderna/BioNTech manufacturing & clinical protocols
- FDA guidance on gene therapy products
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class DeliveryRoute(Enum):
    """mRNA vaccine delivery route."""
    INTRAMUSCULAR = "IM"  # Standard vaccine route
    INTRAVENOUS = "IV"  # Systemic delivery
    INTRADERMAL = "ID"  # Skin-targeted
    SUBCUTANEOUS = "SC"  # Subcutaneous


class LNPComposition(Enum):
    """Lipid nanoparticle formulation."""
    MRNA_1273 = "mRNA-1273"  # Moderna formulation (similar)
    BNTX162B1 = "BNT162b1"  # BioNTech formulation (similar)
    CUSTOM = "custom"


@dataclass
class LNPFormulation:
    """LNP composition and properties."""
    name: str
    mrna_percentage: float  # % of total mass
    lipid_composition: Dict[str, float]  # Ionizable:Cholesterol:PEG:DSPE ratio
    particle_size_nm: float  # Nanometers
    pdI: float  # Polydispersity index (0-1)
    zeta_potential_mv: float  # mV
    encapsulation_efficiency: float  # 0-1
    

@dataclass
class PharmacokineticsProfile:
    """Complete PK profile for mRNA vaccine."""
    # Absorption
    cmax_protein_per_mg: float  # Peak protein (µg per mg mRNA)
    tmax_hours: float  # Time to peak
    auc_protein_µgh_per_mg: float  # Area under curve
    
    # Distribution
    half_life_hours: float  # Elimination half-life
    volume_distribution: float  # L/kg
    lymph_node_drainage_percent: float  # % reaching lymph nodes
    spleen_accumulation_percent: float  # % reaching spleen
    hepatic_clearance_percent: float  # % cleared by liver
    
    # Metabolism
    rnase_susceptibility: float  # 0-1 (lower = more stable)
    innate_immune_activation: float  # 0-1 (TLR activation)
    
    # Immunogenicity
    t_cell_infiltration_peak_days: int
    antibody_response_peak_days: int
    memory_response_durability_months: int
    
    # Clinical recommendations
    dose_µg: float  # Recommended dose
    dose_schedule_days: List[int]  # Days for prime-boost schedule
    duration_protection_months: int


class Pharmacokineticsmodeler:
    """
    Model mRNA vaccine pharmacokinetics and clinical efficacy.
    """
    
    def __init__(self):
        self.lnp_formulations = self._load_lnp_formulations()
        self.protein_expression_model = self._load_protein_expression_model()
        self.immune_response_model = self._load_immune_response_model()
        
    def _load_lnp_formulations(self) -> Dict[str, LNPFormulation]:
        """Load clinical LNP formulation data."""
        return {
            'mRNA-1273': LNPFormulation(
                name='mRNA-1273 (Spikevax-like)',
                mrna_percentage=40.0,  # 40% of LNP mass
                lipid_composition={
                    'SM-102': 0.355,  # Ionizable lipid
                    'cholesterol': 0.309,
                    'PEG': 0.020,
                    'DSPE': 0.076,
                    'PEG-lipid': 0.240,
                },
                particle_size_nm=100,  # 95-125 nm typical
                pdI=0.08,
                zeta_potential_mv=3.5,
                encapsulation_efficiency=0.95,  # 95%
            ),
            'BNT162': LNPFormulation(
                name='BNT162b1 (Comirnaty-like)',
                mrna_percentage=38.0,
                lipid_composition={
                    'ALC-0315': 0.373,
                    'cholesterol': 0.313,
                    'PEG': 0.020,
                    'DSPE': 0.074,
                    'PEG-lipid': 0.220,
                },
                particle_size_nm=95,
                pdI=0.07,
                zeta_potential_mv=2.8,
                encapsulation_efficiency=0.94,
            ),
        }
    
    def _load_protein_expression_model(self) -> Dict[str, any]:
        """Mathematical model for protein expression kinetics."""
        return {
            'baseline_expression_µg_per_mg': 15.0,  # At day 1
            'peak_expression_day': 2,  # Peak expression timing
            'peak_expression_multiplier': 3.5,  # 3.5x baseline
            'mrna_half_life_hours': 10.0,
            'decline_rate': 0.07,  # Per hour after peak
        }
    
    def _load_immune_response_model(self) -> Dict[str, any]:
        """Model for adaptive immune response."""
        return {
            't_cell_response_peak': 7,  # Days
            'antibody_response_peak': 14,  # Days
            'memory_establishment': 21,  # Days
            'primary_coverage': 0.65,  # % of population responding
            'prime_boost_enhancement': 10,  # x fold increase
        }
    
    def model_pharmacokinetics(
        self,
        mrna_dose_µg: float,
        delivery_route: DeliveryRoute = DeliveryRoute.INTRAMUSCULAR,
        lnp_formulation: str = 'mRNA-1273',
        patient_demographics: Optional[Dict] = None,
    ) -> PharmacokineticsProfile:
        """
        Model complete pharmacokinetics for mRNA vaccine.
        
        Args:
            mrna_dose_µg: mRNA dose in micrograms
            delivery_route: Route of administration
            lnp_formulation: LNP type
            patient_demographics: Age, weight, renal function
            
        Returns:
            PharmacokineticsProfile
        """
        if patient_demographics is None:
            patient_demographics = {
                'age': 40,  # years
                'weight': 70,  # kg
                'renal_function': 'normal',
            }
        
        # Load formulation
        lnp = self.lnp_formulations.get(lnp_formulation)
        if not lnp:
            lnp = self.lnp_formulations['mRNA-1273']
        
        # 1. Absorption
        cmax, tmax, auc = self._calculate_absorption(
            mrna_dose_µg, delivery_route, lnp
        )
        
        # 2. Distribution
        half_life, vol_dist = self._calculate_distribution(
            delivery_route, patient_demographics
        )
        
        lymph_drainage, spleen_acc, hepatic = self._calculate_tissue_distribution(
            delivery_route
        )
        
        # 3. Metabolism
        rnase_susceptibility = self._estimate_rnase_susceptibility()
        innate_activation = self._estimate_innate_immune_activation(mrna_dose_µg)
        
        # 4. Immune response
        tcell_peak, ab_peak, memory_duration = self._model_immune_response(
            mrna_dose_µg, cmax, patient_demographics
        )
        
        # 5. Clinical recommendations
        dose_schedule = self._recommend_dose_schedule(
            mrna_dose_µg, tcell_peak, ab_peak
        )
        
        protection_duration = self._estimate_protection_duration(
            memory_duration, patient_demographics
        )
        
        return PharmacokineticsProfile(
            cmax_protein_per_mg=cmax,
            tmax_hours=tmax,
            auc_protein_µgh_per_mg=auc,
            half_life_hours=half_life,
            volume_distribution=vol_dist,
            lymph_node_drainage_percent=lymph_drainage,
            spleen_accumulation_percent=spleen_acc,
            hepatic_clearance_percent=hepatic,
            rnase_susceptibility=rnase_susceptibility,
            innate_immune_activation=innate_activation,
            t_cell_infiltration_peak_days=tcell_peak,
            antibody_response_peak_days=ab_peak,
            memory_response_durability_months=memory_duration,
            dose_µg=mrna_dose_µg,
            dose_schedule_days=dose_schedule,
            duration_protection_months=protection_duration,
        )
    
    def _calculate_absorption(
        self,
        dose_µg: float,
        route: DeliveryRoute,
        lnp: LNPFormulation
    ) -> Tuple[float, float, float]:
        """Calculate drug absorption kinetics."""
        
        pk_model = self.protein_expression_model
        
        # Baseline expression
        dose_normalized = dose_µg / 30.0  # Normalize to 30 µg standard
        
        # Route-specific absorption
        route_absorption_factor = {
            DeliveryRoute.INTRAMUSCULAR: 1.0,
            DeliveryRoute.INTRAVENOUS: 2.5,  # Faster, higher peak
            DeliveryRoute.INTRADERMAL: 0.7,  # Local response
            DeliveryRoute.SUBCUTANEOUS: 0.85,
        }
        
        factor = route_absorption_factor.get(route, 1.0)
        
        # Cmax (peak protein concentration)
        cmax = pk_model['baseline_expression_µg_per_mg'] * dose_normalized * factor * lnp.encapsulation_efficiency
        cmax = cmax * pk_model['peak_expression_multiplier']
        
        # Tmax (time to peak)
        tmax = pk_model['peak_expression_day'] + (0.5 if route == DeliveryRoute.INTRADERMAL else 0)
        
        # AUC (area under curve)
        # Approximate using trapezoidal rule with exponential decline
        auc = cmax * pk_model['mrna_half_life_hours'] / math.log(2) * 1.5  # Heuristic
        
        return cmax, tmax, auc
    
    def _calculate_distribution(
        self,
        route: DeliveryRoute,
        demographics: Dict
    ) -> Tuple[float, float]:
        """Calculate distribution parameters."""
        
        # Half-life depends on route and patient
        half_life_base = 10.0  # hours
        
        # Age factor
        age_factor = 1.0 + (demographics['age'] - 40) * 0.01
        
        # Route factor
        route_half_life = {
            DeliveryRoute.INTRAMUSCULAR: 1.0,
            DeliveryRoute.INTRAVENOUS: 0.5,  # Faster clearance
            DeliveryRoute.INTRADERMAL: 1.5,  # More local retention
            DeliveryRoute.SUBCUTANEOUS: 1.2,
        }
        
        half_life = half_life_base * route_half_life.get(route, 1.0) * age_factor
        
        # Volume of distribution (L/kg)
        weight = demographics['weight']
        vd = 0.3 + (weight / 70.0 - 1) * 0.1  # Adjust for weight
        
        return half_life, vd
    
    def _calculate_tissue_distribution(self, route: DeliveryRoute) -> Tuple[float, float, float]:
        """Calculate organ-specific distribution."""
        
        distribution_map = {
            DeliveryRoute.INTRAMUSCULAR: {
                'lymph_nodes': 35,  # %
                'spleen': 20,
                'liver': 25,
            },
            DeliveryRoute.INTRAVENOUS: {
                'lymph_nodes': 15,
                'spleen': 40,
                'liver': 35,
            },
            DeliveryRoute.INTRADERMAL: {
                'lymph_nodes': 60,  # Enhanced lymph drainage
                'spleen': 10,
                'liver': 10,
            },
            DeliveryRoute.SUBCUTANEOUS: {
                'lymph_nodes': 40,
                'spleen': 15,
                'liver': 25,
            },
        }
        
        dist = distribution_map.get(route)
        if not dist:
            dist = distribution_map[DeliveryRoute.INTRAMUSCULAR]
        
        return (
            dist['lymph_nodes'],
            dist['spleen'],
            dist['liver'],
        )
    
    def _estimate_rnase_susceptibility(self) -> float:
        """Estimate RNase degradation resistance."""
        # 0 = fully resistant, 1 = fully susceptible
        # Optimized mRNA with 2'-OMe and pseudouridine: ~0.15
        return 0.15
    
    def _estimate_innate_immune_activation(self, dose_µg: float) -> float:
        """Estimate TLR3/7/8 activation."""
        # Dose-dependent, but minimized with pseudouridine + optimization
        # 30 µg reference
        dose_factor = (dose_µg / 30.0) * 0.5
        return min(dose_factor + 0.2, 1.0)
    
    def _model_immune_response(
        self,
        dose_µg: float,
        cmax: float,
        demographics: Dict
    ) -> Tuple[int, int, int]:
        """Model adaptive immune response kinetics."""
        
        ir_model = self.immune_response_model
        
        # Dose effect
        dose_effect = 1.0 + (dose_µg / 30.0 - 1) * 0.3
        
        # Age effect (immunosenescence)
        age_effect = 1.0 - (demographics['age'] - 40) * 0.01 if demographics['age'] > 40 else 1.0
        age_effect = max(age_effect, 0.6)  # Minimum 60% of young adult response
        
        # Cmax effect (protein expression)
        cmax_effect = min(cmax / 50.0, 2.0)  # Saturation at high levels
        
        combined_effect = dose_effect * age_effect * cmax_effect
        
        # T-cell response timing
        tcell_peak = max(5, int(ir_model['t_cell_response_peak'] / combined_effect))
        
        # Antibody response timing
        ab_peak = max(10, int(ir_model['antibody_response_peak'] / combined_effect))
        
        # Memory durability
        memory_months = int(ir_model['memory_establishment'] / combined_effect * 2)  # 1-2 years typical
        
        return tcell_peak, ab_peak, memory_months
    
    def _recommend_dose_schedule(
        self,
        dose_µg: float,
        tcell_peak: int,
        ab_peak: int
    ) -> List[int]:
        """
        Recommend prime-boost schedule.
        Typical: Day 0 (prime), Day 21-28 (boost).
        """
        boost_day = ab_peak + 7  # ~3-4 weeks
        
        return [0, boost_day]
    
    def _estimate_protection_duration(
        self,
        memory_months: int,
        demographics: Dict
    ) -> int:
        """Estimate duration of protection."""
        
        # Age factor
        age_discount = 1.0 - (demographics['age'] - 40) * 0.02
        age_discount = max(age_discount, 0.5)
        
        # Memory cells typically provide 6-24 months protection
        protection = max(6, int(memory_months * 0.8 * age_discount))
        
        return protection


@dataclass
class ClinicalTrialDesign:
    """Clinical trial design parameters."""
    phase: str  # Phase 1, 2, 1b/2a
    patient_population: str
    sample_size: int
    primary_endpoints: List[str]
    secondary_endpoints: List[str]
    safety_monitoring: Dict[str, float]
    efficacy_acceptance_criteria: float


class ClinicalTrialDesigner:
    """Design clinical trials for mRNA vaccines."""
    
    @staticmethod
    def design_phase1_trial(
        vaccine_construct_id: str,
        immunogenicity_score: float,
        safety_profile: Dict
    ) -> ClinicalTrialDesign:
        """Design Phase 1 safety trial."""
        
        # Determine sample size based on safety signals
        safety_risk_score = sum(v for v in safety_profile.values()) / len(safety_profile)
        
        if safety_risk_score < 0.2:
            sample_size = 30  # Low risk
        elif safety_risk_score < 0.4:
            sample_size = 50
        else:
            sample_size = 80  # Higher risk
        
        return ClinicalTrialDesign(
            phase="Phase 1",
            patient_population="Healthy adults 18-55",
            sample_size=sample_size,
            primary_endpoints=[
                "Dose safety/tolerability",
                "Local/systemic adverse events",
            ],
            secondary_endpoints=[
                "Immune response (antibodies)",
                "T-cell response (IFN-γ)",
                "Neut antibody titer",
            ],
            safety_monitoring={
                "AE grading": 0.3,
                "Grade 3+ AE": 0.1,
                "SAE": 0.05,
            },
            efficacy_acceptance_criteria=0.5,  # Any seroconversion acceptable
        )
    
    @staticmethod
    def design_phase2_trial(
        vaccine_construct_id: str,
        immunogenicity_score: float,
        hla_diversity: float
    ) -> ClinicalTrialDesign:
        """Design Phase 2 efficacy signal trial."""
        
        # Calculate sample size for efficacy
        # Based on immunogenicity score and HLA diversity
        target_responder_rate = min(0.65, immunogenicity_score)
        
        # n = (Z_α/2 + Z_β)² * p(1-p) / (p - p0)²
        # Simplified: n ≈ 50-200 depending on endpoint
        sample_size = max(50, int(200 * (1 - target_responder_rate)))
        
        return ClinicalTrialDesign(
            phase="Phase 2",
            patient_population="Patients with advanced cancer",
            sample_size=sample_size,
            primary_endpoints=[
                "Immunogenicity (neoantigen-specific T-cells)",
                "Safety in target population",
            ],
            secondary_endpoints=[
                "Recurrence-free survival",
                "Overall survival",
                "Immune checkpoint kinetics",
            ],
            safety_monitoring={
                "Grade 2+ AE": 0.15,
                "Grade 3+ AE": 0.05,
            },
            efficacy_acceptance_criteria=target_responder_rate,
        )
