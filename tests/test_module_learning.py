#!/usr/bin/env python3
"""
Test script for module-focused learning from large repositories.
"""

import os
import sys
from qrev.cli_learning import ModuleLearningCLI

def test_module_learning():
    """Test the module-focused learning functionality."""
    
    print("🧪 Testing Module-Focused Learning")
    print("=" * 50)
    
    # Check for GitHub token
    if not os.getenv("GITHUB_TOKEN"):
        print("❌ GITHUB_TOKEN environment variable is required")
        print("   Set it with: export GITHUB_TOKEN=your_token_here")
        return False
    
    # Test with a large repository, focusing on specific modules
    test_repo = "https://github.com/microsoft/vscode"
    
    print(f"🎯 Testing repository: {test_repo}")
    print("📚 This repository has thousands of PRs - we'll focus on specific modules")
    
    # Create CLI instance
    cli = ModuleLearningCLI()
    
    # Test learning from specific modules
    success = cli.learn_from_modules(
        repo_url=test_repo,
        modules=["src/vs/workbench", "src/vs/platform"],  # Focus on specific modules
        max_prs_per_module=30,  # Limit per module
        max_total_prs=100,      # Total limit
        output_dir="test_module_results",
        include_comments=True,
        include_reviews=True,
        sample_strategy="representative"
    )
    
    if success:
        print("\n✅ Module learning test completed successfully!")
        print("📁 Check the 'test_module_results' directory for output files")
        return True
    else:
        print("\n❌ Module learning test failed!")
        return False

if __name__ == "__main__":
    success = test_module_learning()
    sys.exit(0 if success else 1)
