"""
Relationship analyzer - analyze relationship patterns between users
"""
from typing import Dict, Any, List, Optional
from analyzers.base import BaseAnalyzer


class RelationshipAnalyzer(BaseAnalyzer):
    """Analyze relationship patterns from interaction history"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.llm = config.get("llm", None)
    
    def analyze(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze relationship from interaction history"""
        results = {
            "interaction_frequency": self._calculate_frequency(messages),
            "initiation_pattern": self._calculate_initiation(messages),
            "response_time": self._calculate_response_time(messages),
            "topic_distribution": self._calculate_topics(messages),
            "insights": []
        }
        
        if self.llm and len(messages) > 20:
            results["insights"] = self._get_llm_insights(messages)
        
        return results
    
    def _calculate_frequency(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate interaction frequency"""
        if not messages:
            return {"total": 0}
        
        from collections import defaultdict
        from datetime import datetime
        
        messages_by_day = defaultdict(int)
        
        for msg in messages:
            timestamp = msg.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    date_key = dt.date().isoformat()
                    messages_by_day[date_key] += 1
                except:
                    pass
        
        total = len(messages)
        days = len(messages_by_day)
        avg_per_day = total / days if days > 0 else 0
        
        return {
            "total_messages": total,
            "active_days": days,
            "avg_messages_per_day": round(avg_per_day, 2)
        }
    
    def _calculate_initiation(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate who initiates conversations"""
        if not messages:
            return {}
        
        from collections import defaultdict
        
        initiations = defaultdict(int)
        total_conversations = 0
        
        # A new conversation starts after 4 hours of silence
        from datetime import datetime
        
        last_timestamp = None
        for msg in sorted(messages, key=lambda x: x.get("timestamp", "")):
            timestamp = msg.get("timestamp", "")
            if not timestamp:
                continue
            
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                
                if last_timestamp is None or (dt - last_timestamp).total_seconds() > 14400:  # 4 hours
                    sender = msg.get("sender", "unknown")
                    initiations[sender] += 1
                    total_conversations += 1
                
                last_timestamp = dt
            except:
                continue
        
        return {
            "initiations": dict(initiations),
            "total_conversations": total_conversations
        }
    
    def _calculate_response_time(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate average response time between turns"""
        if len(messages) < 2:
            return {}
        
        from collections import defaultdict
        from datetime import datetime
        
        response_times = defaultdict(list)
        sorted_messages = sorted(messages, key=lambda x: x.get("timestamp", ""))
        
        for i in range(1, len(sorted_messages)):
            prev_msg = sorted_messages[i-1]
            curr_msg = sorted_messages[i]
            
            # Different sender = response
            if prev_msg.get("sender") != curr_msg.get("sender"):
                try:
                    prev_dt = datetime.fromisoformat(prev_msg.get("timestamp", "").replace("Z", "+00:00"))
                    curr_dt = datetime.fromisoformat(curr_msg.get("timestamp", "").replace("Z", "+00:00"))
                    
                    response_sec = (curr_dt - prev_dt).total_seconds()
                    sender = curr_msg.get("sender", "unknown")
                    
                    # Only include reasonable response times (less than 24h)
                    if response_sec < 86400:
                        response_times[sender].append(response_sec)
                except:
                    continue
        
        # Calculate averages
        avg_times = {}
        for sender, times in response_times.items():
            if times:
                avg = sum(times) / len(times)
                avg_times[sender] = {
                    "avg_seconds": round(avg, 0),
                    "avg_minutes": round(avg / 60, 1),
                    "sample_size": len(times)
                }
        
        return avg_times
    
    def _calculate_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Simple topic extraction based on keyword frequency"""
        if not messages:
            return []
        
        # Chinese stop words
        stop_words = set([
            "的", "是", "了", "在", "我", "你", "他", "她", "它", "们", "就", "都",
            "要", "会", "可以", "这个", "那个", "这样", "那样", "什么", "有", "没有",
            "好", "不好", "哦", "嗯", "啊", "呀", "呢", "吧", "哈", "呵呵", "哈哈"
        ])
        
        import re
        word_counts = {}
        
        for msg in messages:
            content = msg.get("content", "")
            # Split into words (simple Chinese character splitting)
            words = re.findall(r'[\w]{2,}|[\u4e00-\u9fa5]{2,}', content)
            
            for word in words:
                if len(word) >= 2 and word not in stop_words:
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top keywords
        sorted_words = sorted(word_counts.keys(), key=lambda w: word_counts[w], reverse=True)
        return sorted_words[:10]
    
    def _get_llm_insights(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Get relationship insights from LLM"""
        if not self.llm:
            return []
        
        # Sample messages
        import random
        sample = random.sample(messages, min(20, len(messages)))
        
        prompt = """请分析这段聊天记录中的两个人的关系模式：
1. 他们之间的互动模式是怎样的？
2. 关系的亲密度如何？
3. 有哪些需要注意的互动特点？

请给出3-5条简洁的洞察，每条一句话。
"""
        
        for msg in sample:
            content = msg.get("content", "")[:100]
            sender = msg.get("sender", "unknown")
            prompt += f"\n{sender}: {content}\n"
        
        try:
            response = self.llm.complete(prompt)
            insights = []
            for line in response.split("\n"):
                line = line.strip()
                if (line.startswith("-") or line.startswith("*") or line.startswith("1.") or line.startswith("2.") or line.startswith("3.")):
                    # Remove number/bullet
                    insight = line.split(".", 1)[-1].strip() if "." in line else line[1:].strip()
                    if insight:
                        insights.append(insight)
            
            return insights[:5]
        except Exception as e:
            print(f"Failed to get LLM insights: {e}")
            return []
