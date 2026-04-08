"""
Feishu collector for auto-collecting Feishu messages and documents
"""
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseCollector, CollectorError, sanitize_text


class FeishuCollector(BaseCollector):
    """Collect Feishu data via API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get("app_id")
        self.app_secret = config.get("app_secret")
        self.user_email = config.get("user_email")
        self.tenant_access_token = None
        
        if not self.app_id or not self.app_secret:
            raise CollectorError("Feishu app_id and app_secret required")
    
    def validate(self) -> bool:
        """Validate Feishu API access"""
        try:
            self._get_tenant_access_token()
            return True
        except Exception as e:
            raise CollectorError(f"Failed to validate Feishu API: {e}")
    
    def collect(self) -> Dict[str, Any]:
        """Collect Feishu messages and documents"""
        if not self.validate():
            raise CollectorError("Feishu API validation failed")
        
        # Get tenant access token
        self._get_tenant_access_token()
        
        user_id = self._get_user_id()
        
        if not user_id:
            raise CollectorError("Failed to get user ID")
        
        # Collect data
        messages = self._collect_messages(user_id)
        docs = self._collect_docs(user_id)
        
        self.collected_data["messages"] = messages
        self.collected_data["documents"] = docs
        self.collected_data["metadata"] = {
            "source": "feishu",
            "collected_at": datetime.now().isoformat(),
            "total_messages": len(messages),
            "total_docs": len(docs),
            "user_email": self.user_email
        }
        
        return self.collected_data
    
    def _get_tenant_access_token(self) -> str:
        """Get tenant access token"""
        if self.tenant_access_token:
            return self.tenant_access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") != 0:
            raise CollectorError(f"Failed to get tenant access token: {data}")
        
        self.tenant_access_token = data["tenant_access_token"]
        return self.tenant_access_token
    
    def _get_user_id(self) -> Optional[str]:
        """Get user ID from email"""
        if not self.user_email:
            return None
        
        url = f"https://open.feishu.cn/open-apis/contact/v3/users/get_by_email"
        params = {"emails": self.user_email}
        headers = {"Authorization": f"Bearer {self.tenant_access_token}"}
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") == 0 and data.get("data", {}).get("user_list"):
            return data["data"]["user_list"][0]["user_id"]
        
        return None
    
    def _collect_messages(self, user_id: str) -> List[Dict[str, Any]]:
        """Collect user messages"""
        messages = []
        
        # Get chat list
        chat_list = self._get_chat_list(user_id)
        
        for chat in chat_list:
            chat_id = chat.get("chat_id")
            if not chat_id:
                continue
            
            # Get messages from this chat
            chat_messages = self._get_chat_messages(chat_id, user_id)
            messages.extend(chat_messages)
        
        # Sort by timestamp
        messages.sort(key=lambda x: x.get("timestamp", ""))
        return messages
    
    def _get_chat_list(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's chat list"""
        # TODO: Implement chat list retrieval
        return []
    
    def _get_chat_messages(self, chat_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get messages from a chat"""
        # TODO: Implement message retrieval
        return []
    
    def _collect_docs(self, user_id: str) -> List[Dict[str, Any]]:
        """Collect user documents"""
        # TODO: Implement document retrieval
        return []


# Feishu MCP format (model context protocol)
class FeishuMCPCollector(FeishuCollector):
    """Collector using Feishu MCP protocol"""
    pass
