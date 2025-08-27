# QReviewer

LLM-powered code review tool with **Amazon Q CLI as the default backend**, plus support for AWS Bedrock and OpenAI.

## 🚀 **NEW: Amazon Q CLI Integration (Default Backend)**

QReviewer now uses **Amazon Q CLI as the default LLM backend** via SSH to your remote Q machine. This provides:

- **🎯 Superior Code Understanding**: Q's specialized knowledge for code review patterns
- **🔒 Enhanced Security**: Q's security-focused insights and recommendations  
- **📱 Easy Setup**: Simple SSH configuration to your Q machine
- **💪 Fallback Options**: Automatic fallback to Bedrock or OpenAI if needed

### **Why Amazon Q CLI?**

Amazon Q CLI provides:
- **Repository Context**: Understands your specific codebase and patterns
- **Security Expertise**: Specialized knowledge for identifying security issues
- **Multi-language Support**: Excellent coverage across Python, JavaScript, Java, Go, etc.
- **Team Learning**: Adapts to your team's coding standards over time

### **Execution Modes**

| Mode | Configuration | Use Case |
|------|---------------|----------|
| **Local (Default)** | No SSH config needed | Same machine as Q CLI |
| **Remote SSH** | Set `Q_CLI_HOST` and `Q_CLI_USER` | Different machine via SSH |
| **Fallback** | Set Bedrock or OpenAI credentials | When Q CLI unavailable |

## Overview

QReviewer fetches GitHub PR diffs, splits them into reviewable hunks, and uses **Amazon Q CLI** (or your chosen LLM backend) to analyze each hunk for code quality issues. It produces structured findings that can be consumed by other tools or agents.

## Features

- 🔍 **PR Analysis**: Fetch and parse GitHub PR diffs with pagination support
- 📝 **Hunk Extraction**: Split unified diffs into logical code hunks
- 🤖 **AI Review**: **Amazon Q CLI as default** with fallback to Bedrock/OpenAI
- 📊 **Structured Output**: JSON findings with severity, category, and confidence scores
- 🔒 **Security Heuristics**: Automatic detection of security-related issues
- 🎯 **WaaP Integration**: Agent wrapper for team.yaml workflows
- 📋 **Guidelines Support**: Custom project guidelines for consistent reviews
- 🚀 **REST API**: FastAPI service for integration with other tools and services
- 📈 **Continuous Improvement**: Retrain and update standards as repositories evolve
- ⚙️ **Multi-Backend LLM**: Switch between Amazon Q CLI, AWS Bedrock, and OpenAI
- 🛡️ **Robust Error Handling**: Graceful degradation and clear error messages

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
- **Amazon Q CLI machine** on your network (default)
- **OR** AWS credentials for Bedrock access (fallback)
- **OR** OpenAI API key (fallback)

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

#### **Option 1: Amazon Q CLI (Recommended - Default)**

```bash
# Set GitHub token
export GITHUB_TOKEN=your_github_token_here

# Amazon Q CLI Configuration
export QREVIEWER_LLM_BACKEND=amazon_q
export Q_CLI_HOST=192.168.1.100      # IP/hostname of your Q machine
export Q_CLI_USER=your_username      # SSH username on Q machine
export Q_CLI_PORT=22                 # SSH port (default: 22)
export Q_CLI_KEY_PATH=~/.ssh/id_rsa # SSH key path (optional)

# Optional: Set API key for production use
export QREVIEWER_API_KEY=your_api_key_here
```

#### **Option 2: AWS Bedrock (Fallback)**

```bash
# Set GitHub token
export GITHUB_TOKEN=your_github_token_here

# AWS Bedrock Configuration
export QREVIEWER_LLM_BACKEND=bedrock
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_key
export MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Optional: Set API key for production use
export QREVIEWER_API_KEY=your_api_key_here
```

#### **Option 3: OpenAI (Fallback)**

```bash
# Set GitHub token
export GITHUB_TOKEN=your_github_token_here

# OpenAI Configuration
export QREVIEWER_LLM_BACKEND=openai
export OPENAI_API_KEY=your_openai_api_key
export OPENAI_MODEL=gpt-4

# Optional: Set API key for production use
export QREVIEWER_API_KEY=your_api_key_here
```

### Configuration Management

QReviewer includes a powerful configuration management system:

```bash
# Show current configuration
qrev config show

# Validate configuration
qrev config validate

# Show required environment variables
qrev config env

# Test LLM connection
qrev config test
```

### 🛡️ Error Handling & Resilience

QReviewer provides robust error handling and graceful degradation:

#### **LLM Backend Failures**

When Amazon Q CLI is unavailable, QReviewer:

- **Returns Structured Errors**: JSON responses with detailed error information
- **Maintains API Contract**: HTTP 200 responses with error context in findings
- **Provides Fallback Options**: Automatic switch to Bedrock or OpenAI if configured
- **Continues Operation**: System remains functional for non-LLM operations

#### **Error Response Examples**

**Q CLI Not Found:**
```json
{
  "findings": [{
    "severity": "info",
    "category": "system", 
    "message": "LLM response parsing failed: Amazon Q CLI error: Local Q CLI execution error: Q CLI command failed: bash: q: command not found",
    "confidence": 0.1
  }]
}
```

**Configuration Issues:**
```bash
qrev config validate
❌ Configuration errors:
   - LLM backend 'amazon_q' is not properly configured
```

#### **Common Error Scenarios**

| Scenario | Error Message | Resolution |
|----------|---------------|------------|
| **Q CLI Missing** | `bash: q: command not found` | Install Q CLI or use fallback backend |
| **SSH Connection Failed** | `SSH command failed: Connection refused` | Check SSH config and network |
| **Rate Limit Exceeded** | `GitHub API error: 403` | Wait for rate limit reset |
| **Invalid PR URL** | `Invalid GitHub repository URL` | Check PR URL format |
| **Authentication Failed** | `GitHub API error: 401` | Verify GITHUB_TOKEN |

#### **Fallback Strategy**

```bash
# Primary: Amazon Q CLI (local or SSH)
QREVIEWER_LLM_BACKEND=amazon_q

# Fallback 1: AWS Bedrock
QREVIEWER_LLM_BACKEND=bedrock
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Fallback 2: OpenAI
QREVIEWER_LLM_BACKEND=openai
OPENAI_API_KEY=your_key
```

#### **Debugging & Troubleshooting**

```bash
# Test current configuration
qrev config test

# Show detailed config info
qrev config show

# Validate all settings
qrev config validate

# Check environment variables
qrev config env
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
# Review with default settings (uses Amazon Q CLI)
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

# Set environment variables (see Environment Setup above)
export GITHUB_TOKEN=your_github_token
export Q_CLI_HOST=192.168.1.100
export Q_CLI_USER=your_username

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
  -d '{
    "prUrl": "https://github.com/org/repo/pull/123",
    "guidelines": "Follow PEP 8 style guidelines",
    "maxConcurrency": 4
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
  -e Q_CLI_HOST=$Q_CLI_HOST \
  -e Q_CLI_USER=$Q_CLI_USER \
  -e QREVIEWER_API_KEY=$API_KEY \
  qreviewer-api
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GITHUB_TOKEN` | GitHub API access token | - | Yes |
| `QREVIEWER_LLM_BACKEND` | LLM backend to use | `amazon_q` | No |
| `Q_CLI_HOST` | Hostname/IP of Q machine | - | Yes* |
| `Q_CLI_USER` | SSH username on Q machine | - | Yes* |
| `Q_CLI_PORT` | SSH port | `22` | No |
| `Q_CLI_KEY_PATH` | SSH private key path | Default SSH key | No |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` | Yes** |
| `AWS_ACCESS_KEY_ID` | AWS access key | - | Yes** |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | Yes** |
| `MODEL_ID` | Bedrock model ID | - | Yes** |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes*** |
| `OPENAI_MODEL` | OpenAI model | `gpt-4` | No |
| `QREVIEWER_API_KEY` | API key for authentication | - | No |
| `FETCH_TIMEOUT_SEC` | GitHub API timeout | `30` | No |
| `REVIEW_TIMEOUT_SEC` | LLM review timeout | `120` | No |
| `MAX_FILES` | Maximum files to process | `200` | No |
| `MAX_PATCH_BYTES` | Maximum patch size | `1,000,000` | No |

*Required for Amazon Q CLI backend
**Required for AWS Bedrock backend  
***Required for OpenAI backend

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

### **Amazon Q CLI Integration (Default)**

QReviewer is now configured to use **Amazon Q CLI as the default backend**:

1. **Install Amazon Q CLI** on a machine in your network
2. **Configure SSH access** to that machine
3. **Set environment variables**:
   ```bash
   export Q_CLI_HOST=192.168.1.100
   export Q_CLI_USER=your_username
   export Q_CLI_PORT=22
   export Q_CLI_KEY_PATH=~/.ssh/id_rsa  # Optional
   ```

4. **Test the connection**:
   ```bash
   qrev config test
   ```

### **AWS Bedrock Integration (Fallback)**

To use AWS Bedrock as a fallback:

1. **Install boto3**:
   ```bash
   pip install boto3
   ```

2. **Set environment variables**:
   ```bash
   export QREVIEWER_LLM_BACKEND=bedrock
   export AWS_REGION=us-east-1
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
   ```

3. **Configure AWS credentials**:
   ```bash
   aws configure
   ```

### **OpenAI Integration (Fallback)**

To use OpenAI as a fallback:

1. **Install openai**:
   ```bash
   pip install openai
   ```

2. **Set environment variables**:
   ```bash
   export QREVIEWER_LLM_BACKEND=openai
   export OPENAI_API_KEY=your_api_key
   export OPENAI_MODEL=gpt-4
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
│   ├── api/                # FastAPI service
│   ├── cli.py              # Main CLI interface
│   ├── cli_config.py       # Configuration management CLI
│   ├── cli_learning.py     # AI learning CLI
│   ├── config.py           # Configuration management
│   ├── llm_client.py       # Multi-backend LLM client
│   ├── github_api.py       # GitHub API integration
│   ├── diff.py             # Diff parsing and hunk extraction
│   ├── models.py           # Data models
│   ├── prompts.py          # LLM prompts
│   ├── report.py           # HTML report generation
│   ├── standards.py        # Review standards management
│   ├── learning.py         # AI learning system
│   └── github_review.py    # GitHub PR review posting
├── learning_results/        # AI learning outputs (organized by repo)
├── tests/                  # Test files and demos
├── standards/              # Default review standards
├── config.env.example      # Configuration template
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container
├── docker-compose.yml      # Docker Compose setup
├── Makefile                # Development commands
└── README.md               # This file
```

## **Amazon Q CLI Setup Guide**

### **Step 1: Install Amazon Q CLI**

On your Q machine:
```bash
# Follow Amazon's official installation guide
# https://docs.aws.amazon.com/q/latest/developer-guide/cli.html
```

### **Step 2: Configure SSH Access**

From your development machine:
```bash
# Test SSH connection
ssh your_username@192.168.1.100

# Test Q CLI access
ssh your_username@192.168.1.100 "q --version"
```

### **Step 3: Configure QReviewer**

```bash
# Set environment variables
export Q_CLI_HOST=192.168.1.100
export Q_CLI_USER=your_username
export GITHUB_TOKEN=your_github_token

# Test configuration
qrev config test
```

### **Step 4: Verify Integration**

```bash
# Test with a simple review
qrev review --inp test-diff.json --out test-findings.json
```

## **Benefits of Amazon Q CLI Integration**

1. **🎯 Superior Code Understanding**: Q understands your codebase context
2. **🔒 Enhanced Security**: Specialized security knowledge and patterns
3. **📱 Easy Setup**: Simple SSH configuration, no API keys needed
4. **💪 Reliable**: Runs on your infrastructure, no external dependencies
5. **🔄 Learning**: Q improves over time with your team's patterns
6. **💰 Cost Effective**: No per-token charges, just your infrastructure costs

## **Fallback Strategy**

QReviewer automatically handles fallbacks:

1. **Primary**: Amazon Q CLI (if configured)
2. **Fallback 1**: AWS Bedrock (if configured)
3. **Fallback 2**: OpenAI (if configured)
4. **Last Resort**: Stub implementation with warnings

This ensures your code reviews continue working even if one backend is unavailable.

## **Troubleshooting**

### **Amazon Q CLI Issues**

```bash
# Test SSH connection
ssh -v your_username@192.168.1.100

# Test Q CLI directly
ssh your_username@192.168.1.100 "q chat --prompt 'Hello'"

# Check configuration
qrev config show
qrev config validate
```

### **Common Issues**

1. **SSH Connection Failed**: Check network, firewall, SSH configuration
2. **Q CLI Not Found**: Verify Q CLI installation on remote machine
3. **Permission Denied**: Check SSH key permissions and user access
4. **Timeout Errors**: Increase `REVIEW_TIMEOUT_SEC` environment variable

### **Performance Tuning**

```bash
# Increase timeouts for large PRs
export REVIEW_TIMEOUT_SEC=300
export FETCH_TIMEOUT_SEC=60

# Adjust concurrency
qrev review --inp pr-diff.json --max-concurrency 2
```

## **Migration from Previous Versions**

If you're upgrading from a previous version:

1. **Backup your configuration**:
   ```bash
   cp .env .env.backup
   ```

2. **Update environment variables**:
   ```bash
   # Old: AWS Bedrock only
   export MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
   
   # New: Amazon Q CLI (default)
   export Q_CLI_HOST=your_q_machine_ip
   export Q_CLI_USER=your_username
   ```

3. **Test the new configuration**:
   ```bash
   qrev config test
   ```

4. **Run a test review** to ensure everything works

## **Contributing**

We welcome contributions! Please see our contributing guidelines for details.

## **License**

This project is licensed under the MIT License - see the LICENSE file for details.
