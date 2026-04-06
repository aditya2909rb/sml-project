"""
Advanced mRNA Cancer Vaccine Research System - User Guide

OVERVIEW
--------
The OncoSML Advanced mRNA Vaccine Research System is a production-grade platform 
for designing personalized neoantigen-based cancer vaccines. It combines 
state-of-the-art computational immunology, molecular biology, and clinical 
trial design methodologies.

CORE CAPABILITIES
-----------------

1. ADVANCED IMMUNOGENICITY PREDICTION
   - Multi-factor immunogenicity scoring
   - MHC-peptide binding thermodynamics
   - TCR contact residue analysis
   - B-cell epitope propensity
   - Population-level MHC diversity coverage
   - Neoantigen advantage scoring

2. CLINICAL-GRADE HLA BINDING PREDICTION
   - Position-specific scoring matrices (PSSM)
   - Allele-specific pocket models
   - Machine learning ensemble approach
   - Percentile ranking vs. decoys
   - Clinical responder probability
   - Confidence metrics

3. ADVANCED mRNA OPTIMIZATION
   - Dendritic cell-optimized codon bias
   - GC content balancing (40-60% optimal)
   - Secondary structure minimization
   - Rare codon elimination
   - Immunostimulatory pattern removal
   - Kozak consensus optimization
   - UTR design for stability

4. PHARMACOKINETICS MODELING
   - mRNA absorption kinetics
   - Protein expression dynamics  
   - Tissue-specific distribution
   - T-cell and B-cell response timing
   - Prime-boost schedule optimization
   - Duration of protection estimation

5. CLINICAL TRIAL VALIDATOR
   - GMP manufacturing readiness
   - Clinical trial eligibility criteria
   - Safety threshold validation
   - Efficacy predictions
   - Regulatory compliance assessment
   - Go/No-go recommendation

6. COMPREHENSIVE RESEARCH REPORTING
   - Publication-ready scientific reports
   - Executive summaries
   - Quality control metrics
   - Safety profiles
   - Manufacturing specifications
   - Regulatory pathway guidance

INSTALLATION & SETUP
--------------------

# 1. Ensure Python 3.8+
python --version

# 2. Install required packages
pip install -r requirements.txt

# 3. Configure Python environment
python -m sml.config --setup

QUICK START
-----------

### Basic Usage
from sml.advanced_vaccine_pipeline import AdvancedVaccineDesignPipeline

# Initialize pipeline
pipeline = AdvancedVaccineDesignPipeline(model_dir="model_store")

# Define patient data
neoantigen_peptides = [
    "AEFGPWQTYS",  # Candidate 1
    "KLLLTQQ",      # Candidate 2
    "LLCVGVSR",     # Candidate 3
]

patient_hla_alleles = [
    "HLA-A*02:01",
    "HLA-B*07:02", 
    "HLA-C*07:02"
]

# Run full analysis
results = pipeline.design_vaccine_candidate(
    sample_id="PATIENT_001",
    neoantigen_peptides=neoantigen_peptides,
    patient_hla_alleles=patient_hla_alleles,
    target_gc_content=50.0,
)

# Get summary
summary = pipeline.create_summary_report(results)
print(summary)

DETAILED MODULE USAGE
---------------------

### 1. Immunogenicity Prediction
from sml.advanced_immunogenicity import AdvancedImmunogenicityPredictor

predictor = AdvancedImmunogenicityPredictor()

profile = predictor.predict_immunogenicity(
    peptide="AEFGPWQTYS",
    mhc_binding_affinity=150,  # nM
    mutation_context="AEFGPWLTYS",  # Wild-type for comparison
    hla_allele="HLA-A*02:01",
    population_mhc_types=["HLA-A*02:01", "HLA-A*01:01", "HLA-B*07:02"]
)

print(f"Immunogenicity: {profile.overall_immunogenicity:.2%}")
print(f"Classification: {profile.classification.value}")
print(f"Evidence: {profile.supporting_evidence}")
print(f"Confidence: {profile.research_confidence:.1%}")

### 2. HLA Binding Prediction  
from sml.clinical_hla_binding import ClinicalHLAPredictor

predictor = ClinicalHLAPredictor()

prediction = predictor.predict_binding(
    peptide="AEFGPWQTYS",
    hla_allele="HLA-A*02:01",
    all_alleles=["HLA-A*02:01", "HLA-B*07:02"]
)

print(f"Affinity: {prediction.binding_affinity_nm:.1f} nM")
print(f"Percentile: {prediction.binding_percentile:.1f}%")
print(f"Strength: {prediction.binding_strength.value}")
print(f"Responder Probability: {prediction.responder_probability:.1%}")
print(f"Clinical Candidate: {prediction.is_clinical_candidate}")

### 3. mRNA Optimization
from sml.advanced_mrna_optimization import AdvancedmRNAOptimizer, OptimizationLevel

optimizer = AdvancedmRNAOptimizer()

construct = optimizer.optimize_mrna_sequence(
    amino_acid_sequence="AEFGPWQTYS" * 5,  # Multi-epitope
    optimization_level=OptimizationLevel.ADVANCED,
    target_gc_content=50.0,
    include_utrs=True
)

print(f"Sequence Length: {len(construct.optimized_mrna)} nt")
print(f"GC Content: {construct.gc_content:.1f}%")
print(f"Codon Score: {construct.codon_optimization_score:.1%}")
print(f"Expression: {construct.predicted_expression_level:.1%}")
print(f"Stability: {construct.mrna_stability_hours:.1f} hours")

### 4. Pharmacokinetics Modeling
from sml.pharmacokinetics_model import Pharmacokineticsmodeler, DeliveryRoute

modeler = Pharmacokineticsmodeler()

pk = modeler.model_pharmacokinetics(
    mrna_dose_µg=30.0,
    delivery_route=DeliveryRoute.INTRAMUSCULAR,
    lnp_formulation='mRNA-1273',
    patient_demographics={
        'age': 65,
        'weight': 75,
        'renal_function': 'normal'
    }
)

print(f"Peak Protein: {pk.cmax_protein_per_mg:.1f} µg/mg mRNA")
print(f"Time to Peak: {pk.tmax_hours:.1f} hours")
print(f"Half-life: {pk.half_life_hours:.1f} hours")
print(f"Lymph Node Drainage: {pk.lymph_node_drainage_percent:.0f}%")
print(f"T-cell Response Peak: Day {pk.t_cell_infiltration_peak_days}")
print(f"Protection Duration: {pk.duration_protection_months} months")

### 5. Clinical Trial Validation
from sml.clinical_trial_validator import ClinicalTrialValidator

validator = ClinicalTrialValidator()

report = validator.assess_clinical_readiness(
    vaccine_id="ONCO-mRNA-001",
    mrna_sequence="AUGCGC...",  # Your sequence
    gc_content=50.5,
    secondary_structure_energy=-1.5,
    immunogenicity_score=0.78,
    predicted_responder_rate=0.68,
    safety_profile={
        'off_target_binding_risk': 0.12,
        'immunostimulation_level': 0.25,
        'genomic_integration_risk': 0.001,
        'lnp_toxicity_risk': 0.08
    },
    hla_coverage=0.72
)

print(f"Eligibility: {report.trial_eligibility.value}")
print(f"Recommendation: {report.go_no_go_recommendation}")
print(f"GMP Readiness: {report.gmp_readiness_percent:.0f}%")
print(f"Safety Grade: {report.safety_assessment.safety_grade}")

### 6. Report Generation
from sml.comprehensive_reporting import ComprehensiveReportGenerator, ReportFormat

generator = ComprehensiveReportGenerator()

report = generator.generate_full_report(
    vaccine_id="ONCO-mRNA-001",
    patient_id="PATIENT_001",
    immunogenicity_profile={...},
    hla_predictions={...},
    mrna_construct={...},
    pharmacokinetics={...},
    clinical_readiness={...},
    neoantigen_candidates=[...],
    output_format=ReportFormat.MARKDOWN
)

# Save to file
with open("vaccine_report.md", "w") as f:
    f.write(report)

COMMAND-LINE INTERFACE
---------------------

# Run complete vaccine design
python main.py run-vaccine-design \\
    --sample-id "PATIENT_001" \\
    --neoantigen-file "neoantigens.txt" \\
    --hla-alleles "HLA-A*02:01,HLA-B*07:02" \\
    --output-dir "results/"

# Generate report only
python main.py generate-report \\
    --results-json "vaccine_design_results.json" \\
    --format markdown \\
    --output "report.md"

# Validate clinical readiness
python main.py validate-clinical \\
    --vaccine-id "ONCO-mRNA-001" \\
    --mrna-sequence "AUGCGC..." \\
    --safety-profile "safety.json"

DATA REQUIREMENTS
-----------------

### Neoantigen Input
- Format: CSV or JSON
- Columns: peptide_sequence, mutation_position, hla_alleles, binding_affinity_nm
- Quality: High-confidence mutations only (VAF > 15%)

### HLA Typing
- Format: Standard HLA nomenclature (e.g., HLA-A*02:01)
- Source: High-resolution typing (4-digit minimum)
- Coverage: Class I (A, B, C) minimum

### mRNA Sequence
- Format: FASTA or plain text
- Orientation: 5' to 3'
- Codon: Standard genetic code
- Content: Coding sequence only (UTRs designed system)

OUTPUT FILES
-----------

vaccine_design_SAMPLE_ID_TIMESTAMP.json
  └─ Complete analysis results in JSON format
  └─ All scores, profiles, and intermediate steps
  └─ Machine-readable for downstream processing

vaccine_report_SAMPLE_ID_TIMESTAMP.md
  └─ Publication-ready Markdown report
  └─ Executive summary, methods, results
  └─ Quality control metrics, safety assessment
  └─ Manufacturing specifications

vaccine_report_SAMPLE_ID_TIMESTAMP.html
  └─ Formatted HTML report for viewing
  └─ Interactive tables and visualizations
  └─ Print-ready layout

VALIDATION & QUALITY CONTROL
----------------------------

All results are validated against:

1. Sequence Quality
   - GC content: 40-60%
   - Homopolymer runs: ≤4 consecutive
   - In-frame stop codons: 0
   - Kozak optimization: Present

2. Safety
   - Off-target binding risk: < 30%
   - Genomic integration: < 1%
   - Immunostimulation: < 50% TLR activation
   - LNP toxicity: < 20% risk

3. Clinical Relevance
   - MHC binding: < 500 nM (strong) or < 5000 nM (weak)
   - Immunogenicity: Top 20% of predicted candidates
   - Population coverage: > 50% of global MHC diversity
   - Responder probability: > 50%

TROUBLESHOOTING
---------------

### Low Immunogenicity Scores
- Check: neoantigen peptides contain significant mutations
- Action: Add WT peptide comparison data
- Solution: Try different HLA allele combinations

### GMP Readiness Below 70%
- Check: Manufacturing process documentation
- Action: Complete analytical method development
- Solution: Establish stability testing program

### Safety Warnings
- Check: mRNA sequence for immunostimulatory patterns
- Action: Run additional secondary structure optimization
- Solution: Consider alternative codon selections

REGULATORY COMPLIANCE
--------------------

This system follows:
- FDA guidance on gene therapy products (2019)
- ICH Q9 Risk Management principles
- GMP manufacturing standards (Ph.Eur. / USP)
- Clinical trial design best practices

Output documentation is suitable for:
- IND (Investigational New Drug) applications
- Clinical trial protocols
- Manufacturing quality dossiers
- Regulatory submissions

PERFORMANCE METRICS
------------------

Typical Runtime:
- Immunogenicity analysis: 1-2 minutes (50 peptides)
- HLA binding prediction: 30 seconds per peptide per HLA
- mRNA optimization: 2-5 minutes
- PK modeling: < 1 minute
- Report generation: 30 seconds

Memory Requirements: ~500 MB RAM
Disk Space: ~100 MB for model data

CITATION & REFERENCES
---------------------

When publishing results from this system, cite:

"OncoSML Advanced mRNA Vaccine Pipeline v1.0
Built on validated algorithms:
- Nielsen et al. (2003) NetMHC
- Karosiene et al. (2012) NetMHCpan
- Gustafsson et al. (2004) Codon optimization
- Pardi et al. (2018) mRNA vaccine design"

Key References:
1. Moderna COVID-19 vaccine clinical reports
2. BioNTech/Pfizer vaccine publications
3. Cancer Research Institute neoantigen guidelines
4. FDA gene therapy guidance documents

SUPPORT & FEEDBACK
------------------

For issues, feature requests, or scientific discussion:
- GitHub: [project repository]
- Email: research@oncosml.org
- Documentation: [full documentation]

---

**Version:** 1.0.0
**Last Updated:** 2026-03-27
**Status:** Advanced Research Grade
"""
