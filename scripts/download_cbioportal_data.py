#!/usr/bin/env python3
"""
cBioPortal Data Downloader and Processor

This script downloads cancer genomics datasets from cBioPortal and processes them
for integration with the SML cancer vaccine training system.
"""

import os
import json
import requests
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Any
import time
from dataclasses import dataclass
import gzip
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# cBioPortal API endpoints
CBIO_PORTAL_BASE = "https://www.cbioportal.org/api"
CBIO_PORTAL_STUDIES = f"{CBIO_PORTAL_BASE}/studies"
CBIO_PORTAL_STUDY_DATA = f"{CBIO_PORTAL_BASE}/studies/{{}}/download"


@dataclass
class CancerStudy:
    """Represents a cancer study from cBioPortal."""
    study_id: str
    name: str
    description: str
    cancer_type: str
    sample_count: int
    data_types: List[str]


@dataclass
class PatientData:
    """Represents processed patient data for training."""
    patient_id: str
    study_id: str
    cancer_type: str
    mutations: List[Dict[str, Any]]
    clinical_data: Dict[str, Any]
    survival_data: Optional[Dict[str, Any]] = None


class CBioPortalDownloader:
    """Downloads and processes data from cBioPortal."""
    
    def __init__(self, output_dir: str = "data/cbioportal"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.raw_data_dir = self.output_dir / "raw"
        self.processed_data_dir = self.output_dir / "processed"
        self.raw_data_dir.mkdir(exist_ok=True)
        self.processed_data_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SML-Cancer-Vaccine-System/1.0',
            'Accept': 'application/json'
        })
    
    def get_available_studies(self, limit: int = 50) -> List[CancerStudy]:
        """Get list of available cancer studies from cBioPortal."""
        logger.info("Fetching available studies from cBioPortal...")
        
        try:
            response = self.session.get(CBIO_PORTAL_STUDIES, params={'projection': 'SUMMARY'})
            response.raise_for_status()
            
            studies_data = response.json()
            
            # Filter for studies with genomic data
            genomic_studies = []
            for study in studies_data:
                if study.get('cancerType', {}).get('cancerTypeId'):
                    cancer_study = CancerStudy(
                        study_id=study['studyId'],
                        name=study['name'],
                        description=study.get('description', ''),
                        cancer_type=study['cancerType']['name'],
                        sample_count=study.get('allSampleCount', 0),
                        data_types=[]  # Will be populated when downloading
                    )
                    genomic_studies.append(cancer_study)
            
            # Sort by sample count (descending)
            genomic_studies.sort(key=lambda x: x.sample_count, reverse=True)
            
            logger.info(f"Found {len(genomic_studies)} studies with genomic data")
            return genomic_studies[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching studies: {e}")
            return []
    
    def download_study_data(self, study_id: str) -> Dict[str, Path]:
        """Download all data files for a specific study."""
        logger.info(f"Downloading data for study: {study_id}")
        
        study_dir = self.raw_data_dir / study_id
        study_dir.mkdir(exist_ok=True)
        
        # Get available data types for this study
        data_files = {}
        
        try:
            # Download mutation data (MAF files)
            mutation_url = f"{CBIO_PORTAL_BASE}/studies/{study_id}/mutation-data"
            mutation_response = self.session.get(mutation_url)
            if mutation_response.status_code == 200:
                mutation_file = study_dir / f"{study_id}_mutations.maf"
                with open(mutation_file, 'w') as f:
                    f.write(mutation_response.text)
                data_files['mutations'] = mutation_file
                logger.info(f"Downloaded mutations: {mutation_file}")
            
            # Download clinical data
            clinical_url = f"{CBIO_PORTAL_BASE}/studies/{study_id}/clinical-data"
            clinical_response = self.session.get(clinical_url)
            if clinical_response.status_code == 200:
                clinical_file = study_dir / f"{study_id}_clinical.txt"
                with open(clinical_file, 'w') as f:
                    f.write(clinical_response.text)
                data_files['clinical'] = clinical_file
                logger.info(f"Downloaded clinical data: {clinical_file}")
            
            # Download survival data
            survival_url = f"{CBIO_PORTAL_BASE}/studies/{study_id}/survival-data"
            survival_response = self.session.get(survival_url)
            if survival_response.status_code == 200:
                survival_file = study_dir / f"{study_id}_survival.txt"
                with open(survival_file, 'w') as f:
                    f.write(survival_response.text)
                data_files['survival'] = survival_file
                logger.info(f"Downloaded survival data: {survival_file}")
            
            # Download gene panel data
            genes_url = f"{CBIO_PORTAL_BASE}/studies/{study_id}/genes"
            genes_response = self.session.get(genes_url)
            if genes_response.status_code == 200:
                genes_file = study_dir / f"{study_id}_genes.txt"
                with open(genes_file, 'w') as f:
                    f.write(genes_response.text)
                data_files['genes'] = genes_file
                logger.info(f"Downloaded gene panel: {genes_file}")
            
            return data_files
            
        except Exception as e:
            logger.error(f"Error downloading study data for {study_id}: {e}")
            return {}
    
    def process_mutation_data(self, maf_file: Path) -> pd.DataFrame:
        """Process MAF (Mutation Annotation Format) file."""
        logger.info(f"Processing mutation data: {maf_file}")
        
        try:
            # Read MAF file
            df = pd.read_csv(maf_file, sep='\t', comment='#', low_memory=False)
            
            # Filter for high-confidence mutations
            # Keep only missense, nonsense, frameshift, and splice site mutations
            high_impact_mutations = [
                'Missense_Mutation', 'Nonsense_Mutation', 'Frame_Shift_Del',
                'Frame_Shift_Ins', 'Splice_Site', 'Translation_Start_Site'
            ]
            
            df_filtered = df[df['Variant_Classification'].isin(high_impact_mutations)].copy()
            
            # Add derived columns
            df_filtered['Hugo_Symbol'] = df_filtered['Hugo_Symbol'].fillna('Unknown')
            df_filtered['Chromosome'] = df_filtered['Chromosome'].fillna('Unknown')
            df_filtered['Start_Position'] = df_filtered['Start_Position'].fillna(0)
            df_filtered['End_Position'] = df_filtered['End_Position'].fillna(0)
            
            # Calculate mutation burden per patient
            mutation_burden = df_filtered.groupby('Tumor_Sample_Barcode').size()
            df_filtered['Mutation_Burden'] = df_filtered['Tumor_Sample_Barcode'].map(mutation_burden)
            
            logger.info(f"Processed {len(df_filtered)} high-impact mutations")
            return df_filtered
            
        except Exception as e:
            logger.error(f"Error processing mutation data: {e}")
            return pd.DataFrame()
    
    def process_clinical_data(self, clinical_file: Path) -> pd.DataFrame:
        """Process clinical data file."""
        logger.info(f"Processing clinical data: {clinical_file}")
        
        try:
            df = pd.read_csv(clinical_file, sep='\t', comment='#')
            
            # Standardize column names
            df.columns = [col.strip() for col in df.columns]
            
            # Filter for relevant clinical features
            relevant_columns = [
                'PATIENT_ID', 'SAMPLE_ID', 'CANCER_TYPE', 'CANCER_TYPE_DETAILED',
                'AGE', 'GENDER', 'STAGE', 'GRADE', 'TUMOR_SITE', 'SAMPLE_TYPE'
            ]
            
            available_columns = [col for col in relevant_columns if col in df.columns]
            df_filtered = df[available_columns].copy()
            
            logger.info(f"Processed clinical data with {len(df_filtered)} samples")
            return df_filtered
            
        except Exception as e:
            logger.error(f"Error processing clinical data: {e}")
            return pd.DataFrame()
    
    def create_training_samples(self, study_id: str, mutation_df: pd.DataFrame, clinical_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Create training samples from processed data."""
        logger.info(f"Creating training samples for study: {study_id}")
        
        samples = []
        
        try:
            # Merge mutation and clinical data
            if not mutation_df.empty and not clinical_df.empty:
                # Map sample IDs between datasets
                mutation_df['SAMPLE_ID'] = mutation_df['Tumor_Sample_Barcode']
                merged_df = mutation_df.merge(
                    clinical_df, 
                    on='SAMPLE_ID', 
                    how='left'
                )
            elif not mutation_df.empty:
                merged_df = mutation_df.copy()
                merged_df['SAMPLE_ID'] = merged_df['Tumor_Sample_Barcode']
            else:
                return samples
            
            # Group by patient/sample
            for sample_id, group in merged_df.groupby('SAMPLE_ID'):
                try:
                    # Extract patient information
                    patient_info = {
                        'sample_id': sample_id,
                        'study_id': study_id,
                        'cancer_type': group['CANCER_TYPE'].iloc[0] if 'CANCER_TYPE' in group.columns else 'Unknown',
                        'age': group['AGE'].iloc[0] if 'AGE' in group.columns else None,
                        'gender': group['GENDER'].iloc[0] if 'GENDER' in group.columns else 'Unknown'
                    }
                    
                    # Extract mutations
                    mutations = []
                    for _, mutation in group.iterrows():
                        mutation_info = {
                            'gene': mutation.get('Hugo_Symbol', 'Unknown'),
                            'chromosome': mutation.get('Chromosome', 'Unknown'),
                            'position': int(mutation.get('Start_Position', 0)),
                            'reference_allele': mutation.get('Reference_Allele', ''),
                            'variant_allele': mutation.get('Tumor_Seq_Allele2', ''),
                            'variant_classification': mutation.get('Variant_Classification', ''),
                            'protein_change': mutation.get('Protein_Change', ''),
                            'mutation_type': self._classify_mutation(mutation),
                            'driver_probability': self._calculate_driver_probability(mutation)
                        }
                        mutations.append(mutation_info)
                    
                    # Create training sample
                    training_sample = {
                        'patient_info': patient_info,
                        'mutations': mutations,
                        'mutation_count': len(mutations),
                        'mutation_burden': group['Mutation_Burden'].iloc[0] if 'Mutation_Burden' in group.columns else len(mutations),
                        'label': self._determine_label(group, mutations),  # 0 for normal, 1 for cancer
                        'timestamp': None
                    }
                    
                    samples.append(training_sample)
                    
                except Exception as e:
                    logger.warning(f"Error processing sample {sample_id}: {e}")
                    continue
            
            logger.info(f"Created {len(samples)} training samples from study {study_id}")
            return samples
            
        except Exception as e:
            logger.error(f"Error creating training samples: {e}")
            return []
    
    def _classify_mutation(self, mutation_row) -> str:
        """Classify mutation type."""
        variant_class = mutation_row.get('Variant_Classification', '')
        
        if variant_class in ['Missense_Mutation', 'Nonsense_Mutation']:
            return 'coding'
        elif variant_class in ['Frame_Shift_Del', 'Frame_Shift_Ins']:
            return 'frameshift'
        elif variant_class == 'Splice_Site':
            return 'splice'
        elif variant_class == 'Translation_Start_Site':
            return 'start_codon'
        else:
            return 'other'
    
    def _calculate_driver_probability(self, mutation_row) -> float:
        """Calculate probability that mutation is a driver mutation."""
        # Simplified driver probability calculation
        # In practice, this would use databases like COSMIC, OncoKB, etc.
        
        gene = mutation_row.get('Hugo_Symbol', '')
        variant_class = mutation_row.get('Variant_Classification', '')
        
        # Known cancer driver genes (simplified list)
        driver_genes = {
            'TP53', 'KRAS', 'PIK3CA', 'EGFR', 'BRAF', 'MYC', 'NRAS', 'HRAS',
            'AKT1', 'CDKN2A', 'PTEN', 'VHL', 'APC', 'CTNNB1', 'BRCA1', 'BRCA2'
        }
        
        base_score = 0.1  # Base probability
        
        if gene in driver_genes:
            base_score += 0.4
        
        if variant_class in ['Missense_Mutation', 'Nonsense_Mutation']:
            base_score += 0.2
        elif variant_class in ['Frame_Shift_Del', 'Frame_Shift_Ins']:
            base_score += 0.3
        
        return min(base_score, 1.0)
    
    def _determine_label(self, group, mutations) -> int:
        """Determine training label (0 for normal, 1 for cancer)."""
        # For cancer genomics, label is typically 1 (cancer)
        # This could be enhanced with survival outcomes or treatment response
        
        if len(mutations) > 0:
            return 1  # Cancer sample with mutations
        else:
            return 0  # Normal sample (no mutations)
    
    def download_and_process_studies(self, study_ids: List[str], max_studies: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Download and process multiple studies."""
        logger.info(f"Starting download and processing for {min(len(study_ids), max_studies)} studies")
        
        all_samples = {}
        
        for i, study_id in enumerate(study_ids[:max_studies]):
            logger.info(f"Processing study {i+1}/{min(len(study_ids), max_studies)}: {study_id}")
            
            try:
                # Download study data
                data_files = self.download_study_data(study_id)
                
                if not data_files:
                    logger.warning(f"No data downloaded for study {study_id}")
                    continue
                
                # Process mutation data
                mutation_df = pd.DataFrame()
                if 'mutations' in data_files:
                    mutation_df = self.process_mutation_data(data_files['mutations'])
                
                # Process clinical data
                clinical_df = pd.DataFrame()
                if 'clinical' in data_files:
                    clinical_df = self.process_clinical_data(data_files['clinical'])
                
                # Create training samples
                if not mutation_df.empty:
                    samples = self.create_training_samples(study_id, mutation_df, clinical_df)
                    all_samples[study_id] = samples
                    
                    # Save processed samples
                    output_file = self.processed_data_dir / f"{study_id}_training_samples.json"
                    with open(output_file, 'w') as f:
                        json.dump(samples, f, indent=2, default=str)
                    
                    logger.info(f"Saved {len(samples)} samples to {output_file}")
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing study {study_id}: {e}")
                continue
        
        return all_samples
    
    def create_combined_dataset(self, all_samples: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Create a combined dataset from all studies."""
        logger.info("Creating combined dataset from all studies")
        
        combined_samples = []
        
        for study_id, samples in all_samples.items():
            for sample in samples:
                # Add study identifier to each sample
                sample['source_study'] = study_id
                combined_samples.append(sample)
        
        # Save combined dataset
        combined_file = self.processed_data_dir / "combined_training_dataset.json"
        with open(combined_file, 'w') as f:
            json.dump(combined_samples, f, indent=2, default=str)
        
        logger.info(f"Created combined dataset with {len(combined_samples)} samples")
        logger.info(f"Combined dataset saved to: {combined_file}")
        
        return combined_samples


def main():
    """Main function to download and process cBioPortal data."""
    downloader = CBioPortalDownloader()
    
    # Get available studies
    logger.info("Fetching available studies...")
    studies = downloader.get_available_studies(limit=20)
    
    if not studies:
        logger.error("No studies found or error fetching studies")
        return
    
    # Display available studies
    logger.info("Available studies:")
    for i, study in enumerate(studies[:10]):
        logger.info(f"{i+1}. {study.study_id} - {study.name} ({study.cancer_type}) - {study.sample_count} samples")
    
    # Select top studies for download
    selected_studies = [study.study_id for study in studies[:5]]  # Top 5 studies
    logger.info(f"Selected studies for download: {selected_studies}")
    
    # Download and process studies
    all_samples = downloader.download_and_process_studies(selected_studies, max_studies=5)
    
    # Create combined dataset
    if all_samples:
        combined_samples = downloader.create_combined_dataset(all_samples)
        
        # Create summary report
        logger.info("\n=== DOWNLOAD SUMMARY ===")
        for study_id, samples in all_samples.items():
            logger.info(f"{study_id}: {len(samples)} samples")
        
        logger.info(f"Total samples: {len(combined_samples)}")
        logger.info("Download and processing completed successfully!")
    else:
        logger.warning("No samples were created. Check the download process.")


if __name__ == "__main__":
    main()