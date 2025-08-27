#!/usr/bin/env python3
"""
Script to demonstrate training on multiple repositories using the organized structure.

This script shows how to train on different repositories and organize the results
in the learning_results/ directory structure.
"""

import os
import sys
from pathlib import Path
from qrev.cli_learning import ModuleLearningCLI

def train_multiple_repositories():
    """Train on multiple repositories to demonstrate the organized structure."""
    
    # Check for GitHub token
    if not os.getenv("GITHUB_TOKEN"):
        print("❌ GITHUB_TOKEN environment variable is required")
        print("   Set it with: export GITHUB_TOKEN=your_token_here")
        return False
    
    # Define repositories to train on
    repositories = [
        {
            "name": "qreviewer",
            "url": "https://github.com/bryanfalkowski/QReviewer",
            "modules": ["qrev", "tests"],
            "max_prs_per_module": 20,
            "strategy": "representative"
        },
        {
            "name": "react_example",
            "url": "https://github.com/facebook/react",
            "modules": ["src", "packages"],
            "max_prs_per_module": 30,
            "strategy": "high_impact"
        },
        {
            "name": "vscode_example",
            "url": "https://github.com/microsoft/vscode",
            "modules": ["src/vs/workbench", "src/vs/platform"],
            "max_prs_per_module": 25,
            "strategy": "recent"
        }
    ]
    
    print("🚀 Training on Multiple Repositories")
    print("=" * 50)
    print("This will demonstrate the organized learning_results/ structure")
    print()
    
    cli = ModuleLearningCLI()
    
    for repo_config in repositories:
        repo_name = repo_config["name"]
        repo_url = repo_config["url"]
        modules = repo_config["modules"]
        max_prs = repo_config["max_prs_per_module"]
        strategy = repo_config["strategy"]
        
        print(f"📚 Training on: {repo_name}")
        print(f"   URL: {repo_url}")
        print(f"   Modules: {', '.join(modules)}")
        print(f"   Strategy: {strategy}")
        print(f"   Max PRs per module: {max_prs}")
        print()
        
        # Set output directory to organized structure
        output_dir = f"learning_results/{repo_name}"
        
        try:
            success = cli.learn_from_modules(
                repo_url=repo_url,
                modules=modules,
                max_prs_per_module=max_prs,
                max_total_prs=max_prs * len(modules),
                output_dir=output_dir,
                include_comments=True,
                include_reviews=True,
                sample_strategy=strategy
            )
            
            if success:
                print(f"✅ Successfully trained on {repo_name}")
                print(f"   Results saved to: {output_dir}/")
            else:
                print(f"❌ Failed to train on {repo_name}")
                
        except Exception as e:
            print(f"❌ Exception while training on {repo_name}: {str(e)}")
        
        print("-" * 50)
        print()
    
    # Show final organized structure
    print("🎉 Training Complete!")
    print("📁 Final organized structure:")
    
    learning_dir = Path("learning_results")
    if learning_dir.exists():
        for item in learning_dir.iterdir():
            if item.is_dir():
                print(f"   📂 {item.name}/")
                if (item / "combined_learning_results.json").exists():
                    print(f"      📄 combined_learning_results.json")
                for module_file in item.glob("module_*_results.json"):
                    print(f"      📄 {module_file.name}")
    
    print()
    print("💡 You can now:")
    print("   1. Compare results between repositories")
    print("   2. Retrain individual repositories")
    print("   3. Add new repositories to the structure")
    print("   4. Use the organized results for analysis")
    
    return True

if __name__ == "__main__":
    success = train_multiple_repositories()
    sys.exit(0 if success else 1)
