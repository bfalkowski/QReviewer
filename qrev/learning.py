"""AI-powered learning from repository review history."""

import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import requests
from .github_review import GitHubReviewError


@dataclass
class ReviewPattern:
    """A pattern learned from repository review history."""
    pattern: str
    message: str
    severity: str
    category: str
    confidence: float
    file_pattern: str
    context: str
    examples: List[str]
    frequency: int


@dataclass
class LearningContext:
    """Context for AI learning from repository."""
    repository: str
    total_prs: int
    total_reviews: int
    total_comments: int
    file_patterns: Dict[str, List[Dict[str, Any]]]
    module_patterns: Dict[str, List[Dict[str, Any]]]
    team_preferences: Dict[str, Any]
    common_issues: List[Dict[str, Any]]


def parse_repository_url(repo_url: str) -> Tuple[str, str]:
    """Parse GitHub repository URL to extract owner and repo."""
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, repo_url)
    if not match:
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")

    owner, repo = match.groups()
    return owner, repo


class RepositoryLearner:
    """Learns from repository review history using AI analysis."""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "QReviewer/1.0.0"
        }
    
    def analyze_repository(
        self, 
        repo_url: str, 
        max_prs: int = 100,
        module_filter: Optional[str] = None,
        include_comments: bool = True,
        include_reviews: bool = True,
        sample_strategy: str = "representative"
    ) -> LearningContext:
        """
        Analyze repository to learn from review history.
        
        Args:
            repo_url: GitHub repository URL
            max_prs: Maximum number of PRs to analyze
            module_filter: Optional module path to filter PRs (e.g., 'src/api')
            include_comments: Include PR comments in analysis
            include_reviews: Include PR reviews in analysis
            sample_strategy: Sampling strategy ('recent', 'representative', 'high_impact')
        """
        owner, repo = parse_repository_url(repo_url)
        api_base = f"https://api.github.com/repos/{owner}/{repo}"
        
        print(f"🔍 Analyzing repository: {owner}/{repo}")
        print(f"📊 Strategy: {sample_strategy}")
        if module_filter:
            print(f"🎯 Module filter: {module_filter}")
        
        # Get PRs with sampling strategy
        prs = self._get_sampled_prs(api_base, max_prs, sample_strategy, module_filter)
        
        if not prs:
            print("⚠️  No PRs found matching criteria")
            return LearningContext(
                repository=f"{owner}/{repo}",
                total_prs=0,
                total_reviews=0,
                total_comments=0,
                file_patterns={},
                module_patterns={},
                team_preferences={},
                common_issues=[]
            )
        
        print(f"📋 Analyzing {len(prs)} PRs...")
        
        total_reviews = 0
        total_comments = 0
        file_patterns = {}
        module_patterns = {}
        team_preferences = {"review_style": {}, "common_categories": {}, "severity_distribution": {}, "team_standards": {}}
        common_issues = []
        
        # Analyze each PR
        for i, pr in enumerate(prs):
            pr_number = pr["number"]
            print(f"  📝 PR #{pr_number} ({i+1}/{len(prs)})")
            
            # Get PR reviews if requested
            if include_reviews:
                reviews = self._get_pr_reviews(api_base, pr_number)
                total_reviews += len(reviews)
                
                # Analyze review patterns
                self._analyze_review_patterns(reviews, team_preferences)
            
            # Get PR comments if requested
            if include_comments:
                comments = self._get_pr_comments(api_base, pr_number)
                total_comments += len(comments)
                
                # Analyze comment patterns
                comment_patterns = self._analyze_comment_patterns(comments)
                common_issues.extend(comment_patterns)
            
            # Analyze file patterns
            if "files" in pr:
                self._analyze_file_patterns(pr["files"], file_patterns, module_patterns, module_filter)
        
        # Generate learning context
        context = LearningContext(
            repository=f"{owner}/{repo}",
            total_prs=len(prs),
            total_reviews=total_reviews,
            total_comments=total_comments,
            file_patterns=file_patterns,
            module_patterns=module_patterns,
            team_preferences=team_preferences,
            common_issues=common_issues
        )
        
        return context
    
    def _get_sampled_prs(
        self, 
        api_base: str, 
        max_prs: int, 
        sample_strategy: str,
        module_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get PRs using the specified sampling strategy."""
        
        # Get all PRs first (we'll sample from these)
        all_prs = []
        page = 1
        per_page = 100
        
        while len(all_prs) < max_prs * 3:  # Get more than needed for sampling
            url = f"{api_base}/pulls?state=all&per_page={per_page}&page={page}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"⚠️  Failed to fetch PRs page {page}: {response.status_code}")
                break
            
            page_prs = response.json()
            if not page_prs:
                break
                
            all_prs.extend(page_prs)
            page += 1
            
            # Respect rate limits
            if "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers["X-RateLimit-Remaining"])
                if remaining < 10:
                    print(f"⚠️  Rate limit low: {remaining} requests remaining")
                    break
        
        print(f"📋 Found {len(all_prs)} total PRs")
        
        # Apply module filtering if specified
        if module_filter:
            filtered_prs = []
            for pr in all_prs:
                if self._pr_touches_module(pr, module_filter):
                    filtered_prs.append(pr)
            all_prs = filtered_prs
            print(f"🎯 After module filtering: {len(all_prs)} PRs")
        
        # Apply sampling strategy
        if sample_strategy == "recent":
            sampled_prs = self._sample_recent_prs(all_prs, max_prs)
        elif sample_strategy == "representative":
            sampled_prs = self._sample_representative_prs(all_prs, max_prs)
        elif sample_strategy == "high_impact":
            sampled_prs = self._sample_high_impact_prs(all_prs, max_prs)
        else:
            print(f"⚠️  Unknown strategy '{sample_strategy}', using representative")
            sampled_prs = self._sample_representative_prs(all_prs, max_prs)
        
        return sampled_prs[:max_prs]
    
    def _pr_touches_module(self, pr: Dict[str, Any], module_filter: str) -> bool:
        """Check if a PR touches files in the specified module."""
        if "files" not in pr:
            return False
        
        for file_info in pr["files"]:
            filename = file_info.get("filename", "")
            if filename.startswith(module_filter):
                return True
        return False
    
    def _sample_recent_prs(self, prs: List[Dict[str, Any]], max_prs: int) -> List[Dict[str, Any]]:
        """Sample most recent PRs."""
        # PRs are already sorted by creation date (newest first)
        return prs[:max_prs]
    
    def _sample_representative_prs(self, prs: List[Dict[str, Any]], max_prs: int) -> List[Dict[str, Any]]:
        """Sample PRs across different time periods for representative coverage."""
        if len(prs) <= max_prs:
            return prs
        
        # Divide into time periods and sample from each
        total_periods = 3  # Recent, middle, older
        prs_per_period = max_prs // total_periods
        
        sampled = []
        
        # Recent PRs (first 1/3)
        recent_count = min(prs_per_period, len(prs) // 3)
        sampled.extend(prs[:recent_count])
        
        # Middle PRs (middle 1/3)
        middle_start = len(prs) // 3
        middle_count = min(prs_per_period, len(prs) // 3)
        sampled.extend(prs[middle_start:middle_start + middle_count])
        
        # Older PRs (last 1/3)
        older_start = 2 * (len(prs) // 3)
        older_count = max_prs - len(sampled)
        sampled.extend(prs[older_start:older_start + older_count])
        
        return sampled
    
    def _sample_high_impact_prs(self, prs: List[Dict[str, Any]], max_prs: int) -> List[Dict[str, Any]]:
        """Sample PRs with high impact (many comments, reviews, changes)."""
        # Score PRs by impact
        scored_prs = []
        for pr in prs:
            score = 0
            score += pr.get("comments", 0) * 2  # Comments are valuable
            score += pr.get("review_comments", 0) * 3  # Review comments are very valuable
            score += pr.get("commits", 0)  # More commits = more complex
            score += pr.get("additions", 0) // 100  # Large changes
            score += pr.get("deletions", 0) // 100  # Large changes
            
            scored_prs.append((score, pr))
        
        # Sort by score (highest first) and take top PRs
        scored_prs.sort(key=lambda x: x[0], reverse=True)
        return [pr for score, pr in scored_prs[:max_prs]]
    
    def _get_pr_reviews(self, api_base: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get all reviews for a specific PR."""
        url = f"{api_base}/pulls/{pr_number}/reviews"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def _get_pr_comments(self, api_base: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get all comments for a specific PR."""
        url = f"{api_base}/pulls/{pr_number}/comments"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def _analyze_review_patterns(self, reviews: List[Dict[str, Any]], team_preferences: Dict[str, Any]):
        """Analyze patterns in PR reviews."""
        # Analyze review styles
        review_states = {}
        for review in reviews:
            state = review.get('state', 'unknown')
            review_states[state] = review_states.get(state, 0) + 1
        
        team_preferences["review_style"] = review_states
    
    def _analyze_comment_patterns(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze patterns in PR comments."""
        patterns = []
        
        for comment in comments:
            if comment.get('body'):
                # Extract patterns from comment text
                comment_patterns = self._extract_patterns_from_text(
                    comment['body'], 'comment', comment.get('id', 'unknown')
                )
                patterns.extend(comment_patterns)
        
        return patterns
    
    def _extract_patterns_from_text(self, text: str, source: str, identifier: str) -> List[Dict[str, Any]]:
        """Extract review patterns from text using AI-like analysis."""
        patterns = []
        
        # Common review patterns (this is where we'd integrate with an actual AI model)
        pattern_matches = [
            # Security patterns
            (r"security|vulnerability|injection|auth", "security", "major"),
            (r"eval\s*\(", "code_injection", "critical"),
            (r"password.*=.*['\"]", "hardcoded_credentials", "critical"),
            
            # Code quality patterns
            (r"unused|dead code", "code_quality", "minor"),
            (r"magic number|hardcoded", "code_quality", "minor"),
            (r"TODO|FIXME|HACK", "code_quality", "minor"),
            
            # Performance patterns
            (r"O\(n\^2\)|quadratic|nested loop", "performance", "major"),
            (r"memory leak|resource leak", "performance", "major"),
            
            # Style patterns
            (r"naming|convention|style", "style", "minor"),
            (r"indentation|formatting", "style", "minor"),
            
            # Documentation patterns
            (r"docstring|comment|documentation", "documentation", "minor"),
            (r"README|docs", "documentation", "minor"),
        ]
        
        for pattern, category, severity in pattern_matches:
            if re.search(pattern, text, re.IGNORECASE):
                # Extract context around the pattern
                pattern_start = text.lower().find(pattern.lower())
                if pattern_start >= 0:
                    context_start = max(0, pattern_start - 50)
                    context_end = min(len(text), pattern_start + len(pattern) + 50)
                    context = text[context_start:context_end]
                    
                    patterns.append({
                        "pattern": pattern,
                        "message": f"Pattern detected in {source} from {identifier}",
                        "severity": severity,
                        "category": category,
                        "confidence": 0.7,  # Base confidence
                        "context": context,
                        "examples": [text],
                        "frequency": 1
                    })
        
        return patterns
    
    def _analyze_file_patterns(
        self, 
        files: List[Dict[str, Any]], 
        file_patterns: Dict[str, List[Dict[str, Any]]],
        module_patterns: Dict[str, List[Dict[str, Any]]],
        module_filter: Optional[str] = None
    ):
        """Analyze patterns in PR files."""
        for file_info in files:
            filename = file_info.get("filename", "")
            
            # Skip if module filter is specified and file doesn't match
            if module_filter and not filename.startswith(module_filter):
                continue
            
            # Extract file type and module
            file_type = self._get_file_type(filename)
            module = self._get_module_from_filename(filename)
            
            # Store file information for pattern analysis
            if file_type not in file_patterns:
                file_patterns[file_type] = []
            
            if module not in module_patterns:
                module_patterns[module] = []
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename."""
        if filename.endswith('.py'):
            return 'python'
        elif filename.endswith('.js') or filename.endswith('.ts'):
            return 'javascript'
        elif filename.endswith('.java'):
            return 'java'
        elif filename.endswith('.go'):
            return 'go'
        elif filename.endswith('.rs'):
            return 'rust'
        elif filename.endswith('.md'):
            return 'documentation'
        elif filename.endswith('.yml') or filename.endswith('.yaml'):
            return 'configuration'
        else:
            return 'other'
    
    def _get_module_from_filename(self, filename: str) -> str:
        """Extract module name from filename."""
        parts = filename.split('/')
        if len(parts) >= 2:
            return parts[0]  # First directory level
        return 'root'
    
    def generate_learned_standards(self, context: LearningContext) -> Dict[str, Any]:
        """Generate new standards based on learned patterns."""
        learned_standards = {}
        
        # Create file-specific standards
        for file_pattern, patterns in context.file_patterns.items():
            if len(patterns) > 0:
                standard_name = f"learned_{file_pattern.replace('*', 'general')}"
                learned_standards[standard_name] = {
                    "name": standard_name,
                    "description": f"Learned standards for {file_pattern} files",
                    "version": "1.0.0",
                    "rules": [],
                    "severity_weights": {"critical": 3.0, "major": 2.0, "minor": 1.0},
                    "categories": list(set(p.get('category', 'unknown') for p in patterns)),
                    "metadata": {"source": "repository_learning", "file_pattern": file_pattern}
                }
                
                # Convert patterns to rules
                for pattern in patterns:
                    if pattern.get('frequency', 0) >= 2:  # Only include patterns that appear multiple times
                        rule = {
                            "id": f"LEARNED_{pattern.get('category', 'unknown').upper()}_{pattern.get('frequency', 1)}",
                            "category": pattern.get('category', 'unknown'),
                            "pattern": pattern.get('pattern', ''),
                            "message": pattern.get('message', ''),
                            "severity": pattern.get('severity', 'minor'),
                            "suggestion": f"Based on {pattern.get('frequency', 1)} similar findings in repository",
                            "confidence": pattern.get('confidence', 0.7)
                        }
                        learned_standards[standard_name]["rules"].append(rule)
        
        return learned_standards
    
    def save_learning_results(self, context: LearningContext, output_file: str = "learning_results.json"):
        """Save learning results to a file."""
        results = {
            "repository": context.repository,
            "summary": {
                "total_prs": context.total_prs,
                "total_reviews": context.total_reviews,
                "total_comments": context.total_comments
            },
            "file_patterns": context.file_patterns,
            "module_patterns": context.module_patterns,
            "team_preferences": context.team_preferences,
            "common_issues": context.common_issues,
            "learned_standards": self.generate_learned_standards(context)
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Learning results saved to {output_file}")
        return output_file


def learn_from_repository(
    repo_url: str, 
    token: str, 
    max_prs: int = 100,
    module_filter: Optional[str] = None,
    include_comments: bool = True,
    include_reviews: bool = True,
    sample_strategy: str = "representative"
) -> LearningContext:
    """
    Learn from repository review history.
    
    Args:
        repo_url: GitHub repository URL
        token: GitHub API token
        max_prs: Maximum number of PRs to analyze
        module_filter: Optional module path to filter PRs
        include_comments: Include PR comments in analysis
        include_reviews: Include PR reviews in analysis
        sample_strategy: Sampling strategy ('recent', 'representative', 'high_impact')
        
    Returns:
        LearningContext with learned patterns
    """
    learner = RepositoryLearner(token)
    return learner.analyze_repository(
        repo_url, max_prs, module_filter, 
        include_comments, include_reviews, sample_strategy
    )
