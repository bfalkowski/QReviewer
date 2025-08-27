#!/usr/bin/env python3
"""Basic functionality test for QReviewer."""

import json
import tempfile
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, '.')

from qrev.models import PRInfo, PRFilePatch, PRDiff, Hunk, Finding, FindingsReport
from qrev.diff import infer_language, parse_hunk_header, split_patch_into_hunks


def test_models():
    """Test basic model functionality."""
    print("🧪 Testing Pydantic models...")
    
    # Test PRInfo
    pr_info = PRInfo(
        url="https://github.com/org/repo/pull/123",
        number=123,
        repo="org/repo"
    )
    assert pr_info.url == "https://github.com/org/repo/pull/123"
    assert pr_info.number == 123
    assert pr_info.repo == "org/repo"
    
    # Test PRFilePatch
    file_patch = PRFilePatch(
        path="src/example.py",
        status="modified",
        patch="@@ -1,3 +1,6 @@\n-old line\n+new line 1\n+new line 2\n+new line 3\n",
        additions=3,
        deletions=1
    )
    assert file_patch.path == "src/example.py"
    assert file_patch.additions == 3
    assert file_patch.deletions == 1
    
    # Test PRDiff
    pr_diff = PRDiff(pr=pr_info, files=[file_patch])
    assert len(pr_diff.files) == 1
    assert pr_diff.pr.number == 123
    
    print("✅ Models test passed!")


def test_diff_parsing():
    """Test diff parsing functionality."""
    print("🔍 Testing diff parsing...")
    
    # Test language inference
    assert infer_language("src/example.py") == "python"
    assert infer_language("src/component.tsx") == "typescript"
    assert infer_language("src/style.css") == "css"
    assert infer_language("README.md") == "markdown"
    
    # Test hunk header parsing
    header = "@@ -10,6 +10,8 @@"
    old_start, old_count, new_start, new_count = parse_hunk_header(header)
    assert old_start == 10
    assert old_count == 6
    assert new_start == 10
    assert new_count == 8
    
    # Test hunk extraction
    patch = "@@ -1,3 +1,6 @@\n-old line\n+new line 1\n+new line 2\n+new line 3\n"
    hunks = split_patch_into_hunks(patch, "src/example.py")
    assert len(hunks) == 1
    assert hunks[0].file_path == "src/example.py"
    assert hunks[0].hunk_header == "@@ -1,3 +1,6 @@"
    assert hunks[0].start_line == 1
    assert hunks[0].end_line == 6
    
    print("✅ Diff parsing test passed!")


def test_json_serialization():
    """Test JSON serialization/deserialization."""
    print("💾 Testing JSON serialization...")
    
    # Create a complete findings report
    pr_info = PRInfo(
        url="https://github.com/org/repo/pull/123",
        number=123,
        repo="org/repo"
    )
    
    finding = Finding(
        file="src/example.py",
        hunk_header="@@ -10,6 +10,8 @@",
        severity="major",
        category="security",
        message="Escape untrusted HTML before rendering.",
        confidence=0.86,
        suggested_patch="```suggestion\nreturn sanitize(html)\n```",
        line_hint=18
    )
    
    findings_report = FindingsReport(pr=pr_info, findings=[finding])
    
    # Test serialization
    json_data = findings_report.dict()
    assert json_data["pr"]["number"] == 123
    assert len(json_data["findings"]) == 1
    assert json_data["findings"][0]["severity"] == "major"
    
    # Test deserialization
    reconstructed = FindingsReport.parse_obj(json_data)
    assert reconstructed.pr.number == 123
    assert len(reconstructed.findings) == 1
    assert reconstructed.findings[0].severity == "major"
    
    print("✅ JSON serialization test passed!")


def test_file_output():
    """Test file output functionality."""
    print("📁 Testing file output...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a simple findings report
        pr_info = PRInfo(
            url="https://github.com/org/repo/pull/123",
            number=123,
            repo="org/repo"
        )
        
        findings_report = FindingsReport(pr=pr_info, findings=[])
        
        # Write to file
        output_file = temp_path / "test_findings.json"
        with open(output_file, 'w') as f:
            json.dump(findings_report.dict(), f, indent=2)
        
        # Verify file exists and can be read
        assert output_file.exists()
        with open(output_file, 'r') as f:
            data = json.load(f)
            assert data["pr"]["number"] == 123
        
        print("✅ File output test passed!")


def main():
    """Run all tests."""
    print("🚀 Starting QReviewer basic functionality tests...\n")
    
    try:
        test_models()
        test_diff_parsing()
        test_json_serialization()
        test_file_output()
        
        print("\n🎉 All tests passed! QReviewer is working correctly.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
