# QReviewer

LLM-powered code review tool using Amazon Q via AWS Bedrock.

## Overview

QReviewer fetches GitHub PR diffs, splits them into reviewable hunks, and uses Amazon Q to analyze each hunk for code quality issues. It produces structured findings that can be consumed by other tools or agents.

## Features

- 🔍 **PR Analysis**: Fetch and parse GitHub PR diffs with pagination support
- 📝 **Hunk Extraction**: Split unified diffs into logical code hunks
- 🤖 **AI Review**: Use Amazon Q via Bedrock to review each hunk
- 📊 **Structured Output**: JSON findings with severity, category, and confidence scores
- 🔒 **Security Heuristics**: Automatic detection of security-related issues
- 🎯 **WaaP Integration**: Agent wrapper for team.yaml workflows
- 📋 **Guidelines Support**: Custom project guidelines for consistent reviews
- 🚀 **REST API**: FastAPI service for integration with other tools and services
- 📈 **Continuous Improvement**: Retrain and update standards as repositories evolve

## 🧠 AI Learning System

QReviewer's AI learning system analyzes repository review history to automatically generate new standards, identify team preferences, and improve review quality over time.

### What It Learns

- **Code Quality Patterns**: Recurring issues, best practices, and anti-patterns
- **Team Preferences**: Review styles, approval ratios, and comment patterns
- **File-Specific Standards**: Language-specific and module-specific patterns
- **Common Issues**: Frequently identified problems and their solutions
- **Review Categories**: Security, performance, style, and documentation patterns

### Learning Capabilities

#### Repository Analysis
- Analyze thousands of PRs efficiently with intelligent sampling
- Extract patterns from PR comments, reviews, and file changes
- Generate confidence scores for learned patterns
- Identify team-specific review preferences

#### Module-Focused Learning
- Focus on specific modules instead of entire repositories
- Handle large repositories (100K+ PRs) efficiently
- Configurable PR limits per module and total
- Multiple sampling strategies for different learning goals

#### Standards Generation
- Automatically create new review standards
- Context-aware rule generation
- Severity and category classification
- Integration with existing review workflows

### Learning Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Recent** | Focus on most recent PRs | Current standards and practices |
| **Representative** | Sample across time periods | Comprehensive learning |
| **High Impact** | Focus on PRs with many comments/reviews | Critical issue identification |

### CLI Learning Commands

```bash
# Learn from specific modules in a repository
qrev learn https://github.com/owner/repo \
  --module src/api \
  --module lib/core \
  --module tests \
  --max-prs-per-module 50 \
  --max-total-prs 200 \
  --strategy representative

# List available sampling strategies
qrev list-strategies

# Learn with custom output directory
qrev learn https://github.com/owner/repo \
  --module src \
  --output-dir custom_results
```

### Learning Output

The system generates:
- **Individual module results** for targeted analysis
- **Combined standards** across all modules
- **Team preferences** and review patterns
- **Common issues** with confidence scores
- **JSON output files** for further processing

### Retraining and Updates

- **Retrain anytime** by running the command again
- **Change focus** by selecting different modules
- **Update strategies** based on evolving needs
- **Track progress** across multiple training runs

## Installation

### Prerequisites

- Python 3.10+
- GitHub Personal Access Token
- AWS credentials configured for Bedrock access

### Quick Install

```bash
# Install dependencies
pip install -r requirements.txt

# Clone the repository
git clone https://github.com/org/qreviewer.git
cd qreviewer

# Install in development mode
pip install -e .
```

### Environment Setup

```bash
# Set GitHub token
export GITHUB_TOKEN=your_github_token_here

# Configure AWS credentials (for Bedrock access)
aws configure

# Optional: Set API key for production use
export QREVIEWER_API_KEY=your_api_key_here
```

## Usage

### CLI Commands

#### 1. Fetch PR Files

```bash
# Fetch PR diff and save to file
qrev fetch --pr https://github.com/org/repo/pull/123 --out pr-diff.json

# Or use the module directly
python -m qrev.cli fetch --pr https://github.com/org/repo/pull/123 --out pr-diff.json
```

#### 2. Review Code Hunks

```bash
# Review with default settings
qrev review --inp pr-diff.json --out findings.json

# Review with custom guidelines
qrev review --inp pr-diff.json --out findings.json --guidelines guidelines.md

# Control concurrency
qrev review --inp pr-diff.json --out findings.json --max-concurrency 8
```

#### 3. Summarize Findings

```bash
# Display human-readable summary
qrev summarize --inp findings.json
```

#### 4. AI Learning from Repository

```bash
# Learn from specific modules in a repository
qrev learn https://github.com/owner/repo \
  --module src/api \
  --module lib/core \
  --max-prs-per-module 50

# List available learning strategies
qrev list-strategies

# Learn with custom parameters
qrev learn https://github.com/owner/repo \
  --module src \
  --strategy high_impact \
  --max-total-prs 200 \
  --output-dir custom_results
```

#### 5. Standards Management

```bash
# View available standards
qrev standards list

# Apply standards to review
qrev review --inp pr-diff.json --standards security,performance

# Create custom standards
qrev standards create --name "team_standards" --file standards.json
```

### WaaP Agent Mode

For integration with team.yaml workflows:

```bash
# Create context file
cat > context.json << EOF
{
  "pr": {
    "url": "https://github.com/org/repo/pull/123"
  },
  "guidelines": {
    "path": "project-guidelines.md"
  }
}
EOF

# Run the agent
python -m agents.qreviewer
```

The agent will:
- Read `pr.url` from `context.json`
- Fetch and review the PR
- Write results to `results/review.findings.json`
- Update `context.json` with review metadata

## API Server Mode

QReviewer now includes a FastAPI service that exposes code review functionality through REST endpoints, making it easy to integrate with CI/CD pipelines, web applications, and other services.

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN=your_github_token
export AWS_REGION=us-east-1
export MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Optional: Set API key for production
export QREVIEWER_API_KEY=your_api_key

# Start development server
make dev
# or
uvicorn qrev.api.app:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Main Endpoint

- **`POST /review`** - Complete PR review pipeline (fetch → review → render → score)

#### AI Learning Endpoints

- **`POST /learn_from_repository`** - Learn from repository review history using AI analysis
- **`GET /learning_status/{task_id}`** - Check status of learning tasks
- **`POST /apply_learned_standards`** - Apply learned standards to existing standards

#### Composition Endpoints

- **`POST /fetch_pr`** - Fetch PR diff from GitHub
- **`POST /review_hunks`** - Review code changes using LLM
- **`POST /render_report`** - Generate HTML report from findings
- **`POST /score`** - Calculate review score from findings

#### GitHub Integration Endpoints

- **`POST /post_review`** - Post review comments to GitHub PR
- **`POST /post_comment`** - Post general comments to GitHub PR
- **`GET /get_reviews`** - Retrieve existing reviews from GitHub PR

#### Utility Endpoints

- **`GET /`** - API information and documentation links
- **`GET /health`** - Health check endpoint
- **`GET /docs`** - Interactive API documentation (Swagger UI)
- **`GET /redoc`** - ReDoc documentation

### Example API Usage

#### Complete Review

```bash
curl -X POST "http://localhost:8000/review" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "prUrl": "https://github.com/org/repo/pull/123",
    "requestId": "review-123"
  }'
```

#### Step-by-Step Review

```bash
# 1. Fetch PR diff
curl -X POST "http://localhost:8000/fetch_pr" \
  -H "Content-Type: application/json" \
  -d '{"prUrl": "https://github.com/org/repo/pull/123"}'

# 2. Review hunks
curl -X POST "http://localhost:8000/review_hunks" \
  -H "Content-Type: application/json" \
  -d '{"diffJson": {...}}'

# 3. Render report
curl -X POST "http://localhost:8000/render_report" \
  -H "Content-Type: application/json" \
  -d '{"findings": [...]}'

# 4. Calculate score
curl -X POST "http://localhost:8000/score" \
  -H "Content-Type: application/json" \
  -d '{"findings": [...]}'
```

#### AI Learning from Repository

```bash
# Learn from repository review history
curl -X POST "http://localhost:8000/learn_from_repository" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "repositoryUrl": "https://github.com/owner/repo",
    "maxPRs": 100,
    "includeComments": true,
    "includeReviews": true
  }'

# Post review to GitHub PR
curl -X POST "http://localhost:8000/post_review" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "prUrl": "https://github.com/owner/repo/pull/123",
    "findings": [...],
    "reviewMessage": "AI-powered code review completed"
  }'
```

### API Response Format

#### Review Response

```json
{
  "score": 2.5,
  "findings": [
    {
      "file": "src/example.py",
      "hunk_header": "@@ -10,6 +10,8 @@",
      "severity": "major",
      "category": "security",
      "message": "Escape untrusted HTML before rendering.",
      "confidence": 0.86,
      "suggested_patch": "```suggestion\nreturn sanitize(html)\n```",
      "line_hint": 18
    }
  ],
  "reportHtml": "<!DOCTYPE html>...",
  "reportHash": "sha256:abc123...",
  "stepDurations": {
    "fetch_pr_ms": 1500,
    "review_ms": 8000,
    "render_ms": 200,
    "score_ms": 50
  }
}
```

### Authentication

The API supports optional Bearer token authentication:

- **Development Mode**: No authentication required when `QREVIEWER_API_KEY` is not set
- **Production Mode**: Set `QREVIEWER_API_KEY` environment variable to require valid Bearer tokens

```bash
# Set API key
export QREVIEWER_API_KEY=your_secret_key

# Use in requests
curl -H "Authorization: Bearer your_secret_key" \
  http://localhost:8000/review
```

### Docker Deployment

```bash
# Build image
make docker-build
# or
docker build -t qreviewer-api .

# Run with Docker Compose
make docker-run
# or
docker-compose up --build

# Run standalone container
docker run -p 8000:8000 \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e MODEL_ID=$MODEL_ID \
  -e QREVIEWER_API_KEY=$API_KEY \
  qreviewer-api
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GITHUB_TOKEN` | GitHub API access token | - | Yes |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` | Yes |
| `AWS_ACCESS_KEY_ID` | AWS access key | - | Yes* |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | Yes* |
| `MODEL_ID` | Bedrock model ID | - | Yes |
| `QREVIEWER_API_KEY` | API key for authentication | - | No |
| `FETCH_TIMEOUT_SEC` | GitHub API timeout | `30` | No |
| `REVIEW_TIMEOUT_SEC` | LLM review timeout | `120` | No |
| `MAX_FILES` | Maximum files to process | `200` | No |
| `MAX_PATCH_BYTES` | Maximum patch size | `1,000,000` | No |

*Can use IAM instance role instead

## Output Formats

### PR Diff JSON

```json
{
  "pr": {
    "url": "https://github.com/org/repo/pull/123",
    "number": 123,
    "repo": "org/repo"
  },
  "files": [
    {
      "path": "src/example.py",
      "status": "modified",
      "patch": "@@ -1,3 +1,6 @@\n-...\n+...\n",
      "additions": 3,
      "deletions": 1
    }
  ]
}
```

### Findings JSON

```json
{
  "pr": {
    "url": "https://github.com/org/repo/pull/123",
    "number": 123,
    "repo": "org/repo"
  },
  "findings": [
    {
      "file": "src/example.py",
      "hunk_header": "@@ -10,6 +10,8 @@",
      "severity": "major",
      "category": "security",
      "message": "Escape untrusted HTML before rendering.",
      "confidence": 0.86,
      "suggested_patch": "```suggestion\nreturn sanitize(html)\n```",
      "line_hint": 18
    }
  ]
}
```

## Configuration

### GitHub Authentication

Set the `GITHUB_TOKEN` environment variable with a Personal Access Token that has access to the repositories you want to review.

### AWS Bedrock Integration

The current implementation includes a stub for Amazon Q integration. To wire up the real Bedrock client:

1. **Install boto3**:
   ```bash
   pip install boto3
   ```

2. **Update `qrev/q_client.py`**:
   - Replace the stub implementation in `review_hunk()`
   - Use the provided example code as a starting point
   - Configure your preferred Amazon Q model

3. **Configure AWS credentials**:
   ```bash
   aws configure
   # Or set environment variables:
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

### Project Guidelines

Create a `guidelines.md` file with your project's coding standards:

```markdown
# Project Guidelines

## Security
- Always validate user inputs
- Use parameterized queries

## Style
- Follow PEP 8
- Add type hints
```

## Project Structure

```
QReviewer/
├── qrev/                    # Core package
│   ├── __init__.py
│   ├── cli.py              # Typer CLI commands
│   ├── models.py            # Pydantic data models
│   ├── github_api.py        # GitHub API client
│   ├── diff.py              # Diff parsing utilities
│   ├── prompts.py           # LLM prompt builders
│   ├── q_client.py          # Amazon Q client (stub)
│   ├── report.py            # HTML report generation
│   └── api/                 # FastAPI service
│       ├── __init__.py
│       ├── app.py           # FastAPI application
│       ├── models.py        # API request/response models
│       ├── security.py      # Authentication middleware
│       ├── utils.py         # Utility functions
│       └── compat.py        # Compatibility layer
├── waap/                    # WaaP utilities
│   ├── __init__.py
│   └── blackboard.py        # Context management
├── agents/                  # Agent wrappers
│   ├── __init__.py
│   └── qreviewer.py         # Main WaaP agent
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_api.py          # API endpoint tests
├── results/                 # Output directory (auto-created)
├── example-guidelines.md    # Sample guidelines
├── example-context.json     # Sample context
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
├── Dockerfile               # Docker image
├── docker-compose.yml       # Docker Compose
├── Makefile                 # Development commands
├── pytest.ini              # Test configuration
└── README.md               # This file
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
make test
# or
pytest

# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8
```

### Development Commands

```bash
# Show available commands
make help

# Install dependencies
make install

# Run development server
make dev

# Run tests
make test

# Build Docker image
make docker-build

# Run with Docker Compose
make docker-run

# Stop Docker services
make docker-stop

# Clean up generated files
make clean

# Test API endpoints
make test-api
```

### Adding New Features

1. **Models**: Extend `qrev/models.py` for new data structures
2. **API**: Add new endpoints in `qrev/api/app.py`
3. **Prompts**: Customize prompts in `qrev/prompts.py`
4. **CLI**: Add new commands in `qrev/cli.py`

### New AI Learning Modules

1. **`qrev/learning.py`** - Repository analysis and pattern extraction
2. **`qrev/cli_learning.py`** - CLI for module-focused learning
3. **`qrev/standards.py`** - Review standards and context management
4. **`qrev/github_review.py`** - GitHub PR review and commenting

### Architecture Overview

```
QReviewer
├── Core Review Engine
│   ├── PR fetching and parsing
│   ├── Hunk extraction and analysis
│   └── LLM integration (Amazon Q)
├── AI Learning System
│   ├── Repository analysis
│   ├── Pattern extraction
│   ├── Standards generation
│   └── Module-focused learning
├── Standards Management
│   ├── Context-aware rules
│   ├── Team preferences
│   └── Custom guidelines
└── GitHub Integration
    ├── Review posting
    ├── Inline comments
    └── PR management
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=qrev

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestReviewEndpoint

# Run specific test method
pytest tests/test_api.py::TestReviewEndpoint::test_review_endpoint_success
```

### Test Coverage

The test suite covers:
- ✅ API endpoint functionality
- ✅ Request/response validation
- ✅ Error handling
- ✅ Security middleware
- ✅ HTML report generation
- ✅ Utility functions
- ✅ AI learning system
- ✅ Module-focused learning
- ✅ Standards management
- ✅ GitHub integration
- ✅ CLI learning commands

## Troubleshooting

### Common Issues

**GitHub API Rate Limits**: Ensure your token has appropriate permissions and consider using a GitHub App for higher limits.

**Bedrock Access**: Verify your AWS credentials and Bedrock permissions in the target region.

**Large PRs**: The tool handles pagination automatically, but very large PRs may take time to process.

**AI Learning**: For large repositories, use module-focused learning with appropriate PR limits to avoid rate limiting.

**Learning Results**: Check output directories for generated standards and analysis results.

**API Authentication**: Check that your `QREVIEWER_API_KEY` is set correctly if using authentication.

### Debug Mode

Enable verbose logging:

```bash
export PYTHONPATH=.
python -m qrev.cli fetch --pr https://github.com/org/repo/pull/123 --out debug.json
```

### API Debugging

```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Test endpoints with verbose output
curl -v -X POST "http://localhost:8000/review" \
  -H "Content-Type: application/json" \
  -d '{"prUrl": "https://github.com/org/repo/pull/123"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/org/qreviewer/issues)
- **Documentation**: [Wiki](https://github.com/org/qreviewer/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/org/qreviewer/discussions)
