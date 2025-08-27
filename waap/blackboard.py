"""Blackboard helper for WaaP agents."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Blackboard:
    """Simple blackboard implementation using filesystem."""
    
    def __init__(self, context_file: str = "context.json"):
        """Initialize blackboard with context file path."""
        self.context_file = Path(context_file)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the blackboard by key."""
        if not self.context_file.exists():
            return default
        
        try:
            with open(self.context_file, 'r') as f:
                context = json.load(f)
            
            # Support dot notation for nested keys
            keys = key.split('.')
            value = context
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except (json.JSONDecodeError, IOError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the blackboard by key."""
        # Load existing context or create new
        context = {}
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    context = json.load(f)
            except (json.JSONDecodeError, IOError):
                context = {}
        
        # Support dot notation for nested keys
        keys = key.split('.')
        current = context
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the final value
        current[keys[-1]] = value
        
        # Ensure directory exists
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write back to file
        with open(self.context_file, 'w') as f:
            json.dump(context, f, indent=2)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all context data."""
        if not self.context_file.exists():
            return {}
        
        try:
            with open(self.context_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}


def get_blackboard() -> Blackboard:
    """Get a blackboard instance."""
    return Blackboard()
