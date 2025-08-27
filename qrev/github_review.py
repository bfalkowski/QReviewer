"""GitHub PR review and commenting functionality."""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
import requests
from .models import Finding


class GitHubReviewError(Exception):
    """GitHub review error."""
    pass


def parse_pr_url(pr_url: str) -> Tuple[str, str, int]:
    """Parse GitHub PR URL to extract owner, repo, and PR number."""
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, pr_url)
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: {pr_url}")
    
    owner, repo, number = match.groups()
    return owner, repo, int(number)


def create_review_comment(finding: Finding, pr_url: str) -> Dict[str, Any]:
    """
    Create a GitHub review comment from a finding.
    
    Args:
        finding: The finding to convert to a comment
        pr_url: The PR URL for context
        
    Returns:
        Dictionary representing the GitHub review comment
    """
    owner, repo, pr_number = parse_pr_url(pr_url)
    
    # Build the comment body
    comment_body = f"""## 🔍 Code Review Finding

**Severity**: {finding.severity.upper()}
**Category**: {finding.category}
**Confidence**: {finding.confidence * 100:.0f}%

**Issue**: {finding.message}

"""
    
    # Add suggestion if available
    if finding.suggested_patch:
        comment_body += f"""**Suggestion**:
```suggestion
{finding.suggested_patch}
```
"""
    
    # Add file context
    comment_body += f"""
**File**: `{finding.file}`
**Line**: {finding.line_hint or 'N/A'}
**Hunk**: `{finding.hunk_header}`

---
*Automated review by QReviewer*"""
    
    return {
        "body": comment_body,
        "path": finding.file,
        "line": finding.line_hint or 1,
        "side": "RIGHT"  # Comment on the new code
    }


def post_pr_review(pr_url: str, findings: List[Finding], token: str, 
                   event: str = "COMMENT", body: str = None) -> Dict[str, Any]:
    """
    Post a review to a GitHub PR with inline comments.
    
    Args:
        pr_url: GitHub PR URL
        findings: List of findings to comment on
        token: GitHub API token
        event: Review event (COMMENT, APPROVE, or REQUEST_CHANGES)
        body: Overall review body
        
    Returns:
        GitHub API response
    """
    owner, repo, pr_number = parse_pr_url(pr_url)
    
    # Get the base URL for the API
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    
    # Prepare the review payload
    review_payload = {
        "event": event,
        "body": body or f"QReviewer automated code review - {len(findings)} findings identified",
        "comments": []
    }
    
    # Convert findings to GitHub comments
    for finding in findings:
        comment = create_review_comment(finding, pr_url)
        review_payload["comments"].append(comment)
    
    # Post the review
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "QReviewer/1.0.0"
    }
    
    review_url = f"{api_base}/pulls/{pr_number}/reviews"
    
    response = requests.post(review_url, json=review_payload, headers=headers)
    
    if response.status_code not in [200, 201]:
        raise GitHubReviewError(f"Failed to post review: {response.status_code} - {response.text}")
    
    return response.json()


def post_pr_comment(pr_url: str, body: str, token: str) -> Dict[str, Any]:
    """
    Post a general comment to a GitHub PR.
    
    Args:
        pr_url: GitHub PR URL
        body: Comment body
        token: GitHub API token
        
    Returns:
        GitHub API response
    """
    owner, repo, pr_number = parse_pr_url(pr_url)
    
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    comments_url = f"{api_base}/issues/{pr_number}/comments"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "QReviewer/1.0.0"
    }
    
    payload = {"body": body}
    
    response = requests.post(comments_url, json=payload, headers=headers)
    
    if response.status_code not in [200, 201]:
        raise GitHubReviewError(f"Failed to post comment: {response.status_code} - {response.text}")
    
    return response.json()


def get_pr_reviews(pr_url: str, token: str) -> List[Dict[str, Any]]:
    """
    Get existing reviews for a PR.
    
    Args:
        pr_url: GitHub PR URL
        token: GitHub API token
        
    Returns:
        List of existing reviews
    """
    owner, repo, pr_number = parse_pr_url(pr_url)
    
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    reviews_url = f"{api_base}/pulls/{pr_number}/reviews"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "QReviewer/1.0.0"
    }
    
    response = requests.get(reviews_url, headers=headers)
    
    if response.status_code != 200:
        raise GitHubReviewError(f"Failed to get reviews: {response.status_code} - {response.text}")
    
    return response.json()

