"""
Persona analyzer - extract personality characteristics from messages
"""
from typing import Dict, Any, List, Optional
from analyzers.base import BaseAnalyzer
from core.models import Persona


class PersonaAnalyzer(BaseAnalyzer):
    """Analyze personality from collected data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.llm = config.get("llm", None)  # LLM client (OpenClaw)
    
    def analyze(self, data: Dict[str, Any]) -> Persona:
        """Analyze collected data and extract persona"""
        messages = data.get("messages", [])
        documents = data.get("documents", [])
        
        persona = Persona()
        
        if not messages:
            return persona
        
        # Extract basic patterns without LLM
        self._extract_basic_patterns(persona, messages)
        
        # If LLM is available, do deep analysis
        if self.llm:
            self._deep_analyze_with_llm(persona, messages, documents)
        
        return persona
    
    def _extract_basic_patterns(self, persona: Persona, messages: List[Dict[str, Any]]):
        """Extract basic patterns from messages"""
        # Calculate average message length
        if not messages:
            return
        
        total_length = sum(len(msg.get("content", "")) for msg in messages)
        avg_length = total_length / len(messages)
        
        # Add tags based on message length
        if avg_length > 100:
            persona.tags.append("话痨")
        elif avg_length < 20:
            persona.tags.append("简洁")
        
        # Detect frequency patterns
        # Count messages by time of day
        from collections import defaultdict
        time_counts = defaultdict(int)
        
        for msg in messages:
            timestamp = msg.get("timestamp", "")
            if timestamp:
                try:
                    # Parse hour from timestamp
                    if "T" in timestamp:
                        hour = int(timestamp.split("T")[1].split(":")[0])
                    else:
                        hour = int(timestamp.split(" ")[1].split(":")[0])
                    
                    if 5 <= hour < 12:
                        time_counts["morning"] += 1
                    elif 12 <= hour < 18:
                        time_counts["afternoon"] += 1
                    elif 18 <= hour < 22:
                        time_counts["evening"] += 1
                    else:
                        time_counts["night"] += 1
                except:
                    pass
        
        # Most active time
        if time_counts:
            max_time = max(time_counts.keys(), key=lambda k: time_counts[k])
            persona.speaking_style["active_time"] = max_time
        
        # Detect emoji usage
        import re
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            "]+",
            flags=re.UNICODE
        )
        
        total_emojis = 0
        for msg in messages:
            content = msg.get("content", "")
            emojis = emoji_pattern.findall(content)
            total_emojis += len(emojis)
        
        emoji_ratio = total_emojis / len(messages)
        if emoji_ratio > 0.5:
            persona.tags.append("爱用表情")
            persona.emotional_pattern["emoji_usage"] = "high"
        elif emoji_ratio > 0.1:
            persona.emotional_pattern["emoji_usage"] = "medium"
        else:
            persona.emotional_pattern["emoji_usage"] = "low"
    
    def _deep_analyze_with_llm(self, persona: Persona, messages: List[Dict[str, Any]], documents: List[Dict[str, Any]]):
        """Use LLM for deep persona analysis"""
        if not self.llm:
            return
        
        # Sample messages to avoid token overflow
        sample_size = min(50, len(messages))
        import random
        sampled_messages = random.sample(messages, sample_size)
        
        # Format prompt for LLM
        prompt = self._build_analysis_prompt(sampled_messages, documents)
        
        try:
            response = self.llm.complete(prompt)
            self._parse_llm_response(persona, response)
        except Exception as e:
            print(f"LLM analysis failed: {e}")
    
    def _build_analysis_prompt(self, messages: List[Dict[str, Any]], documents: List[Dict[str, Any]]) -> str:
        """Build analysis prompt for LLM"""
        prompt = """请分析以下聊天记录，提取这个人的性格特征。

分析要求：
1. 给出最合适的MBTI类型（如果不确定可以给出最可能的）
2. 给出3-5个性格标签
3. 描述他/她的说话风格
4. 描述他/她的情感模式

请用JSON格式输出，格式如下：
{
  "mbti": "ENFP",
  "tags": ["浪漫", "话痨", "感性"],
  "speaking_style": {
    "avg_length": "long",
    "formality": "informal",
    "humor": "high"
  },
  "emotional_pattern": {
    "expressiveness": "high",
    "logic_first": false
  }
}

聊天记录样本：
"""
        
        for i, msg in enumerate(messages[-20:]):  # Last 20 messages
            content = msg.get("content", "")
            if len(content) > 200:
                content = content[:200] + "..."
            prompt += f"\n{i+1}. {content}\n"
        
        return prompt
    
    def _parse_llm_response(self, persona: Persona, response: str):
        """Parse LLM response into persona object"""
        import json
        import re
        
        # Extract JSON from response
        try:
            # Find JSON block
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                if data.get("mbti"):
                    persona.mbti = data["mbti"].upper()
                
                if data.get("tags"):
                    existing_tags = set(persona.tags)
                    for tag in data["tags"]:
                        existing_tags.add(tag)
                    persona.tags = list(existing_tags)
                
                if data.get("speaking_style"):
                    persona.speaking_style.update(data["speaking_style"])
                
                if data.get("emotional_pattern"):
                    persona.emotional_pattern.update(data["emotional_pattern"])
        
        except Exception as e:
            print(f"Failed to parse LLM response: {e}")
