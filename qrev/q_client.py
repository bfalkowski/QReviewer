"""Amazon Q client for code review via Bedrock."""

import json
import logging
from typing import List, Optional
from .models import Hunk, Finding
from .prompts import get_system_prompt, build_review_prompt

logger = logging.getLogger(__name__)


class QClientError(Exception):
    """Q client error."""
    pass


def review_hunk(hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
    """
    Review a code hunk using Amazon Q via Bedrock.
    
    TODO: Replace this stub with actual Bedrock/Q integration:
    
    1. Import boto3 and configure Bedrock client
    2. Use the system prompt from prompts.get_system_prompt()
    3. Build user prompt with prompts.build_review_prompt(hunk, guidelines)
    4. Call Bedrock with Amazon Q model (e.g., anthropic.claude-3-sonnet-20240229-v1:0)
    5. Parse JSON response and convert to Finding objects
    6. Handle errors and retries appropriately
    
    Example integration:
    ```python
    import boto3
    from botocore.exceptions import ClientError
    
    bedrock = boto3.client('bedrock-runtime')
    
    system_prompt = get_system_prompt()
    user_prompt = build_review_prompt(hunk, guidelines)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "messages": messages,
                "max_tokens": 2048,
                "temperature": 0.1
            })
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Parse JSON response and convert to findings
        findings_data = json.loads(content)
        findings = []
        
        for finding_data in findings_data:
            finding = Finding(
                file=hunk.file_path,
                hunk_header=hunk.hunk_header,
                severity=finding_data['severity'],
                category=finding_data['category'],
                message=finding_data['message'],
                confidence=finding_data['confidence'],
                suggested_patch=finding_data.get('suggested_patch'),
                line_hint=hunk.end_line
            )
            findings.append(finding)
        
        return findings
        
    except ClientError as e:
        logger.error(f"Bedrock API error: {e}")
        raise QClientError(f"Failed to call Bedrock: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Q response: {e}")
        raise QClientError(f"Invalid response from Q: {e}")
    ```
    """
    
    # STUB IMPLEMENTATION - Replace with actual Bedrock/Q call above
    logger.warning("Using stub Q client - no actual review performed")
    
    # Return a dummy finding to demonstrate the interface
    dummy_finding = Finding(
        file=hunk.file_path,
        hunk_header=hunk.hunk_header,
        severity="nit",
        category="docs",
        message="Stub implementation - replace with actual Q integration",
        confidence=0.5,
        suggested_patch=None,
        line_hint=hunk.end_line
    )
    
    return [dummy_finding]


def apply_security_heuristics(findings: List[Finding]) -> List[Finding]:
    """Apply security heuristics to flag potential security issues."""
    security_keywords = [
        'xss', 'sql injection', 'sqli', 'ssrf', 'csrf', 'xxe',
        'insecure', 'vulnerability', 'exploit', 'overflow',
        'injection', 'deserialization', 'path traversal'
    ]
    
    for finding in findings:
        if finding.category == 'security':
            continue
            
        message_lower = finding.message.lower()
        if any(keyword in message_lower for keyword in security_keywords):
            # Upgrade to security category if not already
            if finding.category != 'security':
                finding.category = 'security'
                finding.severity = max(finding.severity, 'major')
                finding.confidence = min(finding.confidence + 0.1, 1.0)
    
    return findings
