"""
QQ collector for parsing QQ message exports
"""
import re
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseCollector, CollectorError, parse_timestamp, sanitize_text


class QQCollector(BaseCollector):
    """Collect QQ message data from text/html exports"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.file_path = config.get("path")
        
        if not self.file_path:
            raise CollectorError("QQ export path not provided")
        
        if not os.path.exists(self.file_path):
            raise CollectorError(f"QQ export not found: {self.file_path}")
    
    def validate(self) -> bool:
        """Validate QQ export file"""
        return os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0
    
    def collect(self) -> Dict[str, Any]:
        """Collect QQ messages"""
        if not self.validate():
            raise CollectorError("QQ export validation failed")
        
        # Detect file format
        if self.file_path.endswith('.txt'):
            messages = self._collect_txt()
        elif self.file_path.endswith('.mht'):
            messages = self._collect_mht()
        else:
            raise CollectorError(f"Unsupported QQ export format: {self.file_path}")
        
        self.collected_data["messages"] = messages
        self.collected_data["metadata"] = {
            "source": "qq",
            "collected_at": datetime.now().isoformat(),
            "total_messages": len(messages),
            "format": os.path.splitext(self.file_path)[1][1:]
        }
        
        return self.collected_data
    
    def _collect_txt(self) -> List[Dict[str, Any]]:
        """Collect from TXT format"""
        messages = []
        
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                message = self._parse_txt_line(line)
                if message:
                    messages.append(message)
        
        return messages
    
    def _parse_txt_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a TXT message line
        
        Example format:
        2024-04-07 10:30:00 QQ User: message content
        [2024-04-07 10:30:00] QQ User: message content
        """
        line = line.strip()
        if not line:
            return None
        
        # Try different patterns
        patterns = [
            # Pattern 1: YYYY-MM-DD HH:MM:SS Name: Message
            r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+([^:]+):\s*(.+)$',
            # Pattern 2: [YYYY-MM-DD HH:MM:SS] Name: Message
            r'^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+([^:]+):\s*(.+)$',
            # Pattern 3: Name(YYYY-MM-DD HH:MM:SS): Message
            r'^([^()]+)\((\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\):\s*(.+)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                
                # Extract based on pattern
                if len(groups) == 3:
                    timestamp_str = groups[0]
                    sender = groups[1]
                    content = groups[2]
                elif len(groups) == 3:
                    sender = groups[0]
                    timestamp_str = groups[1]
                    content = groups[2]
                else:
                    continue
                
                timestamp = parse_timestamp(timestamp_str)
                
                return {
                    "content": sanitize_text(content),
                    "sender": sender.strip(),
                    "timestamp": timestamp.isoformat() if timestamp else "",
                    "type": "text",
                    "is_self": "我" in sender or "Me" in sender
                }
        
        return None
    
    def _collect_mht(self) -> List[Dict[str, Any]]:
        """Collect from MHT format (web archive)"""
        # TODO: Implement MHT parsing
        # MHT files are HTML-like with embedded resources
        # For now, return empty
        return []


# QQ Manager format (official export)
class QQManagerCollector(QQCollector):
    """Collector for QQ Manager export format"""
    pass
