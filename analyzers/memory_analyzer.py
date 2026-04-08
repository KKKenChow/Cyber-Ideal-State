"""
Memory analyzer - extract significant memories from messages
"""
from typing import Dict, Any, List, Optional
from analyzers.base import BaseAnalyzer
from core.models import Memory


class MemoryAnalyzer(BaseAnalyzer):
    """Analyze and extract significant memories from collected data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.llm = config.get("llm", None)  # LLM client
    
    def analyze(self, data: Dict[str, Any]) -> Memory:
        """Analyze collected data and extract memories"""
        messages = data.get("messages", [])
        images = data.get("images", [])
        
        memory = Memory()
        
        # Extract basic timeline
        self._extract_basic_timeline(memory, messages, images)
        
        # Extract shared experiences using LLM if available
        if self.llm and len(messages) > 10:
            self._extract_significant_events(memory, messages)
        
        return memory
    
    def _extract_basic_timeline(self, memory: Memory, messages: List[Dict[str, Any]], images: List[Dict[str, Any]]):
        """Extract basic timeline from messages and images"""
        # Add messages to timeline by date
        from collections import defaultdict
        messages_by_date = defaultdict(list)
        
        for msg in messages:
            timestamp = msg.get("timestamp", "")
            if timestamp:
                date = timestamp.split("T")[0] if "T" in timestamp else timestamp.split(" ")[0]
                messages_by_date[date].append(msg)
        
        # High volume dates are likely significant
        for date, date_messages in sorted(messages_by_date.items(), key=lambda x: len(x[1]), reverse=True):
            if len(date_messages) > 20:  # More than 20 messages in one day = significant
                memory.shared_experiences.append(f"{date} 有频繁互动，共 {len(date_messages)} 条消息")
        
        # Add photos to timeline
        for img in images:
            event = {
                "type": "photo",
                "timestamp": img.get("timestamp"),
                "location": img.get("location"),
                "description": img.get("description", "照片")
            }
            memory.timeline.append(event)
        
        # Sort timeline
        memory.timeline.sort(key=lambda x: x.get("timestamp", ""))
    
    def _extract_significant_events(self, memory: Memory, messages: List[Dict[str, Any]]):
        """Extract significant shared experiences using LLM"""
        if not self.llm:
            return
        
        # Group messages by conversation context
        # Take the most significant conversations for analysis
        from collections import defaultdict
        messages_by_date = defaultdict(list)
        
        for msg in messages:
            timestamp = msg.get("timestamp", "")
            if timestamp:
                date = timestamp.split("T")[0] if "T" in timestamp else timestamp.split(" ")[0]
                messages_by_date[date].append(msg)
        
        # Analyze top 5 dates with most messages
        top_dates = sorted(messages_by_date.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        
        for date, date_messages in top_dates:
            # Only analyze if we have enough messages
            if len(date_messages) < 5:
                continue
            
            # Sample messages
            sample = date_messages[-15:]  # Last 15 messages from this date
            prompt = self._build_extraction_prompt(date, sample)
            
            try:
                response = self.llm.complete(prompt)
                self._parse_extraction_response(memory, date, response)
            except Exception as e:
                print(f"Failed to extract events for {date}: {e}")
    
    def _build_extraction_prompt(self, date: str, messages: List[Dict[str, Any]]) -> str:
        """Build prompt for memory extraction"""
        prompt = f"""请查看以下日期 {date} 的聊天记录，从中提取：
1. 你们讨论的主要话题是什么？
2. 是否有重要的共同事件（约会、聚会、旅行、重要决定等）？
3. 是否有你们之间的笑话或梗？

请用JSON格式输出：
{{
  "topic": "主要话题描述",
  "significant_event": null 或 事件描述,
  "inside_jokes": ["梗1", "梗2"]
}}

聊天记录：
"""
        
        for msg in messages:
            content = msg.get("content", "")
            if len(content) > 150:
                content = content[:150] + "..."
            is_self = msg.get("is_self", False)
            speaker = "Me" if is_self else "Other"
            prompt += f"\n{speaker}: {content}\n"
        
        return prompt
    
    def _parse_extraction_response(self, memory: Memory, date: str, response: str):
        """Parse LLM response and add to memory"""
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                if data.get("significant_event"):
                    event = f"{date}: {data['significant_event']}"
                    if event not in memory.shared_experiences:
                        memory.shared_experiences.append(event)
                
                if data.get("inside_jokes"):
                    for joke in data["inside_jokes"]:
                        joke_with_date = f"{date}: {joke}"
                        if joke_with_date not in memory.inside_jokes:
                            memory.inside_jokes.append(joke_with_date)
        
        except Exception as e:
            print(f"Failed to parse extraction response: {e}")
    
    def extract_relationship_insights(self, memory: Memory, messages: List[Dict[str, Any]]):
        """Extract relationship insights"""
        if not self.llm or not messages:
            return []
        
        prompt = """Based on the following chat history between two people, provide insights about their relationship:
- What is the nature of this relationship?
- What are the typical interaction patterns?
- What important things should be remembered about this relationship?

Keep it concise, 3-5 bullet points.
"""
        
        # Sample messages
        import random
        sample = random.sample(messages, min(30, len(messages)))
        for msg in sample:
            content = msg.get("content", "")[:100]
            prompt += f"\n- {content}\n"
        
        try:
            response = self.llm.complete(prompt)
            # Split into insights
            insights = []
            for line in response.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*"):
                    insights.append(line[1:].strip())
                elif line and len(line) > 10:
                    insights.append(line)
            
            return insights[:5]
        except Exception as e:
            print(f"Failed to extract relationship insights: {e}")
            return []
