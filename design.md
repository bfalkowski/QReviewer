# QReviewer FastAPI Service Design

## Overview
Add a production-ready FastAPI service to QReviewer while preserving the existing Typer CLI. The service will expose code review functionality through REST APIs, reusing existing modules rather than duplicating logic.

## Goals
1. **Preserve CLI**: Keep existing CLI intact for local/dev use
2. **Add FastAPI**: Expose code review pipeline through REST endpoints
3. **Composable API**: Provide both one-shot and step-by-step endpoints
4. **Production Ready**: Include idempotency, error handling, timeouts, retries
5. **Integration Ready**: Return structured JSON compatible with Appian/Agent Studio

## Architecture

### High-Level Design
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App  │    │   Existing      │    │   External      │
│   (New)        │    │   Modules       │    │   Services      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ /review        │───▶│ github_api.py   │───▶│ GitHub API     │
│ /fetch_pr      │    │ q_client.py     │───▶│ AWS Bedrock    │
│ /review_hunks  │    │ diff.py         │    │                 │
│ /render_report │    │ models.py       │    │                 │
│ /score         │    └─────────────────┘    └─────────────────┘
└─────────────────┘
```

### API Endpoints

#### Main Endpoint
- `POST /review` - Complete PR review pipeline (fetch → review → render → score)

#### Composition Endpoints
- `POST /fetch_pr` - Fetch PR diff from GitHub
- `POST /review_hunks` - Review code changes using LLM
- `POST /render_report` - Generate HTML report from findings
- `POST /score` - Calculate review score from findings

## Implementation Plan

### Phase 1: Core Infrastructure
1. Create API package structure
2. Implement Pydantic models
3. Add security middleware
4. Create utility functions

### Phase 2: API Endpoints
1. Implement main `/review` endpoint
2. Add composition endpoints
3. Integrate with existing modules
4. Add error handling and validation

### Phase 3: Production Features
1. Add timing and metrics
2. Implement idempotency
3. Add timeouts and retries
4. Create Dockerfile

### Phase 4: Testing & Documentation
1. Write comprehensive tests
2. Update README
3. Add deployment examples

## File Structure

```
qrev/
├── __init__.py
├── cli.py              # Existing CLI (unchanged)
├── api/                # New API package
│   ├── __init__.py
│   ├── app.py         # FastAPI application
│   ├── models.py      # Pydantic models
│   ├── security.py    # Authentication middleware
│   └── utils.py       # Utility functions
├── report.py          # HTML report generation
├── github_api.py      # Existing (ensure async support)
├── q_client.py        # Existing (ensure async support)
└── models.py          # Existing (ensure compatibility)
```

## Data Models

### Request Models
```python
class ReviewRequest(BaseModel):
    prUrl: str
    guidelinesUrl: Optional[str] = None
    requestId: Optional[str] = None

class FetchPRRequest(BaseModel):
    prUrl: str

class ReviewHunksRequest(BaseModel):
    diffJson: Dict[str, Any]
    rules: Optional[Dict[str, Any]] = None

class RenderReportRequest(BaseModel):
    findings: List[Finding]

class ScoreRequest(BaseModel):
    findings: List[Finding]
```

### Response Models
```python
class Finding(BaseModel):
    file: str
    line: int
    severity: str
    ruleId: Optional[str] = None
    title: str
    details: str
    suggestion: str

class ReviewResponse(BaseModel):
    score: Optional[float] = None
    findings: List[Finding]
    reportHtml: Optional[str] = None
    reportHash: Optional[str] = None
    stepDurations: Optional[Dict[str, int]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None
```

## Configuration

### Environment Variables
- `GITHUB_TOKEN` - GitHub API access token
- `AWS_REGION` - AWS region for Bedrock
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` - AWS credentials (or instance role)
- `MODEL_ID` - Bedrock model ID (e.g., `anthropic.claude-3-5-sonnet-20241022-v2:0`)
- `QREVIEWER_API_KEY` - Optional API key for authentication
- `FETCH_TIMEOUT_SEC` - GitHub API timeout (default: 30)
- `REVIEW_TIMEOUT_SEC` - LLM review timeout (default: 120)
- `MAX_FILES` - Maximum files to process (default: 200)
- `MAX_PATCH_BYTES` - Maximum patch size (default: 1,000,000)

### Dependencies
```
fastapi
uvicorn[standard]
pydantic
jinja2
httpx
tenacity
boto3
```

## Security

### Authentication
- Optional Bearer token authentication via `QREVIEWER_API_KEY`
- Dev mode: open endpoints when no API key configured
- Production: require valid Bearer token

### Rate Limiting
- Consider adding rate limiting for production use
- Per-endpoint and per-client limits

## Error Handling

### Standard Error Response
```json
{
  "error": "ERROR_CODE",
  "message": "Human readable error message",
  "requestId": "uuid-string"
}
```

### Error Codes
- `REVIEW_FAILED` - General review pipeline failure
- `GITHUB_ERROR` - GitHub API errors
- `LLM_ERROR` - Bedrock/LLM errors
- `VALIDATION_ERROR` - Request validation errors
- `TIMEOUT_ERROR` - Operation timeout

## Performance & Reliability

### Timeouts
- GitHub API: 30 seconds (configurable)
- LLM review: 120 seconds (configurable)
- Report rendering: 10 seconds (configurable)

### Retries
- GitHub API: Exponential backoff with jitter
- LLM calls: Retry on transient failures
- Network calls: Use tenacity for retry logic

### Metrics
- Step-by-step timing (`stepDurations`)
- Request ID tracking for debugging
- Performance monitoring hooks

## Testing Strategy

### Unit Tests
- Mock external dependencies (GitHub, Bedrock)
- Test all endpoint variations
- Validate error handling paths

### Integration Tests
- Test with real GitHub API (using test repo)
- Test with Bedrock (using small model)
- End-to-end pipeline testing

### Test Coverage Goals
- API endpoints: 90%+
- Error handling: 95%+
- Integration paths: 80%+

## Deployment

### Development
```bash
export QREVIEWER_API_KEY=devkey
export GITHUB_TOKEN=ghp_...
export MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
uvicorn qrev.api.app:app --reload
```

### Production
```bash
# Build Docker image
docker build -t qreviewer-api .

# Run container
docker run -p 8000:8000 \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e MODEL_ID=$MODEL_ID \
  -e QREVIEWER_API_KEY=$API_KEY \
  qreviewer-api
```

## Migration & Compatibility

### Breaking Changes
- None - existing CLI functionality preserved
- All existing imports and function calls remain valid

### Shared Logic
- Refactor common functionality into shared modules
- Both CLI and API use same core functions
- Maintain single source of truth for business logic

## Future Enhancements

### Phase 2 Features
- Caching layer for repeated requests
- Webhook support for GitHub events
- Batch processing for multiple PRs
- Custom rule engine integration

### Monitoring & Observability
- Prometheus metrics
- Structured logging
- Distributed tracing
- Health check endpoints

## Acceptance Criteria

### Functional Requirements
- [ ] `/review` endpoint returns valid `ReviewResponse`
- [ ] All composition endpoints work with expected schemas
- [ ] Existing CLI commands function unchanged
- [ ] Docker build and run successful
- [ ] Tests pass for happy and error paths

### Non-Functional Requirements
- [ ] API response time < 2 seconds for simple PRs
- [ ] Support for PRs up to 200 files
- [ ] Graceful handling of timeouts
- [ ] Proper error messages for debugging
- [ ] Idempotent operations where applicable

## Implementation Notes

### Key Decisions
1. **Async vs Sync**: Use async where it makes sense (HTTP calls), sync for CPU-bound tasks
2. **Error Handling**: Structured errors with consistent format across all endpoints
3. **Validation**: Pydantic models for request/response validation
4. **Testing**: Comprehensive test coverage with mocked external dependencies

### Risks & Mitigation
1. **GitHub API Limits**: Implement rate limiting and pagination handling
2. **LLM Costs**: Add timeout controls and request size limits
3. **Memory Usage**: Stream large diffs and implement size limits
4. **Security**: Validate all inputs and implement proper authentication

### Success Metrics
- API endpoints respond within SLA
- Zero breaking changes to existing CLI
- Test coverage > 90%
- Successful Docker deployment
- Integration with Appian/Agent Studio successful