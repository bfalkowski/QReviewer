"""Configuration management for QReviewer."""

import os
from typing import Literal, Optional
from pathlib import Path

# LLM backend types
LLMBackend = Literal["amazon_q", "bedrock", "openai"]

class QReviewerConfig:
    """Configuration manager for QReviewer."""
    
    def __init__(self):
        # LLM Configuration
        self.llm_backend: LLMBackend = self._get_llm_backend()
        
        # GitHub Configuration
        self.github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
        
        # API Configuration
        self.api_key: Optional[str] = os.getenv("QREVIEWER_API_KEY")
        
        # Timeouts
        self.fetch_timeout_sec: int = int(os.getenv("FETCH_TIMEOUT_SEC", "30"))
        self.review_timeout_sec: int = int(os.getenv("REVIEW_TIMEOUT_SEC", "120"))
        
        # Limits
        self.max_files: int = int(os.getenv("MAX_FILES", "200"))
        self.max_patch_bytes: int = int(os.getenv("MAX_PATCH_BYTES", "1000000"))
        
        # Amazon Q CLI Configuration
        self.q_cli_host: Optional[str] = os.getenv("Q_CLI_HOST")
        self.q_cli_user: Optional[str] = os.getenv("Q_CLI_USER")
        self.q_cli_key_path: Optional[str] = os.getenv("Q_CLI_KEY_PATH")
        self.q_cli_port: int = int(os.getenv("Q_CLI_PORT", "22"))
        
        # AWS Bedrock Configuration (fallback)
        self.aws_region: str = os.getenv("AWS_REGION", "us-east-1")
        self.aws_access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.bedrock_model_id: str = os.getenv("MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        
        # OpenAI Configuration (fallback)
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
        
        # Now set the LLM config after all attributes are available
        self.llm_config = self._get_llm_config()
    
    def _get_llm_backend(self) -> LLMBackend:
        """Get the configured LLM backend."""
        backend = os.getenv("QREVIEWER_LLM_BACKEND", "amazon_q").lower()
        
        if backend not in ["amazon_q", "bedrock", "openai"]:
            print(f"⚠️  Warning: Invalid LLM backend '{backend}', defaulting to 'amazon_q'")
            return "amazon_q"
        
        return backend
    
    def _get_llm_config(self) -> dict:
        """Get configuration for the selected LLM backend."""
        if self.llm_backend == "amazon_q":
            # Check if we should use local execution or SSH
            if self.q_cli_host and self.q_cli_host not in ["localhost", "127.0.0.1"]:
                # Remote SSH execution
                return {
                    "host": self.q_cli_host,
                    "user": self.q_cli_user,
                    "key_path": self.q_cli_key_path,
                    "port": self.q_cli_port,
                    "local": False,
                    "enabled": bool(self.q_cli_host and self.q_cli_user)
                }
            else:
                # Local execution (default)
                return {
                    "host": "localhost",
                    "user": None,
                    "key_path": None,
                    "port": None,
                    "local": True,
                    "enabled": True  # Always enabled for local execution
                }
        elif self.llm_backend == "bedrock":
            return {
                "region": self.aws_region,
                "access_key_id": self.aws_access_key_id,
                "secret_access_key": self.aws_secret_access_key,
                "model_id": self.bedrock_model_id,
                "enabled": bool(self.aws_access_key_id and self.aws_secret_access_key)
            }
        elif self.llm_backend == "openai":
            return {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "enabled": bool(self.openai_api_key)
            }
        
        return {}
    
    def validate(self) -> bool:
        """Validate the configuration."""
        errors = []
        
        # Check GitHub token
        if not self.github_token:
            errors.append("GITHUB_TOKEN environment variable is required")
        
        # Check LLM backend configuration
        if not self.llm_config.get("enabled", False):
            errors.append(f"LLM backend '{self.llm_backend}' is not properly configured")
        
        # Check specific backend requirements
        if self.llm_backend == "amazon_q":
            # For local execution, no additional requirements
            # For remote execution, check SSH requirements
            if self.q_cli_host and self.q_cli_host not in ["localhost", "127.0.0.1"]:
                if not self.q_cli_host:
                    errors.append("Q_CLI_HOST environment variable is required for remote Amazon Q CLI")
                if not self.q_cli_user:
                    errors.append("Q_CLI_USER environment variable is required for remote Amazon Q CLI")
        elif self.llm_backend == "bedrock":
            if not self.aws_access_key_id:
                errors.append("AWS_ACCESS_KEY_ID environment variable is required for Bedrock")
            if not self.aws_secret_access_key:
                errors.append("AWS_SECRET_ACCESS_KEY environment variable is required for Bedrock")
        elif self.llm_backend == "openai":
            if not self.openai_api_key:
                errors.append("OPENAI_API_KEY environment variable is required for OpenAI")
        
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        return True
    
    def get_llm_info(self) -> dict:
        """Get information about the configured LLM backend."""
        return {
            "backend": self.llm_backend,
            "enabled": self.llm_config.get("enabled", False),
            "config": self.llm_config
        }
    
    def print_config(self):
        """Print the current configuration."""
        print("🔧 QReviewer Configuration")
        print("=" * 40)
        print(f"LLM Backend: {self.llm_backend}")
        print(f"LLM Enabled: {self.llm_config.get('enabled', False)}")
        print(f"GitHub Token: {'✅ Set' if self.github_token else '❌ Missing'}")
        print(f"API Key: {'✅ Set' if self.api_key else '❌ Not required'}")
        print()
        
        if self.llm_backend == "amazon_q":
            print("📱 Amazon Q CLI Configuration:")
            print(f"   Host: {self.q_cli_host or '❌ Not set'}")
            print(f"   User: {self.q_cli_user or '❌ Not set'}")
            print(f"   Port: {self.q_cli_port}")
            print(f"   Key Path: {self.q_cli_key_path or 'Default SSH key'}")
        elif self.llm_backend == "bedrock":
            print("☁️  AWS Bedrock Configuration:")
            print(f"   Region: {self.aws_region}")
            print(f"   Model: {self.bedrock_model_id}")
            print(f"   Access Key: {'✅ Set' if self.aws_access_key_id else '❌ Missing'}")
        elif self.llm_backend == "openai":
            print("🤖 OpenAI Configuration:")
            print(f"   Model: {self.openai_model}")
            print(f"   API Key: {'✅ Set' if self.openai_api_key else '❌ Missing'}")
        
        print()

# Global configuration instance
config = QReviewerConfig()
