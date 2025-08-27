"""Utility functions for QReviewer API."""

import hashlib
import time
import uuid
from contextlib import contextmanager
from typing import Dict


def make_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def hash_html(html: str) -> str:
    """Generate SHA256 hash of HTML content."""
    return "sha256:" + hashlib.sha256(html.encode("utf-8")).hexdigest()


@contextmanager
def timed(bucket: Dict[str, int], key: str):
    """
    Context manager to time operations and store results in milliseconds.
    
    Args:
        bucket: Dictionary to store timing results
        key: Key for storing the timing result
    """
    start_time = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        bucket[key] = duration_ms
