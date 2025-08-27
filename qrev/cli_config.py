#!/usr/bin/env python3
"""
Configuration management CLI for QReviewer.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from qrev.config import config

console = Console()
app = typer.Typer(help="QReviewer configuration management")


@app.command()
def show():
    """Show current QReviewer configuration."""
    console.print(Panel.fit(
        "[bold blue]QReviewer Configuration[/bold blue]",
        border_style="blue"
    ))
    
    # LLM Backend Info
    llm_info = config.get_llm_info()
    
    backend_table = Table(title="LLM Backend Configuration")
    backend_table.add_column("Setting", style="cyan")
    backend_table.add_column("Value", style="green")
    
    backend_table.add_row("Backend", llm_info["backend"])
    backend_table.add_row("Status", "✅ Enabled" if llm_info["enabled"] else "❌ Disabled")
    
    if llm_info["backend"] == "amazon_q":
        q_config = llm_info["config"]
        backend_table.add_row("Host", q_config.get("host", "❌ Not set"))
        backend_table.add_row("User", q_config.get("user", "❌ Not set"))
        backend_table.add_row("Port", str(q_config.get("port", 22)))
        backend_table.add_row("Key Path", q_config.get("key_path", "Default SSH key"))
    elif llm_info["backend"] == "bedrock":
        bedrock_config = llm_info["config"]
        backend_table.add_row("Region", bedrock_config.get("region", "❌ Not set"))
        backend_table.add_row("Model", bedrock_config.get("model_id", "❌ Not set"))
        backend_table.add_row("Access Key", "✅ Set" if bedrock_config.get("access_key_id") else "❌ Missing")
        backend_table.add_row("Secret Key", "✅ Set" if bedrock_config.get("secret_access_key") else "❌ Missing")
    elif llm_info["backend"] == "openai":
        openai_config = llm_info["config"]
        backend_table.add_row("Model", openai_config.get("model", "❌ Not set"))
        backend_table.add_row("API Key", "✅ Set" if openai_config.get("api_key") else "❌ Missing")
    
    console.print(backend_table)
    console.print()
    
    # GitHub Configuration
    github_table = Table(title="GitHub Configuration")
    github_table.add_column("Setting", style="cyan")
    github_table.add_column("Value", style="green")
    
    github_table.add_row("Token", "✅ Set" if config.github_token else "❌ Missing")
    console.print(github_table)
    console.print()
    
    # API Configuration
    api_table = Table(title="API Configuration")
    api_table.add_column("Setting", style="cyan")
    api_table.add_column("Value", style="green")
    
    api_table.add_row("API Key", "✅ Set" if config.api_key else "❌ Not required")
    api_table.add_row("Fetch Timeout", f"{config.fetch_timeout_sec}s")
    api_table.add_row("Review Timeout", f"{config.review_timeout_sec}s")
    api_table.add_row("Max Files", str(config.max_files))
    api_table.add_row("Max Patch Size", f"{config.max_patch_bytes:,} bytes")
    
    console.print(api_table)
    console.print()


@app.command()
def validate():
    """Validate current configuration."""
    console.print(Panel.fit(
        "[bold yellow]Validating QReviewer Configuration[/bold yellow]",
        border_style="yellow"
    ))
    
    if config.validate():
        console.print("✅ [green]Configuration is valid![/green]")
        console.print("🚀 QReviewer is ready to use.")
    else:
        console.print("❌ [red]Configuration has errors![/red]")
        console.print("Please fix the issues above before using QReviewer.")


@app.command()
def env():
    """Show environment variables needed for configuration."""
    console.print(Panel.fit(
        "[bold magenta]Environment Variables for QReviewer[/bold magenta]",
        border_style="magenta"
    ))
    
    env_table = Table(title="Required Environment Variables")
    env_table.add_column("Variable", style="cyan")
    env_table.add_column("Description", style="white")
    env_table.add_column("Example", style="green")
    
    env_table.add_row("GITHUB_TOKEN", "GitHub Personal Access Token", "ghp_1234567890...")
    env_table.add_row("QREVIEWER_LLM_BACKEND", "LLM backend to use", "amazon_q")
    
    console.print(env_table)
    console.print()
    
    # Amazon Q CLI specific
    q_table = Table(title="Amazon Q CLI Environment Variables")
    q_table.add_column("Variable", style="cyan")
    q_table.add_column("Description", style="white")
    q_table.add_column("Example", style="green")
    
    q_table.add_row("Q_CLI_HOST", "Hostname/IP of Q machine", "192.168.1.100")
    q_table.add_row("Q_CLI_USER", "SSH username", "bryan")
    q_table.add_row("Q_CLI_PORT", "SSH port (optional)", "22")
    q_table.add_row("Q_CLI_KEY_PATH", "SSH key path (optional)", "~/.ssh/id_rsa")
    
    console.print(q_table)
    console.print()
    
    # Fallback backends
    fallback_table = Table(title="Fallback Backend Environment Variables")
    fallback_table.add_column("Backend", style="cyan")
    fallback_table.add_column("Variables", style="white")
    
    fallback_table.add_row("AWS Bedrock", "AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MODEL_ID")
    fallback_table.add_row("OpenAI", "OPENAI_API_KEY, OPENAI_MODEL")
    
    console.print(fallback_table)
    console.print()
    
    console.print("[bold]Quick Setup:[/bold]")
    console.print("1. Copy config.env.example to .env")
    console.print("2. Fill in your values")
    console.print("3. Run: source .env")
    console.print("4. Run: qrev config validate")


@app.command()
def test():
    """Test the current LLM configuration."""
    console.print(Panel.fit(
        "[bold green]Testing LLM Configuration[/bold green]",
        border_style="green"
    ))
    
    if not config.validate():
        console.print("❌ [red]Configuration is invalid. Please fix errors first.[/red]")
        return
    
    console.print(f"🧪 Testing {config.llm_backend} backend...")
    
    try:
        from qrev.llm_client import get_llm_client
        llm_client = get_llm_client()
        
        # Create a test hunk
        from qrev.models import Hunk
        test_hunk = Hunk(
            file_path="test.py",
            hunk_header="@@ -1,3 +1,6 @@",
            patch_text="def test_function():\n    return 'hello world'\n",
            start_line=1,
            end_line=6,
            language="python"
        )
        
        console.print("📝 Testing with sample code...")
        
        # Test the LLM client
        import asyncio
        findings = asyncio.run(llm_client.review_hunk(test_hunk, "Test guidelines"))
        
        if findings:
            console.print("✅ [green]LLM connection successful![/green]")
            console.print(f"📊 Generated {len(findings)} findings")
            
            # Show first finding
            if findings[0].message != "LLM response parsing failed":
                console.print("🎯 Sample finding:")
                console.print(f"   Severity: {findings[0].severity}")
                console.print(f"   Category: {findings[0].category}")
                console.print(f"   Message: {findings[0].message}")
            else:
                console.print("⚠️  [yellow]LLM responded but parsing failed. Check response format.[/yellow]")
        else:
            console.print("❌ [red]No findings generated. LLM may not be working.[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]LLM test failed: {str(e)}[/red]")
        console.print("Please check your configuration and try again.")


if __name__ == "__main__":
    app()
