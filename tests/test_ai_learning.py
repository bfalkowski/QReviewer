#!/usr/bin/env python3
"""
Test script to demonstrate QReviewer's new AI-powered repository learning functionality.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_learn_from_repository():
    """Test learning from repository review history."""
    print("🤖 Testing AI-powered repository learning...")
    
    payload = {
        "repositoryUrl": "https://github.com/bfalkowski/QReviewer",
        "maxPRs": 50,  # Analyze up to 50 PRs
        "includeComments": True,
        "includeReviews": True,
        "outputFile": "qreviewer_learning_results.json"
    }
    
    print(f"📚 Learning from repository: {payload['repositoryUrl']}")
    print(f"   - Max PRs to analyze: {payload['maxPRs']}")
    print(f"   - Include comments: {payload['includeComments']}")
    print(f"   - Include reviews: {payload['includeReviews']}")
    print(f"   - Output file: {payload['outputFile']}")
    print()
    
    print("🚀 Starting AI learning process...")
    print("   This will analyze all PRs, reviews, and comments in your repository!")
    print("   It's a one-time task that will give QReviewer 'experience' from your team's review history.")
    print()
    
    response = requests.post(f"{BASE_URL}/learn_from_repository", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ AI learning completed successfully!")
        print(f"   - Repository: {result['repository']}")
        print(f"   - Total PRs analyzed: {result['summary']['total_prs']}")
        print(f"   - Total reviews found: {result['summary']['total_reviews']}")
        print(f"   - Total comments analyzed: {result['summary']['total_comments']}")
        print(f"   - Output file: {result['outputFile']}")
        print(f"   - Message: {result['message']}")
        
        print("\n🧠 What the AI learned:")
        print(f"   - Learned standards: {len(result['learnedStandards'])}")
        for std_name, std_data in result['learnedStandards'].items():
            print(f"     • {std_name}: {len(std_data['rules'])} rules")
        
        print(f"   - Common issues identified: {len(result['commonIssues'])}")
        print(f"   - Team preferences learned: {len(result['teamPreferences'])} categories")
        
        return result['outputFile']
        
    else:
        print(f"❌ AI learning failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_apply_learned_standards(learning_results_file):
    """Test applying the learned standards to the system."""
    if not learning_results_file:
        print("❌ No learning results file to apply")
        return
    
    print("\n🔧 Testing learned standards application...")
    
    payload = {
        "learningResultsFile": learning_results_file,
        "overwrite": False  # Don't overwrite existing standards
    }
    
    print(f"📋 Applying learned standards from: {learning_results_file}")
    print("   This will create new standards based on your repository's review patterns!")
    
    response = requests.post(f"{BASE_URL}/apply_learned_standards", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Learned standards applied successfully!")
        print(f"   - Standards applied: {len(result['standardsApplied'])}")
        print(f"   - New standards created: {result['standardsCreated']}")
        print(f"   - Existing standards updated: {result['standardsUpdated']}")
        print(f"   - Message: {result['message']}")
        
        if result['standardsApplied']:
            print("\n📚 New standards available:")
            for std_name in result['standardsApplied']:
                print(f"   • {std_name}")
        
    else:
        print(f"❌ Failed to apply learned standards: {response.status_code}")
        print(f"   Error: {response.text}")

def test_enhanced_review_with_learned_standards():
    """Test enhanced review using the newly learned standards."""
    print("\n🧪 Testing enhanced review with learned standards...")
    
    # First, get available standards to see our new learned ones
    response = requests.post(f"{BASE_URL}/get_standards", json={})
    
    if response.status_code == 200:
        result = response.json()
        learned_standards = [name for name in result['availableStandards'] if name.startswith('learned_')]
        
        if learned_standards:
            print(f"🎯 Found {len(learned_standards)} learned standards: {', '.join(learned_standards)}")
            
            # Test enhanced review with learned standards
            payload = {
                "prUrl": "https://github.com/bfalkowski/QReviewer/pull/1",
                "standards": learned_standards[:2],  # Use first 2 learned standards
                "mode": "learning",
                "requestId": "learned-standards-test"
            }
            
            print(f"📤 Running enhanced review with learned standards: {payload['standards']}")
            print("   - Mode: learning (will provide insights based on repository history)")
            
            response = requests.post(f"{BASE_URL}/enhanced_review", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Enhanced review with learned standards completed!")
                print(f"   - Score: {result['score']:.2f}")
                print(f"   - Findings: {len(result['findings'])}")
                print(f"   - Standards applied: {', '.join(result['standardsApplied'])}")
                
                print("\n📊 Compliance Status:")
                for std, status in result['complianceStatus'].items():
                    emoji = {"PASSED": "🟢", "WARNING": "🟡", "FAILED": "🔴"}.get(status, "⚪")
                    print(f"   {emoji} {std}: {status}")
                
                print("\n💡 AI-Generated Recommendations:")
                for rec in result['recommendations']:
                    print(f"   - {rec}")
                
                print(f"\n⏱️ Performance:")
                for step, duration in result['stepDurations'].items():
                    print(f"   - {step}: {duration}ms")
                
            else:
                print(f"❌ Enhanced review failed: {response.status_code}")
                print(f"   Error: {response.text}")
        else:
            print("❌ No learned standards found")
    else:
        print(f"❌ Failed to get standards: {response.status_code}")

def show_learning_results_summary(learning_results_file):
    """Show a summary of what was learned."""
    if not learning_results_file:
        return
    
    try:
        with open(learning_results_file, 'r') as f:
            results = json.load(f)
        
        print("\n📊 Learning Results Summary")
        print("=" * 50)
        print(f"Repository: {results['repository']}")
        print(f"Total PRs analyzed: {results['summary']['total_prs']}")
        print(f"Total reviews: {results['summary']['total_reviews']}")
        print(f"Total comments: {results['summary']['total_comments']}")
        
        print(f"\n🧠 Learned Standards: {len(results['learned_standards'])}")
        for std_name, std_data in results['learned_standards'].items():
            print(f"  • {std_name}: {len(std_data['rules'])} rules")
            print(f"    Categories: {', '.join(std_data['categories'])}")
        
        print(f"\n🔍 Common Issues: {len(results['common_issues'])}")
        for i, issue in enumerate(results['common_issues'][:5], 1):  # Show top 5
            print(f"  {i}. {issue['category']}: {issue['message']}")
            print(f"     Frequency: {issue['frequency']}, Confidence: {issue['confidence']:.2f}")
        
        print(f"\n👥 Team Preferences:")
        for category, count in results['team_preferences'].get('common_categories', {}).items():
            print(f"  • {category}: {count} mentions")
        
        print(f"\n💾 Results saved to: {learning_results_file}")
        
    except Exception as e:
        print(f"❌ Error reading learning results: {e}")

def main():
    """Run all AI learning tests."""
    print("🤖 QReviewer AI-Powered Repository Learning Test")
    print("=" * 70)
    print()
    print("🎯 This test will demonstrate how QReviewer can learn from your repository's review history!")
    print("   It's like giving your tool 'experience' and 'institutional knowledge'.")
    print()
    
    # Step 1: Learn from repository
    learning_results_file = test_learn_from_repository()
    
    if learning_results_file:
        # Step 2: Show what was learned
        show_learning_results_summary(learning_results_file)
        
        # Step 3: Apply learned standards
        test_apply_learned_standards(learning_results_file)
        
        # Step 4: Test enhanced review with learned standards
        test_enhanced_review_with_learned_standards()
        
        print("\n🎉 AI Learning Test Completed!")
        print()
        print("🚀 What you now have:")
        print("1. **Repository Intelligence**: QReviewer learned from your team's review history")
        print("2. **Custom Standards**: Standards based on your actual codebase patterns")
        print("3. **Team Preferences**: Understanding of what your team cares about")
        print("4. **File-Specific Insights**: Knowledge of common issues in specific file types")
        print("5. **Context Awareness**: Better understanding of your project structure")
        print()
        print("🌟 Your QReviewer is now 'experienced' and knows your team's review patterns!")
        print("   It's like having a senior developer who's been on your team for years!")
        
    else:
        print("\n❌ AI Learning test failed - check the errors above")

if __name__ == "__main__":
    main()
