#!/usr/bin/env python3
"""
Module-Focused Learning CLI for Large Repositories.

This CLI tool enables one-time training on large repositories by focusing on
specific modules rather than the entire codebase.
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel

from .learning import RepositoryLearner, parse_repository_url
from .standards import StandardsManager

app = typer.Typer(help="Module-focused learning from large repositories")
console = Console()

class ModuleLearningCLI:
    """CLI for module-focused repository learning."""
    
    def __init__(self):
        self.learner = None
        self.standards_manager = StandardsManager()
    
    def learn_from_modules(
        self,
        repo_url: str,
        modules: List[str],
        max_prs_per_module: int = 50,
        max_total_prs: int = 500,
        output_dir: str = "learning_results",
        include_comments: bool = True,
        include_reviews: bool = True,
        sample_strategy: str = "representative"
    ):
        """
        Learn from specific modules in a large repository.
        
        Args:
            repo_url: GitHub repository URL
            modules: List of module paths (e.g., ['src/api', 'lib/core', 'tests'])
            max_prs_per_module: Maximum PRs to analyze per module
            max_total_prs: Maximum total PRs across all modules
            output_dir: Directory to save learning results
            include_comments: Include PR comments in analysis
            include_reviews: Include PR reviews in analysis
            sample_strategy: Sampling strategy ('recent', 'representative', 'high_impact')
        """
        
        # Validate GitHub token
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            console.print("[red]❌ GITHUB_TOKEN environment variable is required[/red]")
            console.print("   Set it with: export GITHUB_TOKEN=your_token_here")
            return False
        
        try:
            # Parse repository URL
            owner, repo = parse_repository_url(repo_url)
            console.print(f"[green]🔍 Repository: {owner}/{repo}[/green]")
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Initialize learner
            self.learner = RepositoryLearner(token)
            
            # Display learning plan
            self._display_learning_plan(
                repo_url, modules, max_prs_per_module, 
                max_total_prs, sample_strategy
            )
            
            # Confirm with user
            if not typer.confirm("Proceed with learning?"):
                console.print("[yellow]Learning cancelled[/yellow]")
                return False
            
            # Start learning process
            results = self._execute_module_learning(
                repo_url, modules, max_prs_per_module, max_total_prs,
                include_comments, include_reviews, sample_strategy, output_path
            )
            
            # Display results
            self._display_learning_results(results, output_path)
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Learning failed: {str(e)}[/red]")
            return False
    
    def _display_learning_plan(
        self, repo_url: str, modules: List[str], 
        max_prs_per_module: int, max_total_prs: int, sample_strategy: str
    ):
        """Display the learning plan for user confirmation."""
        
        table = Table(title="📚 Module Learning Plan")
        table.add_column("Module", style="cyan")
        table.add_column("Max PRs", style="magenta", justify="right")
        table.add_column("Strategy", style="green")
        
        for module in modules:
            table.add_row(module, str(max_prs_per_module), sample_strategy)
        
        console.print(table)
        
        console.print(f"\n[blue]📊 Total estimated PRs: {len(modules) * max_prs_per_module}[/blue]")
        console.print(f"[blue]🎯 Sampling strategy: {sample_strategy}[/blue]")
        console.print(f"[blue]📁 Output directory: learning_results/[/blue]")
        
        if len(modules) * max_prs_per_module > max_total_prs:
            console.print(f"[yellow]⚠️  Note: Will cap total PRs at {max_total_prs}[/yellow]")
    
    def _execute_module_learning(
        self, repo_url: str, modules: List[str], 
        max_prs_per_module: int, max_total_prs: int,
        include_comments: bool, include_reviews: bool, 
        sample_strategy: str, output_path: Path
    ) -> Dict[str, Any]:
        """Execute the module learning process."""
        
        all_results = {}
        total_prs_analyzed = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            for i, module in enumerate(modules):
                # Check if we've hit the total limit
                if total_prs_analyzed >= max_total_prs:
                    console.print(f"[yellow]⚠️  Reached total PR limit ({max_total_prs})[/yellow]")
                    break
                
                # Calculate remaining PRs for this module
                remaining_total = max_total_prs - total_prs_analyzed
                module_prs = min(max_prs_per_module, remaining_total)
                
                task = progress.add_task(
                    f"Learning from {module}...", 
                    total=module_prs
                )
                
                try:
                    # Learn from this specific module
                    module_result = self._learn_from_module(
                        repo_url, module, module_prs, 
                        include_comments, include_reviews, sample_strategy
                    )
                    
                    # Update progress
                    progress.update(task, completed=module_result.get('total_prs', 0))
                    
                    # Store results
                    all_results[module] = module_result
                    total_prs_analyzed += module_result.get('total_prs', 0)
                    
                    # Save module results
                    module_file = output_path / f"module_{module.replace('/', '_')}_results.json"
                    self._save_results(module_result, module_file)
                    
                    console.print(f"[green]✅ {module}: {module_result.get('total_prs', 0)} PRs analyzed[/green]")
                    
                except Exception as e:
                    console.print(f"[red]❌ Failed to learn from {module}: {str(e)}[/red]")
                    progress.update(task, completed=0)
        
        # Create combined results
        combined_results = self._combine_module_results(all_results)
        
        # Save combined results
        combined_file = output_path / "combined_learning_results.json"
        self._save_results(combined_results, combined_file)
        
        return combined_results
    
    def _learn_from_module(
        self, repo_url: str, module: str, max_prs: int,
        include_comments: bool, include_reviews: bool, sample_strategy: str
    ) -> Dict[str, Any]:
        """Learn from a specific module in the repository."""
        
        # Use the existing learning infrastructure but focus on module
        context = self.learner.analyze_repository(
            repo_url=repo_url,
            max_prs=max_prs,
            module_filter=module,  # New parameter to filter by module
            include_comments=include_comments,
            include_reviews=include_reviews,
            sample_strategy=sample_strategy
        )
        
        return {
            "module": module,
            "total_prs": context.total_prs,
            "total_reviews": context.total_reviews,
            "total_comments": context.total_comments,
            "file_patterns": context.file_patterns,
            "module_patterns": context.module_patterns,
            "team_preferences": context.team_preferences,
            "common_issues": context.common_issues,
            "learned_standards": self.learner.generate_learned_standards(context)
        }
    
    def _combine_module_results(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results from multiple modules."""
        
        combined = {
            "modules_analyzed": list(module_results.keys()),
            "total_modules": len(module_results),
            "summary": {
                "total_prs": sum(r.get('total_prs', 0) for r in module_results.values()),
                "total_reviews": sum(r.get('total_reviews', 0) for r in module_results.values()),
                "total_comments": sum(r.get('total_comments', 0) for r in module_results.values())
            },
            "combined_standards": {},
            "combined_issues": [],
            "module_results": module_results
        }
        
        # Combine standards across modules
        for module, results in module_results.items():
            for std_name, standard in results.get('learned_standards', {}).items():
                combined_name = f"{module}_{std_name}"
                combined["combined_standards"][combined_name] = standard
        
        # Combine common issues
        all_issues = []
        for results in module_results.values():
            all_issues.extend(results.get('common_issues', []))
        combined["combined_issues"] = all_issues
        
        return combined
    
    def _save_results(self, results: Dict[str, Any], file_path: Path):
        """Save results to JSON file."""
        import json
        
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    def _display_learning_results(self, results: Dict[str, Any], output_path: Path):
        """Display the learning results."""
        
        console.print("\n" + "="*60)
        console.print("[bold green]🎉 Module Learning Complete![/bold green]")
        console.print("="*60)
        
        # Summary table
        summary_table = Table(title="📊 Learning Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta", justify="right")
        
        summary = results.get('summary', {})
        summary_table.add_row("Modules Analyzed", str(results.get('total_modules', 0)))
        summary_table.add_row("Total PRs", str(summary.get('total_prs', 0)))
        summary_table.add_row("Total Reviews", str(summary.get('total_reviews', 0)))
        summary_table.add_row("Total Comments", str(summary.get('total_comments', 0)))
        
        console.print(summary_table)
        
        # Standards summary
        standards = results.get('combined_standards', {})
        if standards:
            console.print(f"\n[green]🎯 Generated Standards: {len(standards)}[/green]")
            for name, standard in list(standards.items())[:5]:  # Show first 5
                console.print(f"   • {name}: {standard.get('description', 'No description')}")
        
        # Issues summary
        issues = results.get('combined_issues', [])
        if issues:
            console.print(f"\n[red]🚨 Common Issues: {len(issues)}[/red]")
            for issue in issues[:5]:  # Show first 5
                console.print(f"   • {issue.get('category', 'Unknown')}: {issue.get('message', 'No message')}")
        
        # Output files
        console.print(f"\n[blue]📁 Results saved to: {output_path}/[/blue]")
        console.print("   • combined_learning_results.json - All results combined")
        console.print("   • module_*_results.json - Individual module results")
        
        # Next steps
        console.print("\n[bold]🚀 Next Steps:[/bold]")
        console.print("   1. Review the generated standards")
        console.print("   2. Apply learned patterns to your review process")
        console.print("   3. Run learning again when you want to update standards")
        console.print("   4. Share standards with your team")


@app.command()
def learn(
    repo_url: str = typer.Argument(..., help="GitHub repository URL"),
    modules: List[str] = typer.Option(
        ["src", "lib", "tests"], 
        "--module", "-m", 
        help="Module paths to analyze (can specify multiple)"
    ),
    max_prs_per_module: int = typer.Option(
        50, "--max-prs-per-module", "-p",
        help="Maximum PRs to analyze per module"
    ),
    max_total_prs: int = typer.Option(
        500, "--max-total-prs", "-t",
        help="Maximum total PRs across all modules"
    ),
    output_dir: str = typer.Option(
        "learning_results", "--output-dir", "-o",
        help="Directory to save learning results"
    ),
    sample_strategy: str = typer.Option(
        "representative", "--strategy", "-s",
        help="Sampling strategy: recent, representative, high_impact"
    ),
    include_comments: bool = typer.Option(
        True, "--no-comments", help="Exclude PR comments from analysis"
    ),
    include_reviews: bool = typer.Option(
        True, "--no-reviews", help="Exclude PR reviews from analysis"
    )
):
    """
    Learn from specific modules in a large repository.
    
    This is designed for one-time training on large repositories by focusing
    on specific modules rather than the entire codebase.
    
    Example:
        qrev learn https://github.com/owner/repo --module src/api --module lib/core --max-prs-per-module 100
    """
    
    # Invert the boolean flags for CLI
    include_comments = not include_comments
    include_reviews = not include_reviews
    
    cli = ModuleLearningCLI()
    
    success = cli.learn_from_modules(
        repo_url=repo_url,
        modules=modules,
        max_prs_per_module=max_prs_per_module,
        max_total_prs=max_total_prs,
        output_dir=output_dir,
        include_comments=include_comments,
        include_reviews=include_reviews,
        sample_strategy=sample_strategy
    )
    
    if success:
        console.print("\n[bold green]✅ Learning completed successfully![/bold green]")
        sys.exit(0)
    else:
        console.print("\n[bold red]❌ Learning failed![/bold red]")
        sys.exit(1)


@app.command()
def list_strategies():
    """List available sampling strategies."""
    
    strategies = {
        "recent": "Focus on most recent PRs (good for current standards)",
        "representative": "Sample across different time periods (balanced approach)",
        "high_impact": "Focus on PRs with many comments/reviews (high-value learning)"
    }
    
    table = Table(title="🎯 Available Sampling Strategies")
    table.add_column("Strategy", style="cyan")
    table.add_column("Description", style="green")
    
    for strategy, description in strategies.items():
        table.add_row(strategy, description)
    
    console.print(table)


if __name__ == "__main__":
    app()
