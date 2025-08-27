#!/usr/bin/env python3
"""Demo script for QReviewer functionality."""

import json
from pathlib import Path

# Add current directory to path
import sys
sys.path.insert(0, '.')

from qrev.models import PRInfo, PRFilePatch, PRDiff, Hunk, Finding, FindingsReport
from qrev.diff import extract_hunks_from_files
from qrev.q_client import review_hunk, apply_security_heuristics


def create_demo_data():
    """Create demo PR diff data."""
    print("🎭 Creating demo PR diff data...")
    
    # Create a sample PR
    pr_info = PRInfo(
        url="https://github.com/org/demo-repo/pull/42",
        number=42,
        repo="org/demo-repo"
    )
    
    # Create sample file patches
    files = [
        PRFilePatch(
            path="src/auth.py",
            status="modified",
            patch="""@@ -15,6 +15,8 @@
 def authenticate_user(username, password):
-    # Simple authentication
-    if username == "admin" and password == "password":
+    # Secure authentication with hashing
+    if not username or not password:
+        return False
+    hashed_password = hash_password(password)
+    if username == "admin" and verify_password(password, hashed_password):
         return True
     return False
""",
            additions=4,
            deletions=2
        ),
        PRFilePatch(
            path="src/utils.py",
            status="modified",
            patch="""@@ -8,10 +8,12 @@
 def process_user_input(user_input):
-    # Process user input directly
-    return user_input
+    # Sanitize user input before processing
+    if not user_input:
+        return ""
+    sanitized = sanitize_input(user_input)
+    return sanitized
""",
            additions=4,
            deletions=2
        )
    ]
    
    pr_diff = PRDiff(pr=pr_info, files=files)
    
    # Save demo data
    with open("demo-pr-diff.json", "w") as f:
        json.dump(pr_diff.dict(), f, indent=2)
    
    print("✅ Demo PR diff saved to demo-pr-diff.json")
    return pr_diff


def demo_review_process():
    """Demonstrate the review process."""
    print("\n🔍 Demonstrating review process...")
    
    # Load demo data
    with open("demo-pr-diff.json", "r") as f:
        pr_diff_data = json.load(f)
        pr_diff = PRDiff.parse_obj(pr_diff_data)
    
    # Extract hunks
    print("📝 Extracting code hunks...")
    hunks = extract_hunks_from_files(pr_diff.files)
    print(f"✅ Found {len(hunks)} hunks to review")
    
    # Review each hunk
    print("\n🤖 Reviewing code hunks...")
    all_findings = []
    
    for i, hunk in enumerate(hunks, 1):
        print(f"  Reviewing hunk {i}: {hunk.file_path}")
        print(f"    Header: {hunk.hunk_header}")
        print(f"    Language: {hunk.language}")
        
        # Get findings from Q client (stub)
        findings = review_hunk(hunk)
        all_findings.extend(findings)
        
        for finding in findings:
            print(f"    Finding: [{finding.severity.upper()}] {finding.message}")
    
    # Apply security heuristics
    print("\n🔒 Applying security heuristics...")
    all_findings = apply_security_heuristics(all_findings)
    
    # Create findings report
    findings_report = FindingsReport(
        pr=pr_diff.pr,
        findings=all_findings
    )
    
    # Save findings
    with open("demo-findings.json", "w") as f:
        json.dump(findings_report.dict(), f, indent=2)
    
    print("✅ Demo findings saved to demo-findings.json")
    
    # Display summary
    print(f"\n📊 Review Summary:")
    print(f"  Total findings: {len(all_findings)}")
    
    severity_counts = {}
    category_counts = {}
    
    for finding in all_findings:
        severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
    
    print(f"  By severity: {severity_counts}")
    print(f"  By category: {category_counts}")


def main():
    """Run the demo."""
    print("🚀 QReviewer Demo")
    print("=" * 50)
    
    try:
        # Create demo data
        create_demo_data()
        
        # Run review process
        demo_review_process()
        
        print("\n🎉 Demo completed successfully!")
        print("\nGenerated files:")
        print("  - demo-pr-diff.json: Sample PR diff")
        print("  - demo-findings.json: Sample findings")
        
        print("\nTo test the CLI:")
        print("  python -m qrev.cli summarize --inp demo-findings.json")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
