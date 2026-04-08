"""
WeChat collector for parsing WeChat message exports
"""
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseCollector, CollectorError, parse_timestamp, sanitize_text


class WeChatCollector(BaseCollector):
    """Collect WeChat message data from SQLite exports"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.db_path = config.get("path")
        
        if not self.db_path:
            raise CollectorError("WeChat database path not provided")
        
        if not os.path.exists(self.db_path):
            raise CollectorError(f"WeChat database not found: {self.db_path}")
    
    def validate(self) -> bool:
        """Validate WeChat database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if required table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Message'")
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
        except Exception as e:
            raise CollectorError(f"Failed to validate WeChat database: {e}")
    
    def collect(self) -> Dict[str, Any]:
        """Collect WeChat messages"""
        if not self.validate():
            raise CollectorError("WeChat database validation failed")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Collect messages
        try:
            messages = self._collect_messages(cursor)
            contacts = self._collect_contacts(cursor)
            rooms = self._collect_rooms(cursor)
            
            self.collected_data["messages"] = messages
            self.collected_data["contacts"] = contacts
            self.collected_data["rooms"] = rooms
            self.collected_data["metadata"] = {
                "source": "wechat",
                "collected_at": datetime.now().isoformat(),
                "total_messages": len(messages),
                "total_contacts": len(contacts)
            }
            
            return self.collected_data
        finally:
            conn.close()
    
    def _collect_messages(self, cursor) -> List[Dict[str, Any]]:
        """Collect messages from database"""
        messages = []
        
        # Try different schemas (WeChatMsg vs PyWxDump vs 留痕)
        schemas = [
            "SELECT * FROM Message",
            "SELECT * FROM messages",
            "SELECT * FROM MSG"
        ]
        
        for schema in schemas:
            try:
                cursor.execute(schema)
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        message = self._parse_message_row(dict(row))
                        if message:
                            messages.append(message)
                    break
            except Exception:
                continue
        
        # Sort by timestamp
        messages.sort(key=lambda x: x.get("timestamp", ""))
        return messages
    
    def _collect_contacts(self, cursor) -> List[Dict[str, Any]]:
        """Collect contacts"""
        contacts = []
        
        try:
            cursor.execute("SELECT * FROM Contact")
            rows = cursor.fetchall()
            
            for row in rows:
                contact = dict(row)
                contacts.append({
                    "username": contact.get("userName", ""),
                    "alias": contact.get("alias", ""),
                    "remark": contact.get("remark", ""),
                    "nickname": contact.get("nickname", "")
                })
        except Exception:
            pass
        
        return contacts
    
    def _collect_rooms(self, cursor) -> List[Dict[str, Any]]:
        """Collect chat rooms"""
        rooms = []
        
        try:
            cursor.execute("SELECT * FROM ChatRoom")
            rows = cursor.fetchall()
            
            for row in rows:
                room = dict(row)
                rooms.append({
                    "chatroom_id": room.get("chatRoomName", ""),
                    "display_name": room.get("displayName", ""),
                    "members": room.get("chatRoomData", "")
                })
        except Exception:
            pass
        
        return rooms
    
    def _parse_message_row(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a message row"""
        # Try different field names across different export formats
        content = (
            row.get("content") or
            row.get("strContent") or
            row.get("message") or
            row.get("textContent") or
            ""
        )
        
        if not content:
            return None
        
        sender = (
            row.get("sender") or
            row.get("talker") or
            row.get("isSender") or
            ""
        )
        
        timestamp_str = (
            row.get("createTime") or
            row.get("timestamp") or
            row.get("msgSvrTime") or
            row.get("time") or
            ""
        )
        
        timestamp = parse_timestamp(timestamp_str)
        
        return {
            "content": sanitize_text(content),
            "sender": sender,
            "timestamp": timestamp.isoformat() if timestamp else "",
            "type": row.get("type", 1),
            "is_self": bool(row.get("isSender", False))
        }


# Legacy compatibility - WeChatMsg format
class WeChatMsgCollector(WeChatCollector):
    """Collector for WeChatMsg export format"""
    pass


# 留痕 format
class LiuhenCollector(WeChatCollector):
    """Collector for 留痕 export format (macOS)"""
    pass


# PyWxDump format
class PyWxDumpCollector(WeChatCollector):
    """Collector for PyWxDump export format"""
    pass
