import os
import hashlib
import json
from typing import List, Optional

class ChangeDetector:
    """
    A utility to detect changes in source directories using recursive file hashing.
    Supports skipping heavy computations if the state is unchanged.
    """
    
    def __init__(self, watch_dir: str, state_file: str, ignore_patterns: Optional[List[str]] = None):
        self.watch_dir = watch_dir
        self.state_file = os.path.basename(state_file)
        self.ignore_patterns = ignore_patterns or [
            "__pycache__", 
            ".pytest_cache", 
            "reports", 
            ".git", 
            ".venv",
            "venv",
            ".build_state.json"
        ]
        # Always ignore the state file itself
        if self.state_file not in self.ignore_patterns:
            self.ignore_patterns.append(self.state_file)

    def has_changed(self) -> bool:
        """
        Computes the current hash and compares it with the stored state.
        Returns True if changes are detected or if no state exists.
        """
        current_hash = self._compute_recursive_hash()
        stored_hash = self._load_state()
        
        if current_hash != stored_hash:
            # We don't save the state here, we only do it after a successful build/test
            return True
        return False

    def save_state(self):
        """Persists the current hash to the state file."""
        current_hash = self._compute_recursive_hash()
        with open(self.state_file, 'w') as f:
            json.dump({"hash": current_hash}, f)

    def _compute_recursive_hash(self) -> str:
        """Computes a combined MD5 hash of all files in the watch directory."""
        hasher = hashlib.md5()
        
        for root, dirs, files in os.walk(self.watch_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            for file in sorted(files):
                if any(pattern in file for pattern in self.ignore_patterns):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        # Add relative path to mix to catch renames
                        rel_path = os.path.relpath(file_path, self.watch_dir)
                        hasher.update(rel_path.encode())
                        
                        # Add content
                        while chunk := f.read(8192):
                            hasher.update(chunk)
                except (OSError, IOError):
                    # Skip files that can't be read (e.g. locked files)
                    continue
        
        return hasher.hexdigest()

    def _load_state(self) -> Optional[str]:
        """Loads the last saved hash from the state file."""
        if not os.path.exists(self.state_file):
            return None
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                return data.get("hash")
        except (json.JSONDecodeError, OSError):
            return None
