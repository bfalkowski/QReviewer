"""QReviewer CLI using Typer."""

import json
import os
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .github_api import fetch_pr_files, GitHubAPIError
from .diff import extract_hunks_from_files
from .llm_client import review_hunk, apply_security_heuristics
from .models import PRDiff, FindingsReport, ReviewStats

app = typer.Typer(help="LLM-powered code review tool")
console = Console()

# Import config functions directly
from .cli_config import show, validate, env, test


@app.command()
def config_show():
    """Show current QReviewer configuration."""
    show()

@app.command()
def config_validate():
    """Validate current configuration."""
    validate()

@app.command()
def config_env():
    """Show environment variables needed for configuration."""
    env()

@app.command()
def config_test():
    """Test the current LLM configuration."""
    test()


@app.command()
def fetch(
    pr: str = typer.Argument(..., help="GitHub PR URL"),
    out: str = typer.Option("pr-diff.json", "--out", "-o", help="Output file path")
):
    """Fetch PR files and unified diff patches."""
    try:
        with console.status(f"Fetching PR files from {pr}..."):
            pr_diff = fetch_pr_files(pr)
        
        # Ensure output directory exists
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write output
        with open(out_path, 'w') as f:
            json.dump(pr_diff.dict(), f, indent=2)
        
        console.print(f"✅ Fetched {len(pr_diff.files)} files from PR #{pr_diff.pr.number}")
        console.print(f"📁 Output written to: {out_path}")
        
    except GitHubAPIError as e:
        console.print(f"❌ GitHub API error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")
        raise typer.Exit(1)


@app.command()
def review(
    inp: str = typer.Option(..., "--inp", "-i", help="Input PR diff file"),
    out: str = typer.Option("findings.json", "--out", "-o", help="Output findings file"),
    guidelines: Optional[str] = typer.Option(None, "--guidelines", "-g", help="Project guidelines file"),
    max_concurrency: int = typer.Option(4, "--max-concurrency", "-c", help="Maximum concurrent reviews")
):
    """Review code hunks and generate findings."""
    try:
        # Load input
        with open(inp, 'r') as f:
            pr_diff_data = json.load(f)
            pr_diff = PRDiff.parse_obj(pr_diff_data)
        
        # Load guidelines if provided
        guidelines_text = None
        if guidelines:
            with open(guidelines, 'r') as f:
                guidelines_text = f.read()
        
        # Extract hunks
        console.print(f"🔍 Extracting hunks from {len(pr_diff.files)} files...")
        hunks = extract_hunks_from_files(pr_diff.files)
        console.print(f"📝 Found {len(hunks)} hunks to review")
        
        if not hunks:
            console.print("⚠️  No hunks found to review")
            return
        
        # Review hunks
        all_findings = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Reviewing hunks...", total=len(hunks))
            
            for hunk in hunks:
                try:
                    findings = review_hunk(hunk, guidelines_text)
                    all_findings.extend(findings)
                except Exception as e:
                    console.print(f"⚠️  Failed to review hunk in {hunk.file_path}: {e}")
                
                progress.advance(task)
        
        # Apply security heuristics
        console.print("🔒 Applying security heuristics...")
        all_findings = apply_security_heuristics(all_findings)
        
        # Create findings report
        findings_report = FindingsReport(
            pr=pr_diff.pr,
            findings=all_findings
        )
        
        # Ensure output directory exists
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write output
        with open(out_path, 'w') as f:
            json.dump(findings_report.dict(), f, indent=2)
        
        console.print(f"✅ Review complete! Found {len(all_findings)} issues")
        console.print(f"📁 Findings written to: {out_path}")
        
    except FileNotFoundError as e:
        console.print(f"❌ File not found: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")
        raise typer.Exit(1)


@app.command()
def summarize(
    inp: str = typer.Option(..., "--inp", "-i", help="Input findings file")
):
    """Summarize findings in a human-readable table."""
    try:
        # Load findings
        with open(inp, 'r') as f:
            findings_data = json.load(f)
            findings_report = FindingsReport.parse_obj(findings_data)
        
        # Calculate stats
        stats = ReviewStats()
        for finding in findings_report.findings:
            if finding.severity == "blocking":
                stats.blocking += 1
            elif finding.severity == "major":
                stats.major += 1
            elif finding.severity == "minor":
                stats.minor += 1
            elif finding.severity == "nit":
                stats.nit += 1
        stats.total = len(findings_report.findings)
        
        # Display summary
        console.print(f"\n📊 Code Review Summary for PR #{findings_report.pr.number}")
        console.print(f"🔗 {findings_report.pr.url}")
        console.print(f"📁 Repository: {findings_report.pr.repo}")
        
        # Stats table
        stats_table = Table(title="Findings Summary")
        stats_table.add_column("Severity", style="bold")
        stats_table.add_column("Count", justify="right")
        stats_table.add_column("Percentage", justify="right")
        
        for severity, count in [
            ("🚫 Blocking", stats.blocking),
            ("⚠️  Major", stats.major),
            ("🔧 Minor", stats.minor),
            ("💡 Nit", stats.nit)
        ]:
            percentage = (count / stats.total * 100) if stats.total > 0 else 0
            stats_table.add_row(severity, str(count), f"{percentage:.1f}%")
        
        console.print(stats_table)
        console.print(f"\n📈 Total Findings: {stats.total}")
        
        # Category breakdown
        if findings_report.findings:
            category_counts = {}
            for finding in findings_report.findings:
                category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
            
            category_table = Table(title="Findings by Category")
            category_table.add_column("Category", style="bold")
            category_table.add_column("Count", justify="right")
            
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                category_table.add_row(category.title(), str(count))
            
            console.print(category_table)
        
        # Top findings
        if findings_report.findings:
            blocking_major = [f for f in findings_report.findings if f.severity in ["blocking", "major"]]
            if blocking_major:
                console.print(f"\n🚨 Top Issues ({len(blocking_major)} blocking/major):")
                for i, finding in enumerate(blocking_major[:5], 1):
                    console.print(f"  {i}. [{finding.severity.upper()}] {finding.message}")
                    console.print(f"     📁 {finding.file} (line ~{finding.line_hint})")
                    console.print()
        
    except FileNotFoundError as e:
        console.print(f"❌ File not found: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")
        raise typer.Exit(1)


@app.command()
def review_only(
    pr_url: str = typer.Option(..., "--pr", "-p", help="GitHub PR URL to review"),
    out: str = typer.Option("review-report.json", "--out", "-o", help="Output report file"),
    guidelines: Optional[str] = typer.Option(None, "--guidelines", "-g", help="Project guidelines file"),
    standards: Optional[str] = typer.Option(None, "--standards", "-s", help="Comma-separated list of standards to apply"),
    max_concurrency: int = typer.Option(4, "--max-concurrency", "-c", help="Maximum concurrent reviews"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, html, or summary")
):
    """Review a GitHub PR and generate a local report without posting to GitHub."""
    try:
        console.print(f"🔍 Fetching PR: {pr_url}")
        
        # Fetch PR diff
        from .github_api import fetch_pr_files
        pr_files = fetch_pr_files(pr_url)
        
        if not pr_files:
            console.print("❌ No files found in PR or failed to fetch")
            raise typer.Exit(1)
        
        # Create PR diff object
        from .diff import extract_hunks_from_files
        pr_diff = PRDiff(
            pr=PRInfo(
                url=pr_url,
                number=int(pr_url.split('/')[-1]),
                repo='/'.join(pr_url.split('/')[-4:-2])
            ),
            files=pr_files
        )
        
        # Load guidelines if provided
        guidelines_text = None
        if guidelines:
            with open(guidelines, 'r') as f:
                guidelines_text = f.read()
        
        # Load standards if provided
        standards_list = None
        if standards:
            standards_list = [s.strip() for s in standards.split(',')]
        
        # Extract hunks
        console.print(f"📝 Extracting hunks from {len(pr_diff.files)} files...")
        hunks = extract_hunks_from_files(pr_diff.files)
        console.print(f"🔍 Found {len(hunks)} hunks to review")
        
        if not hunks:
            console.print("⚠️  No hunks found to review")
            return
        
        # Review hunks
        all_findings = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Reviewing hunks...", total=len(hunks))
            
            for hunk in hunks:
                try:
                    findings = review_hunk(hunk, guidelines_text)
                    all_findings.extend(findings)
                except Exception as e:
                    console.print(f"⚠️  Failed to review hunk in {hunk.file_path}: {e}")
                
                progress.advance(task)
        
        # Apply security heuristics
        console.print("🔒 Applying security heuristics...")
        all_findings = apply_security_heuristics(all_findings)
        
        # Create findings report
        findings_report = FindingsReport(
            pr=pr_diff.pr,
            findings=all_findings
        )
        
        # Ensure output directory exists
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate output based on format
        if format == "html":
            from .report import render_findings_report
            html_content = render_findings_report(findings_report)
            html_file = out_path.with_suffix('.html')
            with open(html_file, 'w') as f:
                f.write(html_content)
            console.print(f"📁 HTML report written to: {html_file}")
            
            # Also save JSON for programmatic use
            with open(out_path, 'w') as f:
                json.dump(findings_report.dict(), f, indent=2)
            console.print(f"📁 JSON findings written to: {out_path}")
            
        elif format == "summary":
            # Generate summary table
            stats = ReviewStats()
            for finding in findings_report.findings:
                if finding.severity == "blocking":
                    stats.blocking += 1
                elif finding.severity == "major":
                    stats.major += 1
                elif finding.severity == "minor":
                    stats.minor += 1
                elif finding.severity == "nit":
                    stats.nit += 1
                stats.total += 1
            
            # Display summary
            console.print("\n📊 Review Summary")
            console.print("=" * 50)
            console.print(f"🔴 Blocking: {stats.blocking}")
            console.print(f"🟠 Major: {stats.major}")
            console.print(f"🟡 Minor: {stats.minor}")
            console.print(f"🟢 Nit: {stats.nit}")
            console.print(f"📊 Total: {stats.total}")
            
            # Save JSON
            with open(out_path, 'w') as f:
                json.dump(findings_report.dict(), f, indent=2)
            console.print(f"\n📁 JSON findings written to: {out_path}")
            
        else:  # json format (default)
            with open(out_path, 'w') as f:
                json.dump(findings_report.dict(), f, indent=2)
            console.print(f"📁 JSON findings written to: {out_path}")
        
        console.print(f"✅ Review complete! Found {len(all_findings)} issues")
        console.print("📋 This was a review-only run - no changes posted to GitHub")
        
        # Show quick summary
        if all_findings:
            console.print("\n🔍 Quick Summary:")
            for finding in all_findings[:3]:  # Show first 3 findings
                severity_emoji = {"blocking": "🔴", "major": "🟠", "minor": "🟡", "nit": "🟢"}.get(finding.severity, "⚪")
                console.print(f"  {severity_emoji} {finding.severity.upper()}: {finding.message}")
            if len(all_findings) > 3:
                console.print(f"  ... and {len(all_findings) - 3} more findings")
        
    except FileNotFoundError as e:
        console.print(f"❌ File not found: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")
        raise typer.Exit(1)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
