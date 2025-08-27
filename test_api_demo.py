#!/usr/bin/env python3
"""
Test file to demonstrate QReviewer API functionality.
This file contains some intentional issues for testing the review system.
"""

import os
import sys
from typing import List, Dict, Any

# Intentional issue: unused import
import json  # This import is not used

def process_data(data: List[str]) -> Dict[str, Any]:
    """
    Process a list of strings and return statistics.
    
    Args:
        data: List of strings to process
        
    Returns:
        Dictionary with processing results
    """
    if not data:
        return {"error": "No data provided"}
    
    # Intentional issue: potential security risk with eval
    # result = eval(str(data))  # This would be flagged by security review
    
    # Better approach
    result = {
        "count": len(data),
        "total_length": sum(len(item) for item in data),
        "average_length": sum(len(item) for item in data) / len(data) if data else 0
    }
    
    return result

def main():
    """Main function to demonstrate the API."""
    # Test data
    test_data = ["hello", "world", "qreviewer", "api"]
    
    # Process the data
    result = process_data(test_data)
    
    # Print results
    print("Processing complete!")
    print(f"Results: {result}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
