#!/usr/bin/env python3
"""
Test script to demonstrate QReviewer's new standards and context functionality.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_get_standards():
    """Test getting available review standards."""
    print("📋 Testing standards retrieval...")
    
    # Get all standards
    response = requests.post(f"{BASE_URL}/get_standards", json={})
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Standards retrieved successfully!")
        print(f"   - Available standards: {', '.join(result['availableStandards'])}")
        
        for name, std in result['standards'].items():
            print(f"   - {name}: {std['description']}")
            print(f"     Rules: {len(std['rules'])}")
            print(f"     Categories: {', '.join(std['categories'])}")
    else:
        print(f"❌ Failed to get standards: {response.status_code}")
        print(f"   Error: {response.text}")
    
    print()

def test_get_context():
    """Test getting project context."""
    print("🏗️ Testing project context retrieval...")
    
    payload = {
        "projectPath": ".",
        "standards": ["security", "python_style"]
    }
    
    response = requests.post(f"{BASE_URL}/get_context", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Project context retrieved successfully!")
        print(f"   - Project: {result['projectContext']['project_name']}")
        print(f"   - Description: {result['projectContext']['project_description'][:100]}...")
        print(f"   - Dependencies: {len(result['projectContext']['dependencies'])}")
        print(f"   - Standards applied: {list(result['standards'].keys())}")
    else:
        print(f"❌ Failed to get context: {response.status_code}")
        print(f"   Error: {response.text}")
    
    print()

def test_enhanced_review():
    """Test the new enhanced review with standards."""
    print("🚀 Testing enhanced review with standards...")
    
    payload = {
        "prUrl": "https://github.com/bfalkowski/QReviewer/pull/1",
        "standards": ["security", "python_style", "performance"],
        "mode": "strict",
        "requestId": "enhanced-review-demo"
    }
    
    print(f"📤 Running enhanced review with standards: {payload['standards']}")
    print("   - Mode: strict (will identify compliance issues)")
    
    response = requests.post(f"{BASE_URL}/enhanced_review", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Enhanced review completed successfully!")
        print(f"   - Score: {result['score']:.2f}")
        print(f"   - Findings: {len(result['findings'])}")
        print(f"   - Standards applied: {', '.join(result['standardsApplied'])}")
        
        print("\n📊 Compliance Status:")
        for std, status in result['complianceStatus'].items():
            emoji = {"PASSED": "🟢", "WARNING": "🟡", "FAILED": "🔴"}.get(status, "⚪")
            print(f"   {emoji} {std}: {status}")
        
        print("\n💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"   - {rec}")
        
        print(f"\n⏱️ Performance:")
        for step, duration in result['stepDurations'].items():
            print(f"   - {step}: {duration}ms")
        
    else:
        print(f"❌ Enhanced review failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    print()

def test_create_custom_standard():
    """Test creating a custom review standard."""
    print("🔧 Testing custom standard creation...")
    
    custom_standard = {
        "name": "team_specific",
        "description": "Team-specific coding standards for QReviewer project",
        "version": "1.0.0",
        "rules": [
            {
                "id": "TEAM001",
                "category": "documentation",
                "pattern": r"def [^(]+\([^)]*\):\s*$",
                "message": "Function missing docstring",
                "severity": "minor",
                "suggestion": "Add docstring: \"\"\"Function description.\"\"\""
            },
            {
                "id": "TEAM002",
                "category": "testing",
                "pattern": r"def test_",
                "message": "Test function should have descriptive name",
                "severity": "minor",
                "suggestion": "Use descriptive test names: test_function_behavior()"
            }
        ],
        "severityWeights": {"critical": 3.0, "major": 2.0, "minor": 1.0},
        "categories": ["documentation", "testing", "team_preferences"],
        "metadata": {"team": "QReviewer", "framework": "custom"}
    }
    
    response = requests.post(f"{BASE_URL}/create_standard", json=custom_standard)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Custom standard created successfully!")
            print(f"   - Name: {result['standardName']}")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Failed to create standard: {result['message']}")
    else:
        print(f"❌ Failed to create standard: {response.status_code}")
        print(f"   Error: {response.text}")
    
    print()

def test_standards_integration():
    """Test how standards integrate with the review process."""
    print("🔗 Testing standards integration...")
    
    # First, get our custom standard
    response = requests.post(f"{BASE_URL}/get_standards", json={"names": ["team_specific"]})
    
    if response.status_code == 200:
        result = response.json()
        if "team_specific" in result['standards']:
            print("✅ Custom standard loaded successfully!")
            std = result['standards']['team_specific']
            print(f"   - Rules: {len(std['rules'])}")
            print(f"   - Categories: {', '.join(std['categories'])}")
            
            # Now test enhanced review with our custom standard
            print("\n🧪 Testing enhanced review with custom standard...")
            
            payload = {
                "prUrl": "https://github.com/bfalkowski/QReviewer/pull/1",
                "standards": ["team_specific"],
                "mode": "learning",
                "requestId": "custom-standard-test"
            }
            
            response = requests.post(f"{BASE_URL}/enhanced_review", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Enhanced review with custom standard completed!")
                print(f"   - Standards applied: {result['standardsApplied']}")
                print(f"   - Compliance: {result['complianceStatus']}")
            else:
                print(f"❌ Enhanced review failed: {response.status_code}")
        else:
            print("❌ Custom standard not found")
    else:
        print(f"❌ Failed to get standards: {response.status_code}")
    
    print()

def main():
    """Run all standards and context tests."""
    print("🧪 QReviewer Standards & Context Test")
    print("=" * 60)
    print()
    
    # Test the new functionality
    test_get_standards()
    test_get_context()
    test_enhanced_review()
    test_create_custom_standard()
    test_standards_integration()
    
    print("🎉 All standards and context tests completed!")
    print()
    print("🚀 What you now have:")
    print("1. **Pre-built standards**: security, python_style, performance")
    print("2. **Context awareness**: Project files, dependencies, team preferences")
    print("3. **Enhanced reviews**: Standards-based compliance checking")
    print("4. **Custom standards**: Create team-specific rules")
    print("5. **Compliance tracking**: Pass/Warning/Fail status by standard")
    print("6. **Smart recommendations**: Standard-specific improvement suggestions")
    print()
    print("🌟 Your QReviewer is now an intelligent, standards-aware code review system!")

if __name__ == "__main__":
    main()
