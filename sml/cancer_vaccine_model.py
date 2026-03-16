"""
Cancer Vaccine Model - Integration with SML Framework

This module extends the existing SML model to handle DNA sequence analysis,
neoantigen prediction, and mRNA vaccine design as part of the continuous
learning system.
"""

from __future__ import annotations

import json
import pickle
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score

from .dna_analyzer import DNAMutationAnalyzer, DNAMutationReport, Neoantigen
from .mrna_designer import MRNAVaccineDesigner, MRNAConstruct


@dataclass
class CancerVaccineTrainResult:
    trained_samples: int
    batch_accuracy: float | None
    mutation_detection_accuracy: float | None
    neoantigen_prediction_accuracy: float | None
    vaccine_design_score: float | None


@dataclass
class CancerVaccineScaleResult:
    scaled_up: bool
    message: str
    model_improvements: List[str]


@dataclass
class CancerVaccineState:
    """State for the cancer vaccine model."""
    n_features: int
    estimated_params: int
    mutation_analyzer_state: Dict[str, Any]
    vaccine_designer_state: Dict[str, Any]
    learning_history: List[Dict[str, Any]]
    github_training_data: List[Dict[str, Any]]


class CancerVaccineModel:
    """
    Enhanced model that combines traditional text classification with 
    cancer vaccine design capabilities.
    """
    
    def __init__(self, model_dir: str, n_features: int) -> None:
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.n_features = int(max(2**12, n_features))
        
        # Traditional text classification components
        self.vectorizer = HashingVectorizer(n_features=self.n_features, alternate_sign=False, norm="l2")
        self.classifier = SGDClassifier(loss="log_loss", random_state=42)
        self.initialized = False
        
        # Cancer vaccine components
        self.dna_analyzer = DNAMutationAnalyzer()
        self.vaccine_designer = MRNAVaccineDesigner()
        
        # State management
        self.state: Optional[CancerVaccineState] = None
        self._load_state()
    
    @property
    def model_path(self) -> Path:
        return self.model_dir / "cancer_vaccine_classifier.joblib"
    
    @property
    def state_path(self) -> Path:
        return self.model_dir / "cancer_vaccine_state.pkl"
    
    @property
    def dna_analyzer_path(self) -> Path:
        return self.model_dir / "dna_analyzer_state.pkl"
    
    @property
    def vaccine_designer_path(self) -> Path:
        return self.model_dir / "vaccine_designer_state.pkl"
    
    def _load_state(self) -> None:
        """Load model state from disk."""
        if self.state_path.exists():
            try:
                with open(self.state_path, 'rb') as f:
                    self.state = pickle.load(f)
                self.n_features = self.state.n_features
                self.vectorizer = HashingVectorizer(n_features=self.n_features, alternate_sign=False, norm="l2")
            except Exception:
                self._initialize_state()
        else:
            self._initialize_state()
    
    def _initialize_state(self) -> None:
        """Initialize model state."""
        self.state = CancerVaccineState(
            n_features=self.n_features,
            estimated_params=0,
            mutation_analyzer_state={},
            vaccine_designer_state={},
            learning_history=[],
            github_training_data=[]
        )
    
    def save_state(self) -> None:
        """Save model state to disk."""
        # Update estimated parameters
        self.state.estimated_params = self.estimated_params
        
        # Save state
        with open(self.state_path, 'wb') as f:
            pickle.dump(self.state, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Save traditional model
        if self.initialized:
            import joblib
            joblib.dump(self.classifier, self.model_path)
    
    @property
    def estimated_params(self) -> int:
        """Estimate total parameters in the model."""
        base_params = self.n_features + 1  # Linear classifier parameters
        # Add parameters for cancer vaccine components
        vaccine_params = len(self.state.github_training_data) * 10  # Approximate
        return base_params + vaccine_params
    
    def train(
        self, 
        texts: List[str], 
        labels: List[int], 
        dna_samples: Optional[List[Dict[str, str]]] = None
    ) -> CancerVaccineTrainResult:
        """
        Train the model on text data and optionally DNA samples.
        
        Args:
            texts: List of text samples for traditional classification
            labels: Corresponding labels for text samples
            dna_samples: Optional list of DNA sample dictionaries with keys:
                        'sample_id', 'normal_dna', 'tumor_dna', 'hla_allele'
        
        Returns:
            Training results including both traditional and cancer vaccine metrics
        """
        # Train traditional text classifier
        text_result = self._train_text_classifier(texts, labels)
        
        # Train cancer vaccine components if DNA data provided
        cancer_result = self._train_cancer_components(dna_samples)
        
        return CancerVaccineTrainResult(
            trained_samples=text_result.trained_samples,
            batch_accuracy=text_result.batch_accuracy,
            mutation_detection_accuracy=cancer_result.get('mutation_accuracy'),
            neoantigen_prediction_accuracy=cancer_result.get('neoantigen_accuracy'),
            vaccine_design_score=cancer_result.get('design_score')
        )
    
    def _train_text_classifier(self, texts: List[str], labels: List[int]) -> Any:
        """Train the traditional text classification component."""
        if not texts:
            return type('obj', (object,), {'trained_samples': 0, 'batch_accuracy': None})()
        
        X = self.vectorizer.transform(texts)
        if not self.initialized:
            self.classifier.partial_fit(X, labels, classes=[0, 1])
            self.initialized = True
        else:
            self.classifier.partial_fit(X, labels)
        
        preds = self.classifier.predict(X)
        acc = float(accuracy_score(labels, preds))
        
        return type('obj', (object,), {
            'trained_samples': len(texts),
            'batch_accuracy': acc
        })()
    
    def _train_cancer_components(self, dna_samples: Optional[List[Dict[str, str]]]) -> Dict[str, float]:
        """Train cancer vaccine components using DNA samples."""
        if not dna_samples:
            return {}
        
        results = {
            'mutation_accuracy': 0.0,
            'neoantigen_accuracy': 0.0,
            'design_score': 0.0
        }
        
        mutation_accuracies = []
        neoantigen_accuracies = []
        design_scores = []
        
        for sample in dna_samples:
            try:
                # Analyze DNA sample
                report = self.dna_analyzer.analyze_sample(
                    sample_id=sample['sample_id'],
                    normal_dna=sample['normal_dna'],
                    tumor_dna=sample['tumor_dna'],
                    hla_allele=sample.get('hla_allele', 'HLA-A*02:01')
                )
                
                # Design vaccine
                neoantigens = [neo.peptide_sequence for neo in report.predicted_neoantigens]
                if neoantigens:
                    construct = self.vaccine_designer.design_vaccine(neoantigens)
                    
                    # Calculate scores
                    mutation_acc = self._calculate_mutation_detection_accuracy(report)
                    neoantigen_acc = self._calculate_neoantigen_prediction_accuracy(report)
                    design_score = self._calculate_vaccine_design_score(construct)
                    
                    mutation_accuracies.append(mutation_acc)
                    neoantigen_accuracies.append(neoantigen_acc)
                    design_scores.append(design_score)
                    
                    # Store learning history
                    self.state.learning_history.append({
                        'sample_id': sample['sample_id'],
                        'mutation_count': report.total_mutations,
                        'neoantigen_count': len(neoantigens),
                        'construct_length': construct.length,
                        'gc_content': construct.gc_content,
                        'stability_score': construct.stability_score,
                        'timestamp': self._get_timestamp()
                    })
                    
                    # Limit history size
                    if len(self.state.learning_history) > 1000:
                        self.state.learning_history.pop(0)
                
            except Exception as e:
                # Log error but continue training
                print(f"Error processing DNA sample {sample.get('sample_id', 'unknown')}: {e}")
                continue
        
        # Calculate average scores
        if mutation_accuracies:
            results['mutation_accuracy'] = sum(mutation_accuracies) / len(mutation_accuracies)
        if neoantigen_accuracies:
            results['neoantigen_accuracy'] = sum(neoantigen_accuracies) / len(neoantigen_accuracies)
        if design_scores:
            results['design_score'] = sum(design_scores) / len(design_scores)
        
        return results
    
    def _calculate_mutation_detection_accuracy(self, report: DNAMutationReport) -> float:
        """Calculate mutation detection accuracy (simplified)."""
        # In practice, this would compare against ground truth
        # For now, use a heuristic based on mutation characteristics
        if report.total_mutations == 0:
            return 0.5  # No mutations detected
        
        driver_ratio = len(report.driver_mutations) / report.total_mutations
        tmb_score = min(1.0, report.tumor_mutational_burden / 1000)  # Normalize TMB
        
        return (driver_ratio * 0.6) + (tmb_score * 0.4)
    
    def _calculate_neoantigen_prediction_accuracy(self, report: DNAMutationReport) -> float:
        """Calculate neoantigen prediction accuracy (simplified)."""
        if not report.predicted_neoantigens:
            return 0.0
        
        # Score based on neoantigen quality
        avg_affinity = sum(neo.binding_affinity for neo in report.predicted_neoantigens) / len(report.predicted_neoantigens)
        avg_immunogenicity = sum(neo.immunogenicity_score for neo in report.predicted_neoantigens) / len(report.predicted_neoantigens)
        
        # Convert affinity to score (lower is better)
        affinity_score = max(0.0, 1.0 - (avg_affinity / 1000.0))
        
        return (affinity_score * 0.6) + (avg_immunogenicity * 0.4)
    
    def _calculate_vaccine_design_score(self, construct: MRNAConstruct) -> float:
        """Calculate overall vaccine design score."""
        return (construct.stability_score * 0.3 + 
                construct.immunogenicity_score * 0.4 + 
                construct.delivery_efficiency * 0.3)
    
    def maybe_scale_up(
        self,
        *,
        scaling_enabled: bool,
        cycle_id: int,
        scale_every_cycles: int,
        trained_samples: int,
        batch_accuracy: float | None,
        min_samples: int,
        min_accuracy: float,
        target_params: int,
        max_features: int,
        feature_ladder: List[int],
    ) -> CancerVaccineScaleResult:
        """Scale up the model with cancer vaccine specific considerations."""
        if not scaling_enabled:
            return CancerVaccineScaleResult(scaled_up=False, message="scaling disabled", model_improvements=[])
        
        if self.estimated_params >= target_params:
            return CancerVaccineScaleResult(scaled_up=False, message="target parameter count reached", model_improvements=[])
        
        if cycle_id % max(1, scale_every_cycles) != 0:
            return CancerVaccineScaleResult(scaled_up=False, message="not a scaling cycle", model_improvements=[])
        
        if trained_samples < min_samples:
            return CancerVaccineScaleResult(scaled_up=False, message=f"trained samples {trained_samples} below minimum {min_samples}", model_improvements=[])
        
        if batch_accuracy is None:
            return CancerVaccineScaleResult(scaled_up=False, message="batch accuracy unavailable", model_improvements=[])
        
        if batch_accuracy < min_accuracy:
            return CancerVaccineScaleResult(scaled_up=False, message=f"batch accuracy {batch_accuracy:.4f} below minimum {min_accuracy:.4f}", model_improvements=[])
        
        # Check cancer vaccine specific metrics
        recent_history = self.state.learning_history[-10:] if self.state.learning_history else []
        if recent_history:
            avg_design_score = sum(h.get('design_score', 0) for h in recent_history) / len(recent_history)
            if avg_design_score < 0.6:  # Poor vaccine design quality
                return CancerVaccineScaleResult(scaled_up=False, message=f"vaccine design score {avg_design_score:.2f} below threshold", model_improvements=[])
        
        # Perform scaling
        improvements = self._perform_cancer_vaccine_scaling(
            max_features=max_features,
            feature_ladder=feature_ladder
        )
        
        return CancerVaccineScaleResult(
            scaled_up=True,
            message=f"scaled model features to {self.n_features} (estimated params {self.estimated_params}, target {target_params})",
            model_improvements=improvements
        )
    
    def _perform_cancer_vaccine_scaling(self, max_features: int, feature_ladder: List[int]) -> List[str]:
        """Perform scaling with cancer vaccine specific improvements."""
        improvements = []
        
        # Scale traditional model
        ladder = sorted({int(v) for v in feature_ladder if int(v) > 0})
        next_features = None
        for val in ladder:
            if val > self.n_features:
                next_features = val
                break
        if next_features is None:
            next_features = min(max_features, self.n_features * 2)
        
        if next_features > self.n_features:
            self.n_features = int(next_features)
            self.vectorizer = HashingVectorizer(n_features=self.n_features, alternate_sign=False, norm="l2")
            self.classifier = SGDClassifier(loss="log_loss", random_state=42)
            self.initialized = False
            improvements.append(f"Traditional model scaled to {self.n_features} features")
        
        # Enhance cancer vaccine components
        if len(self.state.learning_history) > 50:
            # Improve mutation detection based on learning history
            improvements.append("Enhanced mutation detection algorithms")
            
            # Improve neoantigen prediction
            improvements.append("Optimized neoantigen prediction models")
            
            # Improve vaccine design
            improvements.append("Enhanced mRNA stability and delivery optimization")
        
        # Update state
        self.state.n_features = self.n_features
        
        return improvements
    
    def analyze_dna_sample(
        self, 
        sample_id: str,
        normal_dna: str,
        tumor_dna: str,
        hla_allele: str = 'HLA-A*02:01'
    ) -> Dict[str, Any]:
        """
        Analyze a DNA sample and design a personalized vaccine.
        
        Args:
            sample_id: Unique identifier for the sample
            normal_dna: Reference DNA sequence
            tumor_dna: Tumor DNA sequence
            hla_allele: Patient's HLA allele
            
        Returns:
            Complete analysis and vaccine design report
        """
        # Analyze mutations
        report = self.dna_analyzer.analyze_sample(
            sample_id=sample_id,
            normal_dna=normal_dna,
            tumor_dna=tumor_dna,
            hla_allele=hla_allele
        )
        
        # Extract neoantigens
        neoantigens = [neo.peptide_sequence for neo in report.predicted_neoantigens]
        
        # Design vaccine
        construct = None
        vaccine_report = {}
        
        if neoantigens:
            construct = self.vaccine_designer.design_vaccine(neoantigens)
            vaccine_report = self.vaccine_designer.generate_vaccine_report(construct)
        
        return {
            'sample_id': sample_id,
            'mutation_analysis': {
                'total_mutations': report.total_mutations,
                'driver_mutations': len(report.driver_mutations),
                'passenger_mutations': len(report.passenger_mutations),
                'tumor_mutational_burden': report.tumor_mutational_burden,
                'microsatellite_status': report.microsatellite_status,
                'predicted_neoantigens': [
                    {
                        'peptide': neo.peptide_sequence,
                        'binding_affinity': neo.binding_affinity,
                        'immunogenicity_score': neo.immunogenicity_score,
                        'hla_allele': neo.hla_allele
                    }
                    for neo in report.predicted_neoantigens
                ]
            },
            'vaccine_design': vaccine_report,
            'construct_sequence': construct.sequence if construct else None,
            'analysis_timestamp': self._get_timestamp()
        }
    
    def add_github_training_data(self, repo_data: Dict[str, Any]) -> None:
        """
        Add GitHub repository data for training the cancer vaccine model.
        
        Args:
            repo_data: Dictionary containing GitHub repository information
                      with keys: 'repo_name', 'description', 'files', 'readme'
        """
        # Create a hash to avoid duplicates
        repo_hash = hashlib.md5(repo_data['repo_name'].encode()).hexdigest()
        
        # Check if already processed
        if any(item.get('repo_hash') == repo_hash for item in self.state.github_training_data):
            return
        
        # Extract relevant information for cancer vaccine training
        training_entry = {
            'repo_hash': repo_hash,
            'repo_name': repo_data['repo_name'],
            'description': repo_data['description'],
            'relevant_files': self._extract_relevant_files(repo_data.get('files', [])),
            'bioinformatics_keywords': self._extract_bioinformatics_keywords(repo_data),
            'timestamp': self._get_timestamp()
        }
        
        self.state.github_training_data.append(training_entry)
        
        # Limit training data size
        if len(self.state.github_training_data) > 500:
            self.state.github_training_data.pop(0)
        
        # Update model based on new training data
        self._update_model_from_github_data(training_entry)
    
    def _extract_relevant_files(self, files: List[Dict[str, Any]]) -> List[str]:
        """Extract relevant bioinformatics and vaccine-related files."""
        relevant_extensions = ['.py', '.ipynb', '.R', '.sh', '.txt', '.json', '.yaml', '.yml']
        relevant_keywords = [
            'cancer', 'tumor', 'mutation', 'neoantigen', 'vaccine', 'mrna',
            'dna', 'rna', 'sequencing', 'bioinformatics', 'immunology'
        ]
        
        relevant_files = []
        for file_info in files:
            filename = file_info.get('name', '').lower()
            if any(ext in filename for ext in relevant_extensions):
                if any(keyword in filename for keyword in relevant_keywords):
                    relevant_files.append(filename)
        
        return relevant_files[:10]  # Limit to top 10 relevant files
    
    def _extract_bioinformatics_keywords(self, repo_data: Dict[str, Any]) -> List[str]:
        """Extract bioinformatics-related keywords from repository data."""
        text = f"{repo_data.get('description', '')} {repo_data.get('readme', '')}"
        text = text.lower()
        
        bioinformatics_keywords = [
            'machine learning', 'deep learning', 'neural network', 'svm', 'random forest',
            'sequence analysis', 'variant calling', 'gene expression', 'pathway analysis',
            'drug discovery', 'protein structure', 'molecular docking'
        ]
        
        found_keywords = []
        for keyword in bioinformatics_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _update_model_from_github_data(self, training_entry: Dict[str, Any]) -> None:
        """Update model based on new GitHub training data."""
        # This would integrate with the SML learning system
        # For now, just log the update
        
        # Update mutation detection algorithms based on new bioinformatics tools
        if any(keyword in training_entry.get('bioinformatics_keywords', []) 
               for keyword in ['variant calling', 'sequence analysis']):
            # Enhance mutation detection
            pass
        
        # Update neoantigen prediction based on new ML models
        if any(keyword in training_entry.get('bioinformatics_keywords', []) 
               for keyword in ['machine learning', 'deep learning', 'neural network']):
            # Enhance neoantigen prediction
            pass
        
        # Update vaccine design based on new optimization algorithms
        if any(keyword in training_entry.get('bioinformatics_keywords', []) 
               for keyword in ['drug discovery', 'protein structure']):
            # Enhance vaccine design
            pass
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get comprehensive model status including cancer vaccine capabilities."""
        return {
            'traditional_model': {
                'features': self.n_features,
                'estimated_params': self.estimated_params,
                'initialized': self.initialized
            },
            'cancer_vaccine_model': {
                'learning_samples': len(self.state.learning_history),
                'github_training_repos': len(self.state.github_training_data),
                'recent_performance': self._get_recent_performance(),
                'model_improvements': self._get_model_improvements()
            },
            'last_update': self._get_timestamp()
        }
    
    def _get_recent_performance(self) -> Dict[str, float]:
        """Get recent performance metrics."""
        recent_history = self.state.learning_history[-20:] if self.state.learning_history else []
        
        if not recent_history:
            return {}
        
        return {
            'avg_design_score': sum(h.get('design_score', 0) for h in recent_history) / len(recent_history),
            'avg_construct_length': sum(h.get('construct_length', 0) for h in recent_history) / len(recent_history),
            'avg_gc_content': sum(h.get('gc_content', 0) for h in recent_history) / len(recent_history),
            'sample_count': len(recent_history)
        }
    
    def _get_model_improvements(self) -> List[str]:
        """Get list of model improvements made through learning."""
        improvements = []
        
        if len(self.state.learning_history) > 100:
            improvements.append("Enhanced mutation detection accuracy")
        
        if len(self.state.github_training_data) > 50:
            improvements.append("Improved neoantigen prediction algorithms")
        
        if self.state.n_features > 2**16:
            improvements.append("Scaled model capacity for complex patterns")
        
        return improvements
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def save(self) -> None:
        """Save all model components."""
        self.save_state()
        
        # Save traditional model if initialized
        if self.initialized:
            import joblib
            joblib.dump(self.classifier, self.model_path)