"""GitHub API client for fetching PR information."""

import os
import re
from typing import List, Tuple
import requests
from .models import PRInfo, PRFilePatch, PRDiff


class GitHubAPIError(Exception):
    """GitHub API error."""
    pass


def parse_pr_url(url: str) -> Tuple[str, str, int]:
    """Parse GitHub PR URL to extract owner, repo, and PR number."""
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: {url}")
    
    owner, repo, number = match.groups()
    return owner, repo, int(number)


def fetch_pr_files(pr_url: str) -> PRDiff:
    """Fetch PR files with pagination."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise GitHubAPIError("GITHUB_TOKEN environment variable is required")
    
    owner, repo, pr_number = parse_pr_url(pr_url)
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "QReviewer/0.1.0"
    }
    
    base_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    
    all_files = []
    page = 1
    per_page = 100
    
    while True:
        url = f"{base_url}?per_page={per_page}&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise GitHubAPIError(f"GitHub API error: {response.status_code} - {response.text}")
        
        files = response.json()
        if not files:
            break
            
        all_files.extend(files)
        page += 1
        
        # GitHub API returns fewer items than requested when we're at the last page
        if len(files) < per_page:
            break
    
    # Convert to our models
    pr_files = []
    for file_data in all_files:
        pr_file = PRFilePatch(
            path=file_data["filename"],
            status=file_data["status"],
            patch=file_data.get("patch"),
            additions=file_data.get("additions", 0),
            deletions=file_data.get("deletions", 0),
            sha=file_data.get("sha")
        )
        pr_files.append(pr_file)
    
    pr_info = PRInfo(
        url=pr_url,
        number=pr_number,
        repo=f"{owner}/{repo}"
    )
    
    return PRDiff(pr=pr_info, files=pr_files)
