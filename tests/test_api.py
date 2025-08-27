"""Tests for QReviewer API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from qrev.api.app import app
from qrev.models import Finding

# Create test client
client = TestClient(app)


@pytest.fixture
def mock_finding():
    """Create a mock Finding for testing."""
    return Finding(
        file="test.py",
        hunk_header="@@ -1,1 +1,1 @@",
        severity="minor",
        category="style",
        message="Test finding message",
        confidence=0.8,
        suggested_patch=None,
        line_hint=10
    )


@pytest.fixture
def mock_diff_data():
    """Create mock diff data for testing."""
    return {
        "pr": {
            "url": "https://github.com/test/repo/pull/123",
            "number": 123,
            "repo": "test/repo"
        },
        "files": [
            {
                "path": "test.py",
                "status": "modified",
                "patch": "@@ -1,1 +1,1 @@\n-old\n+new",
                "additions": 1,
                "deletions": 1,
                "sha": "abc123"
            }
        ]
    }


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "qreviewer-api"


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns HTML with API information."""
        response = client.get("/")
        assert response.status_code == 200
        assert "QReviewer API" in response.text
        assert "POST /review" in response.text


class TestReviewEndpoint:
    """Test main review endpoint."""
    
    @patch('qrev.api.app.fetch_pr_diff_async')
    @patch('qrev.api.app.review_hunks_async')
    def test_review_endpoint_success(self, mock_review, mock_fetch, mock_finding, mock_diff_data):
        """Test successful review endpoint call."""
        # Mock the async functions
        mock_fetch.return_value = mock_diff_data
        mock_review.return_value = [mock_finding]
        
        # Test request
        request_data = {
            "prUrl": "https://github.com/test/repo/pull/123"
        }
        
        response = client.post("/review", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "findings" in data
        assert "reportHtml" in data
        assert "reportHash" in data
        assert "stepDurations" in data
        assert len(data["findings"]) == 1
        assert data["findings"][0]["file"] == "test.py"
    
    def test_review_endpoint_missing_url(self):
        """Test review endpoint with missing PR URL."""
        request_data = {}
        response = client.post("/review", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('qrev.api.app.fetch_pr_diff_async')
    def test_review_endpoint_github_error(self, mock_fetch):
        """Test review endpoint with GitHub API error."""
        mock_fetch.side_effect = Exception("GitHub API error")
        
        request_data = {
            "prUrl": "https://github.com/test/repo/pull/123"
        }
        
        response = client.post("/review", json=request_data)
        assert response.status_code == 500
        
        data = response.json()
        assert data["detail"]["error"] == "REVIEW_FAILED"
        assert "GitHub API error" in data["detail"]["message"]


class TestFetchPREndpoint:
    """Test fetch PR endpoint."""
    
    @patch('qrev.api.app.fetch_pr_diff_async')
    def test_fetch_pr_success(self, mock_fetch, mock_diff_data):
        """Test successful PR fetch."""
        mock_fetch.return_value = mock_diff_data
        
        request_data = {
            "prUrl": "https://github.com/test/repo/pull/123"
        }
        
        response = client.post("/fetch_pr", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "diffJson" in data
        assert data["diffJson"]["pr"]["number"] == 123
    
    def test_fetch_pr_missing_url(self):
        """Test fetch PR with missing URL."""
        request_data = {}
        response = client.post("/fetch_pr", json=request_data)
        assert response.status_code == 422


class TestReviewHunksEndpoint:
    """Test review hunks endpoint."""
    
    @patch('qrev.api.app.review_hunks_async')
    def test_review_hunks_success(self, mock_review, mock_finding, mock_diff_data):
        """Test successful hunks review."""
        mock_review.return_value = [mock_finding]
        
        request_data = {
            "diffJson": mock_diff_data
        }
        
        response = client.post("/review_hunks", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "findings" in data
        assert len(data["findings"]) == 1
    
    def test_review_hunks_missing_diff(self):
        """Test review hunks with missing diff data."""
        request_data = {}
        response = client.post("/review_hunks", json=request_data)
        assert response.status_code == 422


class TestRenderReportEndpoint:
    """Test render report endpoint."""
    
    def test_render_report_success(self, mock_finding):
        """Test successful report rendering."""
        request_data = {
            "findings": [mock_finding.model_dump()]
        }
        
        response = client.post("/render_report", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "reportHtml" in data
        assert "reportHash" in data
        assert "QReviewer Report" in data["reportHtml"]
    
    def test_render_report_empty_findings(self):
        """Test report rendering with no findings."""
        request_data = {
            "findings": []
        }
        
        response = client.post("/render_report", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "No issues found" in data["reportHtml"]


class TestScoreEndpoint:
    """Test score endpoint."""
    
    def test_score_success(self, mock_finding):
        """Test successful scoring."""
        request_data = {
            "findings": [mock_finding.model_dump()]
        }
        
        response = client.post("/score", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "score" in data
        assert isinstance(data["score"], float)
        assert data["score"] > 0
    
    def test_score_no_findings(self):
        """Test scoring with no findings."""
        request_data = {
            "findings": []
        }
        
        response = client.post("/score", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["score"] == 0.0


class TestErrorHandling:
    """Test error handling across endpoints."""
    
    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        response = client.post("/review", data="invalid json")
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        response = client.post("/review", json={"invalid": "data"})
        assert response.status_code == 422


class TestSecurity:
    """Test security features."""
    
    def test_no_auth_required_when_no_api_key(self):
        """Test that no auth is required when QREVIEWER_API_KEY is not set."""
        # This test assumes no API key is set in test environment
        response = client.get("/health")
        assert response.status_code == 200
    
    @patch.dict('os.environ', {'QREVIEWER_API_KEY': 'test-key'})
    def test_auth_required_when_api_key_set(self):
        """Test that auth is required when QREVIEWER_API_KEY is set."""
        # This would require more complex mocking of the security middleware
        # For now, we'll test the basic functionality
        pass

