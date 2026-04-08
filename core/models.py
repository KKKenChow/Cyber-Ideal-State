"""
Core data models for CyberRepublic
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class RoleType(Enum):
    """Role type classification"""
    EX_PARTNER = "ex-partner"
    COLLEAGUE = "colleague"
    FAMILY = "family"
    FRIEND = "friend"
    OTHER = "other"


class Tier(Enum):
    """Tier classification (Plato's ideal classes)"""
    PHILOSOPHER = "philosopher"  # Philosopher King
    GUARDIAN = "guardian"        # Guardian
    WORKER = "worker"            # Worker


@dataclass
class Persona:
    """Agent personality structure"""
    mbti: Optional[str] = None
    zodiac: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    attachment_style: Optional[str] = None
    love_language: Optional[str] = None
    speaking_style: Dict[str, Any] = field(default_factory=dict)
    emotional_pattern: Dict[str, Any] = field(default_factory=dict)
    decision_mode: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Memory:
    """Agent memory structure"""
    shared_experiences: List[str] = field(default_factory=list)
    decision_history: List[Dict[str, Any]] = field(default_factory=list)
    inside_jokes: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    relationship_insights: List[str] = field(default_factory=list)


@dataclass
class AgentConfig:
    """Agent runtime configuration"""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 300
    system_prompt: Optional[str] = None


@dataclass
class DataSource:
    """Data source specification"""
    type: str  # wechat, qq, feishu, dingtalk, email, social, photo
    path: Optional[str] = None
    credentials: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Role:
    """Role/Agent definition"""
    id: str
    name: str
    type: RoleType
    tier: Tier
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Core components
    persona: Optional[Persona] = None
    memory: Optional[Memory] = None
    agent_config: Optional[AgentConfig] = None
    
    # Data sources
    sources: List[DataSource] = field(default_factory=list)
    
    # Status
    active: bool = True
    agent_id: Optional[str] = None  # OpenClaw agent ID
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "tier": self.tier.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "persona": self.persona.__dict__ if self.persona else None,
            "memory": self.memory.__dict__ if self.memory else None,
            "agent_config": self.agent_config.__dict__ if self.agent_config else None,
            "sources": [s.__dict__ for s in self.sources],
            "active": self.active,
            "agent_id": self.agent_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """Create Role from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            type=RoleType(data["type"]),
            tier=Tier(data["tier"]),
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            persona=Persona(**data["persona"]) if data.get("persona") else None,
            memory=Memory(**data["memory"]) if data.get("memory") else None,
            agent_config=AgentConfig(**data["agent_config"]) if data.get("agent_config") else None,
            sources=[DataSource(**s) for s in data.get("sources", [])],
            active=data.get("active", True),
            agent_id=data.get("agent_id")
        )


@dataclass
class Session:
    """Conversation session"""
    id: str
    name: str
    participants: List[Dict[str, str]]
    speaking_mode: str
    decision_mode: str
    mode: Tier  # Overall session mode based on participants (for backwards compatibility)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "participants": self.participants,
            "speaking_mode": self.speaking_mode,
            "decision_mode": self.decision_mode,
            "mode": self.mode.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": self.messages,
            "active": self.active
        }


@dataclass
class Decision:
    """Multi-agent decision record"""
    id: str
    topic: str
    participants: List[str]  # Role IDs
    mode: str  # vote, debate, consensus
    weights: Dict[str, float]  # Role ID -> weight
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Decision process
    votes: Dict[str, Any] = field(default_factory=dict)
    debate_history: List[Dict[str, Any]] = field(default_factory=list)
    final_decision: Optional[str] = None
    confidence: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "participants": self.participants,
            "mode": self.mode,
            "weights": self.weights,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "votes": self.votes,
            "debate_history": self.debate_history,
            "final_decision": self.final_decision,
            "confidence": self.confidence
        }
