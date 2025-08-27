"""Pydantic models for QReviewer."""

from typing import List, Optional
from pydantic import BaseModel, Field


class PRInfo(BaseModel):
    """Pull request information."""
    url: str = Field(..., description="GitHub PR URL")
    number: int = Field(..., description="PR number")
    repo: str = Field(..., description="Repository slug (owner/repo)")


class PRFilePatch(BaseModel):
    """File patch information from GitHub API."""
    path: str = Field(..., description="File path")
    status: str = Field(..., description="File status (modified, added, removed, renamed)")
    patch: Optional[str] = Field(None, description="Unified diff patch")
    additions: int = Field(0, description="Number of additions")
    deletions: int = Field(0, description="Number of deletions")
    sha: Optional[str] = Field(None, description="File SHA if available")


class PRDiff(BaseModel):
    """Complete PR diff information."""
    pr: PRInfo
    files: List[PRFilePatch]


class Hunk(BaseModel):
    """A single diff hunk."""
    file_path: str = Field(..., description="File path")
    hunk_header: str = Field(..., description="Hunk header (@@ -a,b +c,d @@)")
    patch_text: str = Field(..., description="Hunk patch text")
    start_line: int = Field(..., description="Starting line number for additions")
    end_line: int = Field(..., description="Ending line number for additions")
    language: Optional[str] = Field(None, description="Inferred language from file extension")


class Finding(BaseModel):
    """A single code review finding."""
    file: str = Field(..., description="File path")
    hunk_header: str = Field(..., description="Hunk header")
    severity: str = Field(..., description="Severity: blocking, major, minor, nit")
    category: str = Field(..., description="Category: correctness, security, performance, complexity, style, tests, docs")
    message: str = Field(..., description="Finding message (≤2 sentences)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score [0..1]")
    suggested_patch: Optional[str] = Field(None, description="GitHub suggested change block")
    line_hint: Optional[int] = Field(None, description="Line number hint for the finding")


class FindingsReport(BaseModel):
    """Complete findings report."""
    pr: PRInfo
    findings: List[Finding]


class ReviewStats(BaseModel):
    """Summary statistics for the review."""
    blocking: int = Field(0, description="Number of blocking findings")
    major: int = Field(0, description="Number of major findings")
    minor: int = Field(0, description="Number of minor findings")
    nit: int = Field(0, description="Number of nit findings")
    total: int = Field(0, description="Total number of findings")
