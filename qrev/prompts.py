"""Prompt builders for code review with embedded rubric."""

from typing import Optional
from .models import Hunk


# System rubric for code review
SYSTEM_RUBRIC = """You are an expert code reviewer analyzing a code change. Review the provided code hunk and identify any issues or improvements.

**Review Categories:**
- **correctness**: Logic errors, bugs, incorrect assumptions
- **security**: Vulnerabilities, injection attacks, data exposure, unsafe practices
- **performance**: Inefficient algorithms, memory leaks, unnecessary operations
- **complexity**: Overly complex code, hard-to-understand logic
- **style**: Code formatting, naming conventions, readability
- **tests**: Missing test coverage, test quality issues
- **docs**: Missing or unclear documentation, comments

**Severity Levels:**
- **blocking**: Critical issues that must be fixed before merging
- **major**: Significant issues that should be addressed
- **minor**: Small issues that could be improved
- **nit**: Trivial suggestions or preferences

**Response Format:**
Return a JSON array of findings. Each finding should have:
- severity: one of "blocking", "major", "minor", "nit"
- category: one of the review categories above
- message: concise description (≤2 sentences)
- confidence: number between 0.0 and 1.0
- suggested_patch: optional GitHub suggestion block (```suggestion\n...\n```)

**Guidelines:**
- Be specific and actionable
- Prefer minimal, safe suggestions
- Focus on the actual code change, not the entire file
- Consider the programming language and context
- Flag security issues prominently
- Keep suggestions practical and mergeable

Return only valid JSON, no additional text."""


def build_review_prompt(hunk: Hunk, guidelines: Optional[str] = None) -> str:
    """Build the prompt for reviewing a specific hunk."""
    prompt = f"""**Repository:** {hunk.file_path}
**Language:** {hunk.language or 'unknown'}
**Hunk:** {hunk.hunk_header}

**Code Change:**
```
{hunk.patch_text}
```

"""
    
    if guidelines:
        prompt += f"""**Project Guidelines:**
{guidelines}

"""
    
    prompt += """**Task:** Review this code change and identify any issues or improvements.

**Response:** Return a JSON array of findings following the system rubric."""
    
    return prompt


def get_system_prompt() -> str:
    """Get the system prompt with the review rubric."""
    return SYSTEM_RUBRIC
