"""
Base analyzer class for data analysis
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and return results"""
        pass
