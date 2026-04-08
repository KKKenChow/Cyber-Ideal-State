"""
Base collector class and common utilities
"""
import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseCollector(ABC):
    """Base class for data collectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.collected_data = {
            "messages": [],
            "documents": [],
            "images": [],
            "metadata": {}
        }
    
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Collect data from source"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate source is accessible"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        return {
            "message_count": len(self.collected_data["messages"]),
            "document_count": len(self.collected_data["documents"]),
            "image_count": len(self.collected_data["images"])
        }


class CollectorError(Exception):
    """Custom exception for collector errors"""
    pass


def parse_timestamp(ts: Any) -> Optional[datetime]:
    """Parse various timestamp formats"""
    if not ts:
        return None
    
    if isinstance(ts, datetime):
        return ts
    
    if isinstance(ts, str):
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y/%m/%d %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(ts, fmt)
            except ValueError:
                continue
    
    if isinstance(ts, (int, float)):
        # Unix timestamp
        return datetime.fromtimestamp(ts)
    
    return None


def extract_text_from_image(image_path: str) -> Optional[str]:
    """Extract text from image using OCR (placeholder)"""
    # TODO: Integrate with OCR library (e.g., pytesseract)
    return None


def sanitize_text(text: str) -> str:
    """Sanitize and clean text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    import re
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters
    text = ''.join(char for char in text if char.isprintable() or char == '\n')
    
    return text.strip()
