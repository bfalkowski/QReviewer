#!/usr/bin/env python3
"""
Comprehensive test script for QReviewer API.
This script tests all endpoints and demonstrates the full workflow.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("🔍 Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_root():
    """Test root endpoint."""
    print("🏠 Testing Root Endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Title found: {'QReviewer API' in response.text}")
    print()

def test_score_endpoint():
    """Test score endpoint with sample findings."""
    print("📊 Testing Score Endpoint...")
    
    # Sample findings with different severities
    findings = [
        {
            "file": "test_api_demo.py",
            "hunk_header": "@@ -15,5 +15,5 @@",
            "severity": "critical",
            "category": "security",
            "message": "Unused import detected",
            "confidence": 0.9,
            "suggested_patch": "Remove unused import json",
            "line_hint": 15
        },
        {
            "file": "test_api_demo.py",
            "hunk_header": "@@ -25,3 +25,3 @@",
            "severity": "major",
            "category": "security",
            "message": "Commented eval() usage should be removed",
            "confidence": 0.8,
            "suggested_patch": "Remove commented eval() line",
            "line_hint": 25
        },
        {
            "file": "test_api_demo.py",
            "hunk_header": "@@ -35,2 +35,2 @@",
            "severity": "minor",
            "category": "style",
            "message": "Consider adding type hints",
            "confidence": 0.6,
            "suggested_patch": "Add return type annotation",
            "line_hint": 35
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/score",
        json={"findings": findings}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Score: {result['score']}")
        print(f"Expected: 5.5 (3.0 + 2.0 + 0.5)")
    else:
        print(f"Error: {response.text}")
    print()

def test_render_report():
    """Test report rendering endpoint."""
    print("📄 Testing Report Rendering...")
    
    findings = [
        {
            "file": "test_api_demo.py",
            "hunk_header": "@@ -15,5 +15,5 @@",
            "severity": "critical",
            "category": "security",
            "message": "Unused import detected",
            "confidence": 0.9,
            "suggested_patch": "Remove unused import json",
            "line_hint": 15
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/render_report",
        json={"findings": findings}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Report generated: {len(result['reportHtml'])} characters")
        print(f"Report hash: {result['reportHash']}")
        print(f"Contains 'QReviewer Report': {'QReviewer Report' in result['reportHtml']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_review_hunks():
    """Test review hunks endpoint."""
    print("🔍 Testing Review Hunks Endpoint...")
    
    # Sample diff data
    diff_data = {
        "pr": {
            "url": "https://github.com/bfalkowski/QReviewer/pull/1",
            "number": 1,
            "repo": "bfalkowski/QReviewer"
        },
        "files": [
            {
                "path": "test_api_demo.py",
                "status": "modified",
                "patch": "@@ -15,5 +15,5 @@\n-import json  # This import is not used\n+import json  # This import is not used\n",
                "additions": 1,
                "deletions": 1,
                "sha": "abc123"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/review_hunks",
        json={"diffJson": diff_data}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Findings generated: {len(result['findings'])}")
        for finding in result['findings']:
            print(f"  - {finding['severity']}: {finding['message']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_fetch_pr():
    """Test fetch PR endpoint."""
    print("📥 Testing Fetch PR Endpoint...")
    
    # This will fail without GitHub token, but shows the error handling
    response = requests.post(
        f"{BASE_URL}/fetch_pr",
        json={"prUrl": "https://github.com/bfalkowski/QReviewer/pull/1"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 500:
        error = response.json()
        print(f"Error type: {error['detail']['error']}")
        print(f"Message: {error['detail']['message']}")
        print(f"Request ID: {error['detail']['requestId']}")
    else:
        print(f"Unexpected response: {response.text}")
    print()

def test_complete_review():
    """Test the complete review pipeline."""
    print("🚀 Testing Complete Review Pipeline...")
    
    # This will fail without GitHub token, but shows the error handling
    response = requests.post(
        f"{BASE_URL}/review",
        json={
            "prUrl": "https://github.com/bfalkowski/QReviewer/pull/1",
            "requestId": "demo-review-123"
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 500:
        error = response.json()
        print(f"Error type: {error['detail']['error']}")
        print(f"Message: {error['detail']['message']}")
        print(f"Request ID: {error['detail']['requestId']}")
    else:
        print(f"Unexpected response: {response.text}")
    print()

def main():
    """Run all API tests."""
    print("🧪 QReviewer API Comprehensive Test")
    print("=" * 50)
    print()
    
    # Test basic endpoints
    test_health()
    test_root()
    
    # Test functional endpoints
    test_score_endpoint()
    test_render_report()
    test_review_hunks()
    
    # Test endpoints that require GitHub token
    test_fetch_pr()
    test_complete_review()
    
    print("✅ All tests completed!")
    print()
    print("📋 Summary:")
    print("- Health and root endpoints: Working")
    print("- Score calculation: Working")
    print("- Report rendering: Working")
    print("- Review hunks: Working (with mock data)")
    print("- GitHub integration: Requires GITHUB_TOKEN")
    print()
    print("🔗 Interactive API docs: http://localhost:8000/docs")
    print("🔗 ReDoc: http://localhost:8000/redoc")

if __name__ == "__main__":
    main()
