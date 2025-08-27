"""Multi-backend LLM client for QReviewer."""

import json
import logging
import subprocess
import asyncio
from typing import List, Optional, Dict, Any
from .models import Hunk, Finding
from .prompts import get_system_prompt, build_review_prompt
from .config import config

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """LLM client error."""
    pass


class BaseLLMClient:
    """Base class for LLM clients."""
    
    def __init__(self):
        self.config = config
    
    async def review_hunk(self, hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
        """Review a code hunk using the configured LLM backend."""
        raise NotImplementedError("Subclasses must implement review_hunk")
    
    def _parse_findings_response(self, response_text: str) -> List[Finding]:
        """Parse LLM response into Finding objects."""
        try:
            # Try to parse as JSON first
            findings_data = json.loads(response_text)
            
            # Handle different response formats
            if isinstance(findings_data, list):
                findings_list = findings_data
            elif isinstance(findings_data, dict) and "findings" in findings_data:
                findings_list = findings_data["findings"]
            else:
                logger.warning(f"Unexpected response format: {type(findings_data)}")
                return self._create_dummy_finding(hunk, "Unexpected response format")
            
            findings = []
            for finding_data in findings_list:
                if isinstance(finding_data, dict):
                    finding = Finding(
                        file=hunk.file_path,
                        hunk_header=hunk.hunk_header,
                        severity=finding_data.get("severity", "info"),
                        category=finding_data.get("category", "general"),
                        message=finding_data.get("message", "No message provided"),
                        confidence=finding_data.get("confidence", 0.5),
                        suggested_patch=finding_data.get("suggested_patch"),
                        line_hint=hunk.end_line
                    )
                    findings.append(finding)
            
            return findings if findings else self._create_dummy_finding(hunk, "No findings generated")
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return self._create_dummy_finding(hunk, f"Failed to parse response: {e}")
        except Exception as e:
            logger.error(f"Error parsing findings: {e}")
            return self._create_dummy_finding(hunk, f"Error parsing findings: {e}")
    
    def _create_dummy_finding(self, hunk: Hunk, message: str) -> List[Finding]:
        """Create a dummy finding when parsing fails."""
        return [Finding(
            file=hunk.file_path,
            hunk_header=hunk.hunk_header,
            severity="info",
            category="system",
            message=f"LLM response parsing failed: {message}",
            confidence=0.1,
            suggested_patch=None,
            line_hint=hunk.end_line
        )]


class AmazonQCLIClient(BaseLLMClient):
    """Amazon Q CLI client using SSH to remote machine."""
    
    def __init__(self):
        super().__init__()
        self.q_config = self.config.llm_config
    
    async def review_hunk(self, hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
        """Review a code hunk using Amazon Q CLI via SSH."""
        try:
            # Build the prompt
            system_prompt = get_system_prompt()
            user_prompt = build_review_prompt(hunk, guidelines)
            
            # Create the Q CLI command
            q_command = self._build_q_command(system_prompt, user_prompt)
            
            # Execute via SSH
            response = await self._execute_ssh_command(q_command)
            
            # Parse the response
            return self._parse_findings_response(response)
            
        except Exception as e:
            logger.error(f"Amazon Q CLI error: {e}")
            return self._create_dummy_finding(hunk, f"Amazon Q CLI error: {e}")
    
    def _build_q_command(self, system_prompt: str, user_prompt: str) -> str:
        """Build the Q CLI command for code review."""
        # Combine prompts and create a focused code review prompt
        combined_prompt = f"""
{system_prompt}

Please review the following code changes and provide feedback in JSON format.

{user_prompt}

Respond with a JSON array of findings, each with:
- severity: "nit", "minor", "major", "critical"
- category: "security", "performance", "style", "docs", "logic", "general"
- message: Clear description of the issue
- confidence: 0.0 to 1.0
- suggested_patch: Optional code suggestion
"""
        
        # Escape the prompt for shell execution
        escaped_prompt = combined_prompt.replace('"', '\\"').replace("'", "\\'")
        
        # Build the Q CLI command
        return f'q chat --prompt "{escaped_prompt}"'
    
    async def _execute_ssh_command(self, command: str) -> str:
        """Execute a command on the remote Q machine via SSH."""
        ssh_config = self.q_config
        
        # Build SSH command
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=30",
            "-p", str(ssh_config["port"]),
        ]
        
        # Add SSH key if specified
        if ssh_config.get("key_path"):
            ssh_cmd.extend(["-i", ssh_config["key_path"]])
        
        # Add user@host
        ssh_cmd.append(f"{ssh_config['user']}@{ssh_config['host']}")
        
        # Add the Q command
        ssh_cmd.append(command)
        
        logger.debug(f"Executing SSH command: {' '.join(ssh_cmd)}")
        
        try:
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.review_timeout_sec
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown SSH error"
                raise LLMClientError(f"SSH command failed: {error_msg}")
            
            response = stdout.decode().strip()
            if not response:
                raise LLMClientError("Empty response from Q CLI")
            
            return response
            
        except asyncio.TimeoutError:
            raise LLMClientError(f"SSH command timed out after {self.config.review_timeout_sec} seconds")
        except Exception as e:
            raise LLMClientError(f"SSH execution error: {e}")


class BedrockClient(BaseLLMClient):
    """AWS Bedrock client for fallback LLM access."""
    
    def __init__(self):
        super().__init__()
        self.bedrock_config = self.config.llm_config
    
    async def review_hunk(self, hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
        """Review a code hunk using AWS Bedrock."""
        try:
            # Import boto3 here to avoid dependency issues
            import boto3
            from botocore.exceptions import ClientError
            
            # Create Bedrock client
            bedrock = boto3.client(
                'bedrock-runtime',
                region_name=self.bedrock_config["region"],
                aws_access_key_id=self.bedrock_config["access_key_id"],
                aws_secret_access_key=self.bedrock_config["secret_access_key"]
            )
            
            # Build the prompt
            system_prompt = get_system_prompt()
            user_prompt = build_review_prompt(hunk, guidelines)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Call Bedrock
            response = bedrock.invoke_model(
                modelId=self.bedrock_config["model_id"],
                body=json.dumps({
                    "messages": messages,
                    "max_tokens": 2048,
                    "temperature": 0.1
                })
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            return self._parse_findings_response(content)
            
        except ImportError:
            logger.error("boto3 not installed for Bedrock support")
            return self._create_dummy_finding(hunk, "boto3 not installed for Bedrock support")
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            return self._create_dummy_finding(hunk, f"Bedrock API error: {e}")
        except Exception as e:
            logger.error(f"Bedrock error: {e}")
            return self._create_dummy_finding(hunk, f"Bedrock error: {e}")


class OpenAIClient(BaseLLMClient):
    """OpenAI client for fallback LLM access."""
    
    def __init__(self):
        super().__init__()
        self.openai_config = self.config.llm_config
    
    async def review_hunk(self, hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
        """Review a code hunk using OpenAI."""
        try:
            # Import openai here to avoid dependency issues
            import openai
            
            # Configure OpenAI
            openai.api_key = self.openai_config["api_key"]
            
            # Build the prompt
            system_prompt = get_system_prompt()
            user_prompt = build_review_prompt(hunk, guidelines)
            
            # Call OpenAI
            response = await openai.ChatCompletion.acreate(
                model=self.openai_config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2048,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return self._parse_findings_response(content)
            
        except ImportError:
            logger.error("openai not installed for OpenAI support")
            return self._create_dummy_finding(hunk, "openai not installed for OpenAI support")
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return self._create_dummy_finding(hunk, f"OpenAI error: {e}")


def get_llm_client() -> BaseLLMClient:
    """Get the configured LLM client."""
    backend = config.llm_backend
    
    if backend == "amazon_q":
        return AmazonQCLIClient()
    elif backend == "bedrock":
        return BedrockClient()
    elif backend == "openai":
        return OpenAIClient()
    else:
        raise ValueError(f"Unsupported LLM backend: {backend}")


# Backward compatibility
def review_hunk(hunk: Hunk, guidelines: Optional[str] = None) -> List[Finding]:
    """Backward compatibility function for existing code."""
    client = get_llm_client()
    
    # Run in event loop if not already running
    try:
        loop = asyncio.get_running_loop()
        # If we're already in an event loop, we need to handle this differently
        # For now, just return a dummy finding
        logger.warning("Cannot run async review_hunk in existing event loop")
        return client._create_dummy_finding(hunk, "Async execution not supported in this context")
    except RuntimeError:
        # No event loop running, we can create one
        return asyncio.run(client.review_hunk(hunk, guidelines))


def apply_security_heuristics(findings: List[Finding]) -> List[Finding]:
    """Apply security heuristics to flag potential security issues."""
    security_keywords = [
        "password", "secret", "key", "token", "auth", "login", "admin",
        "sql", "injection", "xss", "csrf", "eval", "exec", "shell",
        "file", "upload", "download", "path", "traversal", "overflow"
    ]
    
    enhanced_findings = findings.copy()
    
    for finding in enhanced_findings:
        # Check if finding contains security-related keywords
        content_lower = finding.message.lower()
        if any(keyword in content_lower for keyword in security_keywords):
            # If it's not already marked as security, consider upgrading severity
            if finding.category != "security":
                finding.category = "security"
                # Upgrade severity if it's currently low
                if finding.severity in ["nit", "minor"]:
                    finding.severity = "major"
                    finding.confidence = min(finding.confidence + 0.2, 1.0)
    
    return enhanced_findings
