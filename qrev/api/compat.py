"""Compatibility layer for existing QReviewer modules."""

import asyncio
from typing import Dict, Any, List, Optional
from ..models import Finding, PRDiff
from ..github_api import fetch_pr_files
from ..llm_client import get_llm_client
from ..diff import split_patch_into_hunks
import json


async def fetch_pr_diff_async(pr_url: str, token: str = None) -> Dict[str, Any]:
    """
    Async wrapper for fetch_pr_files.
    
    Args:
        pr_url: GitHub PR URL
        token: GitHub token (optional, will use env var if not provided)
        
    Returns:
        Dictionary representation of PR diff data
    """
    # Run the sync function in a thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    pr_diff = await loop.run_in_executor(None, fetch_pr_files, pr_url)
    
    # Convert to dictionary format for API compatibility
    return {
        "pr": {
            "url": pr_diff.pr.url,
            "number": pr_diff.pr.number,
            "repo": pr_diff.pr.repo
        },
        "files": [
            {
                "path": file.path,
                "status": file.status,
                "patch": file.patch,
                "additions": file.additions,
                "deletions": file.deletions,
                "sha": file.sha
            }
            for file in pr_diff.files
        ]
    }


async def review_hunks_async(diff_json: Dict[str, Any], rules: Optional[Dict[str, Any]] = None, model_id: str = None) -> List[Finding]:
    """
    Async wrapper for reviewing hunks.
    
    Args:
        diff_json: PR diff data from GitHub
        rules: Optional review rules
        model_id: Optional model ID for LLM (ignored, uses config)
        
    Returns:
        List of Finding objects
    """
    findings = []
    
    # Process each file in the diff
    for file_data in diff_json.get("files", []):
        if not file_data.get("patch"):
            continue
            
        # Parse the patch into hunks
        hunks = split_patch_into_hunks(file_data["patch"], file_data["path"])
        
        # Review each hunk
        for hunk in hunks:
            hunk_findings = await review_hunk_async(hunk, rules)
            findings.extend(hunk_findings)
    
    return findings


async def review_hunk_async(hunk, rules: Optional[Dict[str, Any]] = None) -> List[Finding]:
    """
    Async wrapper for review_hunk.
    
    Args:
        hunk: Hunk object to review
        rules: Optional review rules
        
    Returns:
        List of Finding objects
    """
    # Get the configured LLM client
    llm_client = get_llm_client()
    
    # Convert rules to guidelines string if provided
    guidelines = None
    if rules:
        if isinstance(rules, dict):
            guidelines = json.dumps(rules, indent=2)
        else:
            guidelines = str(rules)
    
    # Review the hunk using the configured LLM backend
    return await llm_client.review_hunk(hunk, guidelines)
