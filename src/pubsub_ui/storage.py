import json
import os
from typing import Optional


class LocalStorage:
    def __init__(self, filename: str = ".storage.json"):
        self.filename = filename
        self.data = self._load()
    
    def _load(self) -> dict:
        """Load data from storage file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _save(self) -> None:
        """Save data to storage file."""
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)
    
    def get(self, key: str) -> Optional[str]:
        """Get value from storage."""
        return self.data.get(key)
    
    def set(self, key: str, value: str) -> None:
        """Set value in storage."""
        self.data[key] = value
        self._save()
