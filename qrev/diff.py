"""Unified diff parsing and hunk extraction."""

import re
from typing import List, Optional, Tuple
from .models import Hunk, PRFilePatch


def infer_language(file_path: str) -> Optional[str]:
    """Infer programming language from file extension."""
    extension_map = {
        # Common web languages
        '.js': 'javascript', '.jsx': 'javascript', '.ts': 'typescript', '.tsx': 'typescript',
        '.html': 'html', '.htm': 'html', '.css': 'css', '.scss': 'scss', '.sass': 'sass',
        
        # Python
        '.py': 'python', '.pyi': 'python',
        
        # Java
        '.java': 'java', '.kt': 'kotlin',
        
        # C-family
        '.c': 'c', '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.h': 'c', '.hpp': 'cpp',
        
        # Go
        '.go': 'go',
        
        # Rust
        '.rs': 'rust',
        
        # Ruby
        '.rb': 'ruby',
        
        # PHP
        '.php': 'php',
        
        # Shell
        '.sh': 'bash', '.bash': 'bash', '.zsh': 'bash',
        
        # Configuration
        '.yaml': 'yaml', '.yml': 'yaml', '.json': 'json', '.toml': 'toml', '.ini': 'ini',
        '.cfg': 'ini', '.conf': 'ini',
        
        # Documentation
        '.md': 'markdown', '.rst': 'rst', '.txt': 'text'
    }
    
    for ext, lang in extension_map.items():
        if file_path.lower().endswith(ext):
            return lang
    
    return None


def parse_hunk_header(header: str) -> Tuple[int, int, int, int]:
    """Parse hunk header @@ -a,b +c,d @@ to extract line numbers."""
    pattern = r"^@@ -(\d+),(\d+) \+(\d+),(\d+) @@"
    match = re.match(pattern, header)
    if not match:
        raise ValueError(f"Invalid hunk header: {header}")
    
    old_start, old_count, new_start, new_count = map(int, match.groups())
    return old_start, old_count, new_start, new_count


def split_patch_into_hunks(patch: str, file_path: str) -> List[Hunk]:
    """Split unified diff patch into individual hunks."""
    if not patch:
        return []
    
    # Split by hunk headers
    hunk_pattern = r"(@@ -\d+,\d+ \+\d+,\d+ @@.*?)(?=@@ -\d+,\d+ \+\d+,\d+ @@|$)"
    hunks = re.findall(hunk_pattern, patch, re.DOTALL)
    
    result = []
    for hunk_text in hunks:
        # Extract header and content
        lines = hunk_text.strip().split('\n')
        header = lines[0]
        content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
        try:
            old_start, old_count, new_start, new_count = parse_hunk_header(header)
            
            # Calculate line hints for the finding
            # For additions, use the new line range
            start_line = new_start
            end_line = new_start + new_count - 1 if new_count > 0 else new_start
            
            hunk = Hunk(
                file_path=file_path,
                hunk_header=header,
                patch_text=content,
                start_line=start_line,
                end_line=end_line,
                language=infer_language(file_path)
            )
            result.append(hunk)
            
        except ValueError as e:
            # Skip invalid hunks
            continue
    
    return result


def extract_hunks_from_files(files: List[PRFilePatch]) -> List[Hunk]:
    """Extract hunks from all PR files."""
    all_hunks = []
    
    for file_patch in files:
        if file_patch.patch:
            hunks = split_patch_into_hunks(file_patch.patch, file_patch.path)
            all_hunks.extend(hunks)
    
    return all_hunks
