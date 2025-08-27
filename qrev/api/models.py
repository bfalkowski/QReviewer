"""Pydantic models for QReviewer API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from ..models import Finding


class ReviewRequest(BaseModel):
    """Request for a complete PR review."""
    prUrl: str = Field(..., description="GitHub PR URL to review")
    guidelinesUrl: Optional[str] = Field(None, description="Optional guidelines URL")
    requestId: Optional[str] = Field(None, description="Optional request ID for idempotency")


class FetchPRRequest(BaseModel):
    """Request to fetch PR diff from GitHub."""
    prUrl: str = Field(..., description="GitHub PR URL to fetch")


class FetchPRResponse(BaseModel):
    """Response containing PR diff data."""
    diffJson: Dict[str, Any] = Field(..., description="PR diff data from GitHub")


class ReviewHunksRequest(BaseModel):
    """Request to review code hunks using LLM."""
    diffJson: Dict[str, Any] = Field(..., description="PR diff data to review")
    rules: Optional[Dict[str, Any]] = Field(None, description="Optional review rules")


class ReviewHunksResponse(BaseModel):
    """Response containing review findings."""
    findings: List[Finding] = Field(..., description="List of code review findings")


class RenderReportRequest(BaseModel):
    """Request to render HTML report from findings."""
    findings: List[Finding] = Field(..., description="Findings to render in report")


class RenderReportResponse(BaseModel):
    """Response containing rendered HTML report."""
    reportHtml: str = Field(..., description="HTML report content")
    reportHash: str = Field(..., description="SHA256 hash of report content")


class ScoreRequest(BaseModel):
    """Request to score findings."""
    findings: List[Finding] = Field(..., description="Findings to score")


class ScoreResponse(BaseModel):
    """Response containing calculated score."""
    score: float = Field(..., description="Calculated review score")


class ReviewResponse(BaseModel):
    """Complete review response."""
    score: Optional[float] = Field(None, description="Calculated review score")
    findings: List[Finding] = Field(..., description="List of code review findings")
    reportHtml: Optional[str] = Field(None, description="HTML report content")
    reportHash: Optional[str] = Field(None, description="SHA256 hash of report content")
    stepDurations: Optional[Dict[str, int]] = Field(None, description="Step timing in milliseconds")
    artifacts: Optional[List[Dict[str, Any]]] = Field(None, description="Additional artifacts")
