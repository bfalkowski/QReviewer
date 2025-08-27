"""Pydantic models for QReviewer API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from ..models import Finding


class ReviewRequest(BaseModel):
    """Request for a complete PR review."""
    prUrl: str = Field(..., description="GitHub PR URL to review")
    guidelinesUrl: Optional[str] = Field(None, description="Optional guidelines URL")
    requestId: Optional[str] = Field(None, description="Optional request ID for idempotency")
    standards: Optional[List[str]] = Field(None, description="List of standards to apply")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional review context")


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
    standards: Optional[List[str]] = Field(None, description="Standards to apply")


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


# New models for GitHub integration
class PostReviewRequest(BaseModel):
    """Request to post a review to a GitHub PR."""
    prUrl: str = Field(..., description="GitHub PR URL")
    findings: List[Finding] = Field(..., description="Findings to post as review comments")
    event: str = Field("COMMENT", description="Review event: COMMENT, APPROVE, or REQUEST_CHANGES")
    body: Optional[str] = Field(None, description="Overall review body")


class PostReviewResponse(BaseModel):
    """Response from posting a GitHub review."""
    success: bool = Field(..., description="Whether the review was posted successfully")
    reviewId: Optional[int] = Field(None, description="GitHub review ID if successful")
    commentsPosted: int = Field(..., description="Number of inline comments posted")
    message: str = Field(..., description="Success or error message")


class PostCommentRequest(BaseModel):
    """Request to post a general comment to a GitHub PR."""
    prUrl: str = Field(..., description="GitHub PR URL")
    body: str = Field(..., description="Comment body to post")


class PostCommentResponse(BaseModel):
    """Response from posting a GitHub comment."""
    success: bool = Field(..., description="Whether the comment was posted successfully")
    commentId: Optional[int] = Field(None, description="GitHub comment ID if successful")
    message: str = Field(..., description="Success or error message")


class GetReviewsRequest(BaseModel):
    """Request to get existing reviews for a PR."""
    prUrl: str = Field(..., description="GitHub PR URL")


class GetReviewsResponse(BaseModel):
    """Response containing existing PR reviews."""
    reviews: List[Dict[str, Any]] = Field(..., description="List of existing reviews")
    totalReviews: int = Field(..., description="Total number of reviews")


# New models for standards and context
class GetStandardsRequest(BaseModel):
    """Request to get available review standards."""
    names: Optional[List[str]] = Field(None, description="Specific standards to retrieve")


class GetStandardsResponse(BaseModel):
    """Response containing available standards."""
    standards: Dict[str, Dict[str, Any]] = Field(..., description="Available standards")
    availableStandards: List[str] = Field(..., description="List of standard names")


class GetContextRequest(BaseModel):
    """Request to get project context for reviews."""
    projectPath: str = Field(..., description="Path to project directory")
    standards: Optional[List[str]] = Field(None, description="Standards to include in context")


class GetContextResponse(BaseModel):
    """Response containing project context."""
    projectContext: Dict[str, Any] = Field(..., description="Project context information")
    standards: Dict[str, Dict[str, Any]] = Field(..., description="Applicable standards")
    availableStandards: List[str] = Field(..., description="All available standards")


class CreateStandardRequest(BaseModel):
    """Request to create a new review standard."""
    name: str = Field(..., description="Standard name")
    description: str = Field(..., description="Standard description")
    version: str = Field(..., description="Standard version")
    rules: List[Dict[str, Any]] = Field(..., description="Review rules")
    severityWeights: Dict[str, float] = Field(..., description="Severity weights")
    categories: List[str] = Field(..., description="Rule categories")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")


class CreateStandardResponse(BaseModel):
    """Response from creating a standard."""
    success: bool = Field(..., description="Whether the standard was created successfully")
    standardName: str = Field(..., description="Name of created standard")
    message: str = Field(..., description="Success or error message")


class EnhancedReviewRequest(BaseModel):
    """Enhanced review request with standards and context."""
    prUrl: str = Field(..., description="GitHub PR URL to review")
    standards: List[str] = Field(..., description="Standards to apply")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    requestId: Optional[str] = Field(None, description="Request ID for idempotency")
    mode: str = Field("strict", description="Review mode: strict, learning, or compliance")


class EnhancedReviewResponse(BaseModel):
    """Enhanced review response with standards analysis."""
    score: float = Field(..., description="Calculated review score")
    findings: List[Finding] = Field(..., description="List of findings")
    standardsApplied: List[str] = Field(..., description="Standards that were applied")
    complianceStatus: Dict[str, str] = Field(..., description="Compliance status by standard")
    recommendations: List[str] = Field(..., description="Standard-specific recommendations")
    reportHtml: str = Field(..., description="Enhanced HTML report")
    reportHash: str = Field(..., description="Report content hash")
    stepDurations: Dict[str, int] = Field(..., description="Step timing in milliseconds")


# New models for repository learning
class LearnFromRepositoryRequest(BaseModel):
    """Request to learn from repository review history."""
    repositoryUrl: str = Field(..., description="GitHub repository URL")
    maxPRs: int = Field(100, description="Maximum number of PRs to analyze")
    includeComments: bool = Field(True, description="Include PR comments in analysis")
    includeReviews: bool = Field(True, description="Include PR reviews in analysis")
    outputFile: Optional[str] = Field(None, description="Output file for results")


class LearnFromRepositoryResponse(BaseModel):
    """Response from repository learning process."""
    success: bool = Field(..., description="Whether learning was successful")
    repository: str = Field(..., description="Repository analyzed")
    summary: Dict[str, Any] = Field(..., description="Learning summary")
    learnedStandards: Dict[str, Dict[str, Any]] = Field(..., description="Generated standards")
    commonIssues: List[Dict[str, Any]] = Field(..., description="Common issues found")
    teamPreferences: Dict[str, Any] = Field(..., description="Team preferences learned")
    outputFile: Optional[str] = Field(None, description="Output file path")
    message: str = Field(..., description="Success or error message")


class GetLearningStatusRequest(BaseModel):
    """Request to get learning process status."""
    taskId: str = Field(..., description="Learning task ID")


class GetLearningStatusResponse(BaseModel):
    """Response containing learning process status."""
    taskId: str = Field(..., description="Learning task ID")
    status: str = Field(..., description="Current status: running, completed, failed")
    progress: float = Field(..., description="Progress percentage (0-100)")
    currentStep: str = Field(..., description="Current step description")
    estimatedTime: Optional[int] = Field(None, description="Estimated time remaining in seconds")
    results: Optional[Dict[str, Any]] = Field(None, description="Results if completed")


class ApplyLearnedStandardsRequest(BaseModel):
    """Request to apply learned standards to existing standards."""
    learningResultsFile: str = Field(..., description="Path to learning results file")
    standardNames: Optional[List[str]] = Field(None, description="Specific standards to apply")
    overwrite: bool = Field(False, description="Whether to overwrite existing standards")


class ApplyLearnedStandardsResponse(BaseModel):
    """Response from applying learned standards."""
    success: bool = Field(..., description="Whether standards were applied successfully")
    standardsApplied: List[str] = Field(..., description="Names of applied standards")
    standardsCreated: int = Field(..., description="Number of new standards created")
    standardsUpdated: int = Field(..., description="Number of existing standards updated")
    message: str = Field(..., description="Success or error message")
