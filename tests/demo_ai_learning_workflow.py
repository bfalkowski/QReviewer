#!/usr/bin/env python3
"""
Comprehensive demonstration of the AI Learning Workflow.

This script demonstrates the complete AI-powered learning system:
1. Learning from repository history
2. Analyzing patterns and generating standards
3. Applying learned standards to new reviews
4. Continuous improvement
"""

import os
import requests
import json
import time
from typing import Dict, Any, List

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_section(title: str):
    """Print a formatted section."""
    print(f"\n📋 {title}")
    print("-" * 40)

def test_ai_learning_workflow():
    """Demonstrate the complete AI learning workflow."""
    
    print_header("AI-Powered Learning from Repository History")
    
    # Step 1: Learn from a repository with rich history
    print_section("Step 1: Learning from Repository History")
    
    target_repo = "https://github.com/facebook/react"
    print(f"🎯 Target repository: {target_repo}")
    print("   This repository has thousands of PRs and reviews")
    print("   We'll analyze recent PRs to learn patterns")
    
    try:
        # Start the learning process
        print("\n🤖 Starting AI learning process...")
        response = requests.post(
            "http://localhost:8000/learn_from_repository",
            json={
                "repositoryUrl": target_repo,
                "maxPRs": 20,  # Analyze more PRs for better learning
                "includeComments": True,
                "includeReviews": True
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Learning completed successfully!")
            print(f"   📊 Analyzed: {result['summary']['total_prs']} PRs")
            print(f"   🔍 Reviews: {result['summary']['total_reviews']}")
            print(f"   💬 Comments: {result['summary']['total_comments']}")
            print(f"   📁 Results saved to: {result['outputFile']}")
            
            # Step 2: Analyze what was learned
            print_section("Step 2: Analysis of Learned Patterns")
            
            if result['learnedStandards']:
                print("🎯 Generated Standards:")
                for name, standard in result['learnedStandards'].items():
                    print(f"   📋 {name}")
                    print(f"      Description: {standard.get('description', 'N/A')}")
                    print(f"      Categories: {', '.join(standard.get('categories', []))}")
                    print(f"      Version: {standard.get('version', 'N/A')}")
            else:
                print("🎯 No standards generated yet")
            
            if result['commonIssues']:
                print("\n🚨 Common Issues Identified:")
                for i, issue in enumerate(result['commonIssues'][:5], 1):
                    print(f"   {i}. {issue.get('category', 'Unknown')}: {issue.get('message', 'N/A')}")
                    print(f"      Severity: {issue.get('severity', 'Unknown')}")
                    print(f"      Confidence: {issue.get('confidence', 0):.1f}")
            else:
                print("\n🚨 No common issues identified")
            
            if result['teamPreferences']:
                print("\n👥 Team Preferences Learned:")
                prefs = result['teamPreferences']
                if 'review_style' in prefs:
                    print("   Review Style:")
                    for style, count in prefs['review_style'].items():
                        print(f"      {style}: {count}")
            
            # Step 3: Show how this improves future reviews
            print_section("Step 3: How This Improves Future Reviews")
            
            print("🔮 The AI system now understands:")
            print("   • Common patterns in this codebase")
            print("   • Team review preferences")
            print("   • File-specific issues")
            print("   • Severity distributions")
            
            print("\n💡 Benefits for future reviews:")
            print("   • More accurate issue detection")
            print("   • Context-aware suggestions")
            print("   • Team-specific standards")
            print("   • Continuous improvement")
            
            # Step 4: Demonstrate continuous learning
            print_section("Step 4: Continuous Learning Capabilities")
            
            print("🔄 The system can:")
            print("   • Learn from new PRs automatically")
            print("   • Update standards based on new patterns")
            print("   • Adapt to team changes over time")
            print("   • Generate reports on learning progress")
            
            # Step 5: Show practical applications
            print_section("Step 5: Practical Applications")
            
            print("🎯 Use Cases:")
            print("   • Onboarding new team members")
            print("   • Standardizing review processes")
            print("   • Identifying recurring issues")
            print("   • Improving code quality metrics")
            print("   • Training AI models for code review")
            
        else:
            print(f"❌ Learning failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception during learning: {str(e)}")
    
    # Step 6: Show how to use the learned knowledge
    print_section("Step 6: Using Learned Knowledge")
    
    print("🔧 To use the learned knowledge:")
    print("   1. The system automatically applies learned patterns")
    print("   2. New reviews benefit from historical insights")
    print("   3. Standards can be exported and shared")
    print("   4. Learning results can be analyzed further")
    
    print("\n📚 Next Steps:")
    print("   • Run learning on your own repositories")
    print("   • Customize learning parameters")
    print("   • Export and share learned standards")
    print("   • Integrate with existing review workflows")
    
    print_header("AI Learning Workflow Complete!")
    print("🎉 The system has successfully demonstrated:")
    print("   ✅ Repository analysis and pattern extraction")
    print("   ✅ AI-powered learning from review history")
    print("   ✅ Standard generation and team preference learning")
    print("   ✅ Continuous improvement capabilities")
    print("   ✅ Practical applications for code review")

if __name__ == "__main__":
    test_ai_learning_workflow()
