"""
GitHub Trainer for Cancer Vaccine Model

This module enables the AI system to learn from GitHub repositories containing
bioinformatics tools, vaccine research, and DNA analysis code to continuously
improve the cancer vaccine design capabilities.
"""

from __future__ import annotations

import json
import requests
import asyncio
import aiohttp
from typing import List, Dict, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
import hashlib
import re
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GitHubRepo:
    """Represents a GitHub repository."""
    full_name: str
    description: str
    language: str
    stars: int
    forks: int
    topics: List[str]
    created_at: str
    updated_at: str
    clone_url: str
    default_branch: str


@dataclass
class GitHubFile:
    """Represents a file in a GitHub repository."""
    path: str
    name: str
    type: str
    size: int
    sha: str
    download_url: str


@dataclass
class TrainingSample:
    """Represents a training sample extracted from GitHub."""
    repo_name: str
    file_path: str
    content_type: str  # 'code', 'documentation', 'data'
    content: str
    relevant_keywords: List[str]
    extracted_features: Dict[str, Any]
    timestamp: str


class GitHubAPI:
    """Handles GitHub API interactions."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CancerVaccineTrainer/1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    async def search_repositories(
        self, 
        query: str, 
        stars_min: int = 50, 
        language: str = "Python",
        max_results: int = 100
    ) -> List[GitHubRepo]:
        """
        Search for repositories matching the query.
        
        Args:
            query: Search query (e.g., "cancer vaccine", "bioinformatics")
            stars_min: Minimum number of stars
            language: Programming language filter
            max_results: Maximum number of results to return
            
        Returns:
            List of matching repositories
        """
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": f"{query} stars:>{stars_min} language:{language}",
            "sort": "stars",
            "order": "desc",
            "per_page": min(max_results, 100)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_repo_search_results(data)
                    else:
                        logger.error(f"GitHub API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching repositories: {e}")
            return []
    
    def _parse_repo_search_results(self, data: Dict[str, Any]) -> List[GitHubRepo]:
        """Parse GitHub repository search results."""
        repos = []
        for item in data.get("items", []):
            repo = GitHubRepo(
                full_name=item["full_name"],
                description=item.get("description", ""),
                language=item.get("language", ""),
                stars=item["stargazers_count"],
                forks=item["forks_count"],
                topics=item.get("topics", []),
                created_at=item["created_at"],
                updated_at=item["updated_at"],
                clone_url=item["clone_url"],
                default_branch=item["default_branch"]
            )
            repos.append(repo)
        return repos
    
    async def get_repository_contents(
        self, 
        repo_full_name: str, 
        path: str = "",
        max_files: int = 100
    ) -> List[GitHubFile]:
        """
        Get contents of a repository.
        
        Args:
            repo_full_name: Repository name in format "owner/name"
            path: Path within the repository
            max_files: Maximum number of files to retrieve
            
        Returns:
            List of files in the repository
        """
        url = f"{self.base_url}/repos/{repo_full_name}/contents/{path}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_contents(data, max_files)
                    else:
                        logger.error(f"Error getting repository contents: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error getting repository contents: {e}")
            return []
    
    def _parse_contents(self, data: Any, max_files: int) -> List[GitHubFile]:
        """Parse repository contents."""
        files = []
        file_count = 0
        
        def process_item(item):
            nonlocal file_count
            if file_count >= max_files:
                return
            
            if item["type"] == "file":
                file_obj = GitHubFile(
                    path=item["path"],
                    name=item["name"],
                    type=item["type"],
                    size=item["size"],
                    sha=item["sha"],
                    download_url=item["download_url"]
                )
                files.append(file_obj)
                file_count += 1
            elif item["type"] == "dir":
                # For directories, we would need to make additional API calls
                # This is a simplified version
                pass
        
        if isinstance(data, list):
            for item in data:
                process_item(item)
        else:
            process_item(data)
        
        return files
    
    async def get_file_content(self, download_url: str) -> Optional[str]:
        """
        Get content of a specific file.
        
        Args:
            download_url: Direct download URL of the file
            
        Returns:
            File content as string, or None if failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url, headers=self.headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        return content
                    else:
                        logger.error(f"Error getting file content: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return None


class BioinformaticsKeywordExtractor:
    """Extracts bioinformatics and cancer-related keywords from text."""
    
    def __init__(self):
        self.cancer_keywords = [
            'cancer', 'tumor', 'oncology', 'carcinoma', 'metastasis',
            'mutation', 'variant', 'snp', 'indel', 'cnv',
            'neoantigen', 'antigen', 'epitope', 'hla', 'mhc',
            'vaccine', 'immunotherapy', 'checkpoint', 'pd1', 'pd-l1',
            'ctla4', 'tcr', 'bcr', 'immune', 'immunogenicity'
        ]
        
        self.bioinformatics_keywords = [
            'sequence', 'alignment', 'blast', 'sam', 'bam',
            'vcf', 'gff', 'gtf', 'fasta', 'fastq',
            'genomics', 'transcriptomics', 'proteomics', 'metabolomics',
            'pathway', 'go', 'kegg', 'reactome', 'biomart',
            'biopython', 'bioperl', 'bioconductor', 'samtools', 'bwa',
            'gatk', 'picard', 'star', 'hisat2', 'kallisto'
        ]
        
        self.machine_learning_keywords = [
            'machine learning', 'deep learning', 'neural network', 'cnn', 'rnn',
            'lstm', 'transformer', 'bert', 'gpt', 'svm',
            'random forest', 'gradient boosting', 'xgboost', 'lightgbm',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas',
            'numpy', 'matplotlib', 'seaborn', 'plotly'
        ]
        
        self.dna_rna_keywords = [
            'dna', 'rna', 'mrna', 'trna', 'rrna', 'microrna',
            'transcription', 'translation', 'codon', 'amino acid',
            'protein', 'peptide', 'structure', 'folding', 'domain',
            'promoter', 'enhancer', 'silencer', 'utr', 'polya'
        ]
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in (self.cancer_keywords + self.bioinformatics_keywords + 
                       self.machine_learning_keywords + self.dna_rna_keywords):
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))  # Remove duplicates
    
    def calculate_relevance_score(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance score based on keyword frequency and importance."""
        if not keywords:
            return 0.0
        
        text_lower = text.lower()
        score = 0.0
        
        # Weight different keyword categories
        weights = {
            'cancer': 3.0,
            'bioinformatics': 2.0,
            'machine learning': 2.5,
            'dna/rna': 2.0
        }
        
        for keyword in keywords:
            frequency = text_lower.count(keyword)
            category_weight = 1.0
            
            if keyword in self.cancer_keywords:
                category_weight = weights['cancer']
            elif keyword in self.bioinformatics_keywords:
                category_weight = weights['bioinformatics']
            elif keyword in self.machine_learning_keywords:
                category_weight = weights['machine learning']
            elif keyword in self.dna_rna_keywords:
                category_weight = weights['dna/rna']
            
            score += frequency * category_weight
        
        # Normalize by text length
        if len(text) > 0:
            score = score / len(text) * 1000
        
        return min(score, 10.0)  # Cap at 10.0


class CodeAnalyzer:
    """Analyzes code files to extract relevant features."""
    
    def __init__(self):
        self.python_patterns = {
            'import_statements': r'^(import|from)\s+[\w\.]+',
            'function_definitions': r'^def\s+\w+',
            'class_definitions': r'^class\s+\w+',
            'comments': r'#.*$',
            'docstrings': r'""".*?"""',
        }
    
    def analyze_python_code(self, content: str) -> Dict[str, Any]:
        """Analyze Python code to extract features."""
        features = {
            'import_count': 0,
            'function_count': 0,
            'class_count': 0,
            'comment_lines': 0,
            'bioinformatics_imports': [],
            'cancer_related_functions': [],
            'machine_learning_functions': []
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Count imports
            if re.match(self.python_patterns['import_statements'], line):
                features['import_count'] += 1
                # Check for bioinformatics imports
                if any(pkg in line for pkg in ['biopython', 'biopandas', 'pysam', 'pyvcf']):
                    features['bioinformatics_imports'].append(line)
            
            # Count functions
            if re.match(self.python_patterns['function_definitions'], line):
                features['function_count'] += 1
                func_name = line.split('(')[0].split(' ')[1]
                # Check for cancer/ML related functions
                if any(keyword in func_name.lower() for keyword in ['cancer', 'tumor', 'mutation', 'neoantigen']):
                    features['cancer_related_functions'].append(func_name)
                elif any(keyword in func_name.lower() for keyword in ['predict', 'train', 'model', 'learn']):
                    features['machine_learning_functions'].append(func_name)
            
            # Count classes
            if re.match(self.python_patterns['class_definitions'], line):
                features['class_count'] += 1
            
            # Count comments
            if line_stripped.startswith('#'):
                features['comment_lines'] += 1
        
        return features


class GitHubTrainer:
    """Main class for training the cancer vaccine model from GitHub."""
    
    def __init__(self, github_token: Optional[str] = None):
        self.api = GitHubAPI(github_token)
        self.keyword_extractor = BioinformaticsKeywordExtractor()
        self.code_analyzer = CodeAnalyzer()
        self.trained_repos = set()
        
        # Training queries for different domains
        self.training_queries = [
            "cancer vaccine machine learning",
            "neoantigen prediction bioinformatics",
            "tumor mutation analysis",
            "mrna vaccine design",
            "cancer immunotherapy algorithms",
            "bioinformatics sequence analysis",
            "cancer genomics machine learning",
            "immune epitope prediction"
        ]
    
    async def train_from_github(self, max_repos: int = 50, max_files_per_repo: int = 20) -> List[TrainingSample]:
        """
        Train the model by analyzing GitHub repositories.
        
        Args:
            max_repos: Maximum number of repositories to analyze
            max_files_per_repo: Maximum number of files to analyze per repository
            
        Returns:
            List of training samples extracted from GitHub
        """
        training_samples = []
        
        logger.info("Starting GitHub training process...")
        
        # Search for relevant repositories
        for query in self.training_queries:
            logger.info(f"Searching for repositories with query: {query}")
            repos = await self.api.search_repositories(
                query=query, 
                stars_min=20, 
                max_results=20
            )
            
            for repo in repos[:max_repos // len(self.training_queries)]:
                if repo.full_name in self.trained_repos:
                    continue
                
                logger.info(f"Analyzing repository: {repo.full_name}")
                samples = await self._analyze_repository(repo, max_files_per_repo)
                training_samples.extend(samples)
                self.trained_repos.add(repo.full_name)
                
                if len(training_samples) >= max_repos:
                    break
            
            if len(training_samples) >= max_repos:
                break
        
        logger.info(f"Completed GitHub training with {len(training_samples)} samples")
        return training_samples
    
    async def _analyze_repository(
        self, 
        repo: GitHubRepo, 
        max_files: int
    ) -> List[TrainingSample]:
        """Analyze a single repository and extract training samples."""
        samples = []
        
        # Get repository contents
        files = await self.api.get_repository_contents(repo.full_name, max_files=max_files)
        
        # Analyze each relevant file
        for file in files:
            if self._is_relevant_file(file):
                content = await self.api.get_file_content(file.download_url)
                if content and len(content) > 100:  # Skip very small files
                    sample = self._create_training_sample(repo, file, content)
                    if sample:
                        samples.append(sample)
        
        return samples
    
    def _is_relevant_file(self, file: GitHubFile) -> bool:
        """Check if a file is relevant for training."""
        relevant_extensions = ['.py', '.ipynb', '.R', '.sh', '.txt', '.md', '.json', '.yaml', '.yml']
        relevant_keywords = [
            'cancer', 'tumor', 'mutation', 'neoantigen', 'vaccine', 'mrna',
            'dna', 'rna', 'sequencing', 'bioinformatics', 'immunology',
            'machine', 'learning', 'deep', 'neural', 'model'
        ]
        
        # Check file extension
        if not any(ext in file.name.lower() for ext in relevant_extensions):
            return False
        
        # Check file name for relevant keywords
        if any(keyword in file.name.lower() for keyword in relevant_keywords):
            return True
        
        # Check path for relevant directories
        if any(keyword in file.path.lower() for keyword in ['src/', 'scripts/', 'analysis/', 'models/']):
            return True
        
        return False
    
    def _create_training_sample(
        self, 
        repo: GitHubRepo, 
        file: GitHubFile, 
        content: str
    ) -> Optional[TrainingSample]:
        """Create a training sample from repository file."""
        # Extract keywords
        keywords = self.keyword_extractor.extract_keywords(content)
        
        # Calculate relevance score
        relevance_score = self.keyword_extractor.calculate_relevance_score(content, keywords)
        
        # Skip if not relevant enough
        if relevance_score < 2.0:
            return None
        
        # Determine content type
        content_type = 'code'
        if file.name.endswith(('.md', '.txt', '.rst')):
            content_type = 'documentation'
        elif file.name.endswith(('.json', '.csv', '.tsv', '.bed', '.vcf')):
            content_type = 'data'
        
        # Extract features
        extracted_features = {}
        if content_type == 'code' and file.name.endswith('.py'):
            extracted_features = self.code_analyzer.analyze_python_code(content)
        
        return TrainingSample(
            repo_name=repo.full_name,
            file_path=file.path,
            content_type=content_type,
            content=content[:10000],  # Limit content size
            relevant_keywords=keywords,
            extracted_features=extracted_features,
            timestamp=datetime.now().isoformat()
        )
    
    def extract_training_insights(self, samples: List[TrainingSample]) -> Dict[str, Any]:
        """
        Extract insights from training samples to improve the model.
        
        Args:
            samples: List of training samples from GitHub
            
        Returns:
            Insights and recommendations for model improvement
        """
        insights = {
            'most_common_keywords': {},
            'popular_libraries': [],
            'common_patterns': [],
            'recommended_improvements': [],
            'training_summary': {
                'total_samples': len(samples),
                'code_samples': len([s for s in samples if s.content_type == 'code']),
                'documentation_samples': len([s for s in samples if s.content_type == 'documentation']),
                'data_samples': len([s for s in samples if s.content_type == 'data'])
            }
        }
        
        # Analyze keywords
        keyword_counts = {}
        for sample in samples:
            for keyword in sample.relevant_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        insights['most_common_keywords'] = dict(sorted(
            keyword_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:20])
        
        # Analyze code patterns
        code_samples = [s for s in samples if s.content_type == 'code']
        if code_samples:
            # Extract popular libraries from import statements
            import_counts = {}
            for sample in code_samples:
                for feature_key, feature_value in sample.extracted_features.items():
                    if 'import' in feature_key.lower():
                        if isinstance(feature_value, list):
                            for imp in feature_value:
                                lib_name = imp.split()[-1].split('.')[0]
                                import_counts[lib_name] = import_counts.get(lib_name, 0) + 1
            
            insights['popular_libraries'] = dict(sorted(
                import_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10])
        
        # Generate recommendations
        recommendations = []
        
        if 'neoantigen' in insights['most_common_keywords']:
            recommendations.append("Enhance neoantigen prediction algorithms")
        
        if 'machine learning' in insights['most_common_keywords']:
            recommendations.append("Implement advanced ML models for mutation analysis")
        
        if 'biopython' in insights['popular_libraries']:
            recommendations.append("Integrate Biopython for enhanced sequence analysis")
        
        if 'tensorflow' in insights['popular_libraries'] or 'pytorch' in insights['popular_libraries']:
            recommendations.append("Add deep learning capabilities for pattern recognition")
        
        insights['recommended_improvements'] = recommendations
        
        return insights
    
    async def continuous_training_loop(self, interval_hours: int = 24):
        """
        Run continuous training loop to periodically update from GitHub.
        
        Args:
            interval_hours: Hours between training cycles
        """
        while True:
            try:
                logger.info("Starting continuous GitHub training cycle...")
                samples = await self.train_from_github(max_repos=20, max_files_per_repo=10)
                
                if samples:
                    insights = self.extract_training_insights(samples)
                    logger.info(f"Training cycle completed. Insights: {insights['recommended_improvements']}")
                
                # Wait for next cycle
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error in continuous training loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying


# Example usage and testing
async def main():
    """Example of how to use the GitHub trainer."""
    # Initialize trainer (you can provide a GitHub token for higher rate limits)
    trainer = GitHubTrainer()
    
    # Train from GitHub
    samples = await trainer.train_from_github(max_repos=10, max_files_per_repo=5)
    
    # Extract insights
    insights = trainer.extract_training_insights(samples)
    
    # Print results
    print(f"Trained on {len(samples)} samples")
    print(f"Most common keywords: {insights['most_common_keywords']}")
    print(f"Recommended improvements: {insights['recommended_improvements']}")


if __name__ == "__main__":
    asyncio.run(main())