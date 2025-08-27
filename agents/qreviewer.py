"""QReviewer WaaP agent wrapper."""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import qrev modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from waap.blackboard import get_blackboard
from qrev.github_api import fetch_pr_files, GitHubAPIError
from qrev.diff import extract_hunks_from_files
from qrev.q_client import review_hunk, apply_security_heuristics
from qrev.models import FindingsReport, ReviewStats


def main():
    """Main WaaP agent entry point."""
    try:
        # Get blackboard
        blackboard = get_blackboard()
        
        # Read required context
        pr_url = blackboard.get("pr.url")
        if not pr_url:
            print("❌ Missing required blackboard key: pr.url")
            sys.exit(1)
        
        guidelines_path = blackboard.get("guidelines.path")
        
        print(f"🔍 Starting code review for PR: {pr_url}")
        
        # Step 1: Fetch PR files
        print("📥 Fetching PR files...")
        try:
            pr_diff = fetch_pr_files(pr_url)
            print(f"✅ Fetched {len(pr_diff.files)} files")
        except GitHubAPIError as e:
            print(f"❌ GitHub API error: {e}")
            sys.exit(1)
        
        # Step 2: Extract hunks
        print("🔍 Extracting code hunks...")
        hunks = extract_hunks_from_files(pr_diff.files)
        print(f"✅ Found {len(hunks)} hunks to review")
        
        if not hunks:
            print("⚠️  No hunks found to review")
            # Still write empty findings file
            findings_report = FindingsReport(
                pr=pr_diff.pr,
                findings=[]
            )
        else:
            # Step 3: Review hunks
            print("🤖 Reviewing code hunks...")
            all_findings = []
            
            # Load guidelines if provided
            guidelines_text = None
            if guidelines_path and Path(guidelines_path).exists():
                with open(guidelines_path, 'r') as f:
                    guidelines_text = f.read()
                print(f"📋 Using guidelines from: {guidelines_path}")
            
            for i, hunk in enumerate(hunks, 1):
                try:
                    print(f"  Reviewing hunk {i}/{len(hunks)}: {hunk.file_path}")
                    findings = review_hunk(hunk, guidelines_text)
                    all_findings.extend(findings)
                except Exception as e:
                    print(f"  ⚠️  Failed to review hunk in {hunk.file_path}: {e}")
            
            # Apply security heuristics
            print("🔒 Applying security heuristics...")
            all_findings = apply_security_heuristics(all_findings)
            
            # Create findings report
            findings_report = FindingsReport(
                pr=pr_diff.pr,
                findings=all_findings
            )
            
            print(f"✅ Review complete! Found {len(all_findings)} issues")
        
        # Step 4: Write results
        print("💾 Writing results...")
        
        # Ensure results directory exists
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        # Write findings to file
        findings_file = results_dir / "review.findings.json"
        with open(findings_file, 'w') as f:
            json.dump(findings_report.model_dump(), f, indent=2)
        
        print(f"📁 Findings written to: {findings_file}")
        
        # Step 5: Update blackboard
        print("🔄 Updating blackboard...")
        
        # Calculate stats
        stats = ReviewStats()
        for finding in findings_report.findings:
            if finding.severity == "blocking":
                stats.blocking += 1
            elif finding.severity == "major":
                stats.major += 1
            elif finding.severity == "minor":
                stats.minor += 1
            elif finding.severity == "nit":
                stats.nit += 1
        stats.total = len(findings_report.findings)
        
        # Set blackboard keys
        blackboard.set("review.findings", str(findings_file))
        blackboard.set("review.stats", stats.dict())
        
        print("✅ Blackboard updated with review results")
        
        # Print summary
        print(f"\n📊 Review Summary:")
        print(f"  🚫 Blocking: {stats.blocking}")
        print(f"  ⚠️  Major: {stats.major}")
        print(f"  🔧 Minor: {stats.minor}")
        print(f"  💡 Nit: {stats.nit}")
        print(f"  📈 Total: {stats.total}")
        
        print("\n🎉 QReviewer agent completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
