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

## Installation

### Prerequisites

- Python 3.10+
- GitHub Personal Access Token
- AWS credentials configured for Bedrock access

### Quick Install

```bash
# Install dependencies
pip install typer[all] pydantic requests rich

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
│   └── q_client.py          # Amazon Q client (stub)
├── waap/                    # WaaP utilities
│   ├── __init__.py
│   └── blackboard.py        # Context management
├── agents/                  # Agent wrappers
│   ├── __init__.py
│   └── qreviewer.py         # Main WaaP agent
├── results/                 # Output directory (auto-created)
├── example-guidelines.md    # Sample guidelines
├── example-context.json     # Sample context
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8
```

### Adding New Features

1. **Models**: Extend `qrev/models.py` for new data structures
2. **API**: Add new endpoints in `qrev/github_api.py`
3. **Prompts**: Customize prompts in `qrev/prompts.py`
4. **CLI**: Add new commands in `qrev/cli.py`

## Troubleshooting

### Common Issues

**GitHub API Rate Limits**: Ensure your token has appropriate permissions and consider using a GitHub App for higher limits.

**Bedrock Access**: Verify your AWS credentials and Bedrock permissions in the target region.

**Large PRs**: The tool handles pagination automatically, but very large PRs may take time to process.

### Debug Mode

Enable verbose logging:

```bash
export PYTHONPATH=.
python -m qrev.cli fetch --pr https://github.com/org/repo/pull/123 --out debug.json
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
