"""FastAPI application for QReviewer."""

import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from .models import (
    ReviewRequest, ReviewResponse, FetchPRRequest, FetchPRResponse,
    ReviewHunksRequest, ReviewHunksResponse, RenderReportRequest,
    RenderReportResponse, ScoreRequest, ScoreResponse,
    LearnFromRepositoryRequest, LearnFromRepositoryResponse
)
from .security import require_api_key
from .utils import make_request_id, hash_html, timed
from .compat import fetch_pr_diff_async, review_hunks_async
from ..report import render_html

# Create FastAPI app
app = FastAPI(
    title="QReviewer API",
    description="Automated code review service for GitHub pull requests with AI learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Learning task storage (in production, use Redis or database)
learning_tasks = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information."""
    return """
    <html>
        <head>
            <title>QReviewer API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { font-weight: bold; color: #0066cc; }
                .ai { background: #fff3e0; border-left: 4px solid #ff9800; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 QReviewer API</h1>
                <p>Welcome to the QReviewer API! This service provides automated code review for GitHub pull requests with AI-powered learning from repository history.</p>
                
                <h2>Available Endpoints</h2>
                
                <div class="endpoint">
                    <div class="method">POST /review</div>
                    <p>Complete PR review pipeline (fetch → review → render → score)</p>
                </div>
                
                <div class="endpoint">
                    <div class="method">POST /fetch_pr</div>
                    <p>Fetch PR diff from GitHub</p>
                </div>
                
                <div class="endpoint">
                    <div class="method">POST /review_hunks</div>
                    <p>Review code changes using LLM</p>
                </div>
                
                <div class="endpoint">
                    <div class="method">POST /render_report</div>
                    <p>Generate HTML report from findings</p>
                </div>
                
                <div class="endpoint">
                    <div class="method">POST /score</div>
                    <p>Calculate review score from findings</p>
                </div>
                
                <h2>AI-Powered Learning</h2>
                
                <div class="endpoint ai">
                    <div class="method">POST /learn_from_repository</div>
                    <p>🤖 NEW: Learn from repository review history using AI analysis</p>
                </div>
                
                <h2>Documentation</h2>
                <p><a href="/docs">Interactive API docs (Swagger UI)</a></p>
                <p><a href="/redoc">ReDoc documentation</a></p>
            </div>
        </body>
    </html>
    """


@app.post("/review", response_model=ReviewResponse)
async def review(req: ReviewRequest, _ok: bool = Depends(require_api_key)):
    """
    Complete PR review pipeline.
    
    This endpoint performs the entire review process:
    1. Fetches PR diff from GitHub
    2. Reviews code changes using LLM
    3. Renders HTML report
    4. Calculates review score
    """
    request_id = req.requestId or make_request_id()
    step_durations = {}
    
    try:
        # Step 1: Fetch PR diff
        with timed(step_durations, "fetch_pr_ms"):
            diff = await fetch_pr_diff_async(req.prUrl)
        
        # Step 2: Review hunks
        with timed(step_durations, "review_ms"):
            findings = await review_hunks_async(diff, None)  # No rules for now
        
        # Step 3: Render HTML report
        with timed(step_durations, "render_ms"):
            html = render_html(findings)
            report_hash = hash_html(html)
        
        # Step 4: Calculate score
        with timed(step_durations, "score_ms"):
            score = calculate_score(findings)
        
        return ReviewResponse(
            score=score,
            findings=findings,
            reportHtml=html,
            reportHash=report_hash,
            stepDurations=step_durations
        )
        
    except Exception as e:
        # Log the error for debugging
        import logging
        logging.error(f"Review failed for request {request_id}: {str(e)}")
        
        # Return standardized error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "REVIEW_FAILED",
                "message": str(e),
                "requestId": request_id
            }
        )


@app.post("/fetch_pr", response_model=FetchPRResponse)
async def fetch_pr(req: FetchPRRequest, _ok: bool = Depends(require_api_key)):
    """Fetch PR diff from GitHub."""
    try:
        diff = await fetch_pr_diff_async(req.prUrl)
        return FetchPRResponse(diffJson=diff)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "GITHUB_ERROR",
                "message": str(e),
                "requestId": make_request_id()
            }
        )


@app.post("/review_hunks", response_model=ReviewHunksResponse)
async def review_hunks(req: ReviewHunksRequest, _ok: bool = Depends(require_api_key)):
    """Review code changes using LLM."""
    try:
        findings = await review_hunks_async(req.diffJson, req.rules)
        return ReviewHunksResponse(findings=findings)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LLM_ERROR",
                "message": str(e),
                "requestId": make_request_id()
            }
        )


@app.post("/render_report", response_model=RenderReportResponse)
async def render_report(req: RenderReportRequest, _ok: bool = Depends(require_api_key)):
    """Generate HTML report from findings."""
    try:
        html = render_html(req.findings)
        report_hash = hash_html(html)
        return RenderReportResponse(reportHtml=html, reportHash=report_hash)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "RENDER_ERROR",
                "message": str(e),
                "requestId": make_request_id()
            }
        )


@app.post("/score", response_model=ScoreResponse)
async def score(req: ScoreRequest, _ok: bool = Depends(require_api_key)):
    """Calculate review score from findings."""
    try:
        score_value = calculate_score(req.findings)
        return ScoreResponse(score=score_value)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SCORE_ERROR",
                "message": str(e),
                "requestId": make_request_id()
            }
        )


def calculate_score(findings) -> float:
    """
    Calculate a review score based on findings.
    
    Higher scores indicate more issues found.
    """
    severity_weights = {
        "CRITICAL": 3.0,
        "BLOCKING": 3.0,
        "MAJOR": 2.0,
        "MINOR": 1.0,
        "NIT": 0.5
    }
    
    total_score = 0.0
    for finding in findings:
        severity = getattr(finding, "severity", "MEDIUM").upper()
        weight = severity_weights.get(severity, 1.0)
        total_score += weight
    
    return float(total_score)


# New AI-powered learning endpoints
@app.post("/learn_from_repository", response_model=LearnFromRepositoryResponse)
async def learn_from_repository_endpoint(req: LearnFromRepositoryRequest, _ok: bool = Depends(require_api_key)):
    """
    Learn from repository review history using AI analysis.
    
    This endpoint analyzes all PRs, reviews, and comments in a repository to:
    1. Identify common review patterns
    2. Learn team preferences
    3. Generate new standards
    4. Understand file-specific issues
    """
    try:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GITHUB_TOKEN environment variable is required"
            )
        
        # Create learning task
        task_id = str(uuid.uuid4())
        learning_tasks[task_id] = {
            "status": "running",
            "progress": 0.0,
            "current_step": "Starting repository analysis...",
            "results": None
        }
        
        # Start learning process (this is a one-time task as requested)
        print(f"🤖 Starting AI learning from repository: {req.repositoryUrl}")
        
        # Run the learning process
        from ..learning import learn_from_repository
        context = learn_from_repository(
            repo_url=req.repositoryUrl,
            token=token,
            max_prs=req.maxPRs
        )
        
        # Save results using the learner instance
        from ..learning import RepositoryLearner
        learner = RepositoryLearner(token)
        output_file = req.outputFile or f"learning_results_{task_id[:8]}.json"
        learner.save_learning_results(context, output_file)
        
        # Update task status
        learning_tasks[task_id]["status"] = "completed"
        learning_tasks[task_id]["progress"] = 100.0
        learning_tasks[task_id]["current_step"] = "Learning completed"
        learning_tasks[task_id]["results"] = {
            "repository": context.repository,
            "summary": {
                "total_prs": context.total_prs,
                "total_reviews": context.total_reviews,
                "total_comments": context.total_comments
            },
            "learned_standards": learner.generate_learned_standards(context),
            "common_issues": context.common_issues,
            "team_preferences": context.team_preferences
        }
        
        return LearnFromRepositoryResponse(
            success=True,
            repository=context.repository,
            summary={
                "total_prs": context.total_prs,
                "total_reviews": context.total_reviews,
                "total_comments": context.total_comments
            },
            learnedStandards=learner.generate_learned_standards(context),
            commonIssues=context.common_issues,
            teamPreferences=context.team_preferences,
            outputFile=output_file,
            message=f"Successfully learned from {context.total_prs} PRs with {context.total_reviews} reviews"
        )
        
    except Exception as e:
        import logging
        logging.error(f"Repository learning failed: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LEARNING_FAILED",
                "message": str(e),
                "requestId": make_request_id()
            }
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "qreviewer-api"}
