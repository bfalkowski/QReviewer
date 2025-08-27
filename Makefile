.PHONY: help install dev test build run clean docker-build docker-run docker-stop

# Default target
help:
	@echo "QReviewer - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker Compose services"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       - Clean up generated files"
	@echo "  help        - Show this help message"

# Install dependencies
install:
	pip install -r requirements.txt

# Run development server
dev:
	@echo "Starting development server..."
	@echo "Make sure you have set the required environment variables:"
	@echo "  GITHUB_TOKEN, AWS_REGION, MODEL_ID (optional: QREVIEWER_API_KEY)"
	@echo ""
	uvicorn qrev.api.app:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	python -m pytest tests/ -v

# Build Docker image
docker-build:
	docker build -t qreviewer-api .

# Run with Docker Compose
docker-run:
	@echo "Starting QReviewer API with Docker Compose..."
	@echo "Make sure you have set the required environment variables:"
	@echo "  GITHUB_TOKEN, AWS_REGION, MODEL_ID (optional: QREVIEWER_API_KEY)"
	@echo ""
	docker-compose up --build

# Stop Docker Compose services
docker-stop:
	docker-compose down

# Clean up generated files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Quick test of the API
test-api:
	@echo "Testing API endpoints..."
	@echo "Health check:"
	curl -s http://localhost:8000/health | jq .
	@echo ""
	@echo "Root endpoint:"
	curl -s http://localhost:8000/ | head -20
