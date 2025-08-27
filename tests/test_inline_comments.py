#!/usr/bin/env python3
"""
Test script to demonstrate QReviewer's new inline commenting functionality.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

# Your real PR URL
PR_URL = "https://github.com/bfalkowski/QReviewer/pull/1"

def test_post_review_with_inline_comments():
    """Test posting a review with inline comments to your PR."""
    print("🔍 Testing inline comment posting to your PR #1...")
    
    # Enhanced findings with better suggestions for inline commenting
    findings = [
        {
            "file": "test_api_demo.py",
            "hunk_header": "@@ -15,5 +15,5 @@",
            "severity": "critical",
            "category": "security",
            "message": "Unused import 'json' detected - this should be removed to avoid confusion",
            "confidence": 0.95,
            "suggested_patch": "import os\nimport sys\nfrom typing import List, Dict, Any\n\n# Intentional issue: unused import\n# import json  # This import is not used",
            "line_hint": 15
        },
        {
            "file": "test_api_demo.py",
            "hunk_header": "@@ -25,3 +25,3 @@",
            "severity": "major",
            "category": "security",
            "message": "Commented eval() usage should be completely removed - this is a security risk",
            "confidence": 0.9,
            "suggested_patch": "    # Better approach - no eval() usage\n    result = {",
            "line_hint": 25
        },
        {
            "file": "test_api_demo.py",
            "hunk_header": "@@ -35,2 +35,2 @@",
            "severity": "minor",
            "category": "style",
            "message": "Consider adding return type annotation for better code clarity",
            "confidence": 0.7,
            "suggested_patch": "def process_data(data: List[str]) -> Dict[str, Any]:",
            "line_hint": 35
        }
    ]
    
    # Test the new /post_review endpoint
    payload = {
        "prUrl": PR_URL,
        "findings": findings,
        "event": "COMMENT",  # Can be COMMENT, APPROVE, or REQUEST_CHANGES
        "body": "🔍 QReviewer Automated Code Review\n\nThis PR has been automatically reviewed and contains several findings that should be addressed before merging."
    }
    
    print(f"📤 Posting review with {len(findings)} inline comments...")
    print(f"   - Critical: 1 finding")
    print(f"   - Major: 1 finding") 
    print(f"   - Minor: 1 finding")
    
    response = requests.post(f"{BASE_URL}/post_review", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Review posted successfully!")
        print(f"   - Review ID: {result.get('reviewId', 'N/A')}")
        print(f"   - Comments posted: {result['commentsPosted']}")
        print(f"   - Message: {result['message']}")
        
        print("\n🎯 Check your PR at:")
        print(f"   {PR_URL}")
        print("   You should now see inline comments on specific lines!")
        
    else:
        print(f"❌ Failed to post review: {response.status_code}")
        print(f"   Error: {response.text}")
    
    print()

def test_post_general_comment():
    """Test posting a general comment to your PR."""
    print("💬 Testing general comment posting...")
    
    payload = {
        "prUrl": PR_URL,
        "body": """## 🎉 QReviewer Integration Complete!

This PR has been successfully reviewed by QReviewer's automated system. 

### 📊 Review Summary
- **Total Findings**: 3
- **Critical Issues**: 1 (unused import)
- **Major Issues**: 1 (commented eval usage)
- **Minor Issues**: 1 (missing type hints)

### 🚀 Next Steps
1. Review the inline comments on specific lines
2. Address the critical and major findings
3. Consider the minor suggestions for code improvement

---
*Automated review by QReviewer API*"""
    }
    
    response = requests.post(f"{BASE_URL}/post_comment", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ General comment posted successfully!")
        print(f"   - Comment ID: {result.get('commentId', 'N/A')}")
        print(f"   - Message: {result['message']}")
    else:
        print(f"❌ Failed to post comment: {response.status_code}")
        print(f"   Error: {response.text}")
    
    print()

def test_get_existing_reviews():
    """Test getting existing reviews for your PR."""
    print("📋 Testing review retrieval...")
    
    payload = {
        "prUrl": PR_URL
    }
    
    response = requests.post(f"{BASE_URL}/get_reviews", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Reviews retrieved successfully!")
        print(f"   - Total reviews: {result['totalReviews']}")
        
        if result['reviews']:
            print("   - Existing reviews:")
            for i, review in enumerate(result['reviews'], 1):
                state = review.get('state', 'unknown')
                user = review.get('user', {}).get('login', 'unknown')
                print(f"     {i}. {state} by {user}")
        else:
            print("   - No existing reviews found")
    else:
        print(f"❌ Failed to get reviews: {response.status_code}")
        print(f"   Error: {response.text}")
    
    print()

def main():
    """Run all inline commenting tests."""
    print("🧪 QReviewer Inline Commenting Test")
    print("=" * 50)
    print()
    
    # Test the new functionality
    test_post_review_with_inline_comments()
    test_post_general_comment()
    test_get_existing_reviews()
    
    print("🎉 All tests completed!")
    print()
    print("📋 What to check:")
    print("1. Go to your PR: https://github.com/bfalkowski/QReviewer/pull/1")
    print("2. Look for inline comments on specific lines")
    print("3. Check the general comment at the bottom")
    print("4. Verify the review appears in the PR timeline")
    print()
    print("🚀 Your QReviewer now supports full GitHub integration!")

if __name__ == "__main__":
    main()
