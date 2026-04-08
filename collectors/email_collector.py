"""
Email collector for parsing email exports
"""
import email
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseCollector, CollectorError, parse_timestamp, sanitize_text


class EmailCollector(BaseCollector):
    """Collect email data from EML/MBOX files"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.file_path = config.get("path")
        
        if not self.file_path:
            raise CollectorError("Email file path not provided")
        
        if not os.path.exists(self.file_path):
            raise CollectorError(f"Email file not found: {self.file_path}")
    
    def validate(self) -> bool:
        """Validate email file"""
        return os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0
    
    def collect(self) -> Dict[str, Any]:
        """Collect emails"""
        if not self.validate():
            raise CollectorError("Email file validation failed")
        
        if self.file_path.endswith('.mbox'):
            emails = self._collect_mbox()
        elif self.file_path.endswith('.eml'):
            emails = self._collect_eml()
        else:
            raise CollectorError(f"Unsupported email format: {self.file_path}")
        
        self.collected_data["messages"] = emails
        self.collected_data["metadata"] = {
            "source": "email",
            "collected_at": datetime.now().isoformat(),
            "total_messages": len(emails)
        }
        
        return self.collected_data
    
    def _collect_eml(self) -> List[Dict[str, Any]]:
        """Collect from single EML file"""
        with open(self.file_path, 'rb') as f:
            msg = email.message_from_bytes(f.read())
        
        return [self._parse_email(msg)]
    
    def _collect_mbox(self) -> List[Dict[str, Any]]:
        """Collect from MBOX file"""
        emails = []
        
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            mbox = email.mbox(f)
            
            for msg in mbox:
                email_data = self._parse_email(msg)
                if email_data:
                    emails.append(email_data)
        
        return emails
    
    def _parse_email(self, msg) -> Optional[Dict[str, Any]]:
        """Parse an email message"""
        # Extract headers
        from_addr = msg.get("From", "")
        to_addr = msg.get("To", "")
        cc_addr = msg.get("Cc", "")
        subject = msg.get("Subject", "")
        date_str = msg.get("Date", "")
        
        # Extract body
        body = self._extract_body(msg)
        
        # Parse timestamp
        timestamp = parse_timestamp(date_str)
        
        return {
            "content": sanitize_text(body),
            "sender": from_addr,
            "recipient": to_addr,
            "cc": cc_addr,
            "subject": subject,
            "timestamp": timestamp.isoformat() if timestamp else "",
            "type": "email"
        }
    
    def _extract_body(self, msg) -> str:
        """Extract email body"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                if content_type == "text/plain":
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        body += part.get_payload(decode=True).decode(charset, errors='ignore')
                    except:
                        pass
                elif content_type == "text/html":
                    # TODO: Extract text from HTML
                    pass
        else:
            charset = msg.get_content_charset() or "utf-8"
            try:
                body = msg.get_payload(decode=True).decode(charset, errors='ignore')
            except:
                body = str(msg.get_payload())
        
        return body
