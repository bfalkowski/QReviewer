#!/usr/bin/env python3
"""
Test AI learning from a real repository with more PRs.
"""

import os
import requests
import json
from typing import Dict, Any

def test_ai_learning_real_repo():
    """Test AI learning from a real repository with more PRs."""
    
    # Test with a popular open source repository that likely has many PRs
    test_repos = [
        "https://github.com/microsoft/vscode",  # VS Code - many PRs
        "https://github.com/facebook/react",    # React - many PRs
        "https://github.com/tensorflow/tensorflow",  # TensorFlow - many PRs
    ]
    
    print("🤖 Testing AI Learning from Real Repositories")
    print("=" * 50)
    
    for repo_url in test_repos:
        print(f"\n📚 Testing repository: {repo_url}")
        
        try:
            # Test the AI learning endpoint
            response = requests.post(
                "http://localhost:8000/learn_from_repository",
                json={
                    "repositoryUrl": repo_url,
                    "maxPRs": 10,  # Limit to 10 PRs for testing
                    "includeComments": True,
                    "includeReviews": True
                },
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Repository: {result['repository']}")
                print(f"   📊 Summary: {result['summary']}")
                print(f"   📁 Output file: {result['outputFile']}")
                print(f"   💡 Message: {result['message']}")
                
                # Show some learned standards if any
                if result['learnedStandards']:
                    print(f"   🎯 Learned standards: {len(result['learnedStandards'])} found")
                    for name, standard in list(result['learnedStandards'].items())[:3]:
                        print(f"      - {name}: {standard.get('description', 'No description')}")
                else:
                    print("   🎯 No standards learned yet (repository may be too new)")
                
                # Show common issues if any
                if result['commonIssues']:
                    print(f"   🚨 Common issues: {len(result['commonIssues'])} found")
                    for issue in result['commonIssues'][:3]:
                        print(f"      - {issue.get('type', 'Unknown')}: {issue.get('message', 'No message')}")
                else:
                    print("   🚨 No common issues identified")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout for {repo_url} (this is expected for large repositories)")
        except Exception as e:
            print(f"❌ Exception for {repo_url}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Learning Test Complete!")
    print("\n💡 Note: Large repositories may timeout or take a long time to analyze.")
    print("   This is expected behavior for repositories with many PRs.")

if __name__ == "__main__":
    test_ai_learning_real_repo()
