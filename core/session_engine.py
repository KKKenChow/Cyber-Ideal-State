"""
Session Engine - manage conversations with one or multiple agents

SessionEngine handles session lifecycle and message flow.
For vote/debate/consensus modes, it delegates the actual decision
logic to DecisionEngine and stores the results in both the session
messages and the decisions directory.
"""
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.models import Session, Tier, Role
from core.decision_engine import DecisionEngine


class SessionEngine:
    """Engine for managing conversations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sessions_dir = config.get("sessions_dir", "data/sessions")
        self.decision_engine = DecisionEngine(config)
    
    def create_session(
        self,
        name: str,
        participants: List[Dict[str, Any]],  # List of {role_id, tier, role_name?}
        decision_mode: str = "chat",
        speaking_mode: str = "free"  # free | turn_based | debate | vote | consensus
    ) -> Session:
        """Create a new session with multiple participants"""
        session_id = str(uuid.uuid4())[:8]
        
        # Determine session mode based on participants
        if len(participants) == 1:
            session_tier = Tier(participants[0]["tier"])
        else:
            tiers = set(p["tier"] for p in participants)
            if tiers == {"philosopher", "guardian", "worker"}:
                session_tier = Tier("philosopher")  # Ideal State mode
            else:
                session_tier = Tier("worker")  # Default to worker for multi-chat
        
        session = Session(
            id=session_id,
            name=name,
            participants=participants,
            speaking_mode=speaking_mode,
            decision_mode=decision_mode,
            mode=session_tier,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            active=True
        )
        
        # Store participants and configuration in messages as metadata
        session.messages = [{
            "role": "system",
            "content": f"Session configuration",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "session_name": name,
                "participants": participants,
                "decision_mode": decision_mode,
                "speaking_mode": speaking_mode
            }
        }]
        
        return session
    
    def send_message(
        self,
        session_id: str,
        user_message: str,
        openclaw_api
    ) -> Dict[str, Any]:
        """Send a message to session and get responses"""
        session = self._load_session(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        config = self._get_session_config(session)
        
        # Add user message
        session.messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get responses based on mode
        responses = []
        
        if config["speaking_mode"] == "free":
            responses = self._free_discussion(session, user_message, openclaw_api)
        elif config["speaking_mode"] == "turn_based":
            responses = self._turn_based(session, user_message, openclaw_api)
        elif config["speaking_mode"] == "debate":
            responses = self._debate_mode(session, user_message, openclaw_api)
        elif config["speaking_mode"] == "vote":
            responses = self._vote_mode(session, user_message, openclaw_api)
        elif config["speaking_mode"] == "consensus":
            responses = self._consensus_mode(session, user_message, openclaw_api)
        
        # Add responses to session
        for response in responses:
            msg = {
                "role": "assistant",
                "content": response["content"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Add metadata if available
            if "role_id" in response:
                msg["metadata"] = {
                    "role_id": response["role_id"],
                    "role_name": response.get("role_name", response["role_id"])
                }
            
            # Add other metadata fields (like vote result, decision info)
            for key in ["type", "result", "votes", "yes_count", "no_count", "round",
                        "confidence", "decision_id", "consensus_reached", "proposal",
                        "debate_rounds"]:
                if key in response:
                    if "metadata" not in msg:
                        msg["metadata"] = {}
                    msg["metadata"][key] = response[key]
            
            session.messages.append(msg)
        
        # Save session
        self._save_session(session)
        
        return {
            "session_id": session_id,
            "user_message": user_message,
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_session_config(self, session: Session) -> Dict[str, Any]:
        """Extract session configuration from metadata"""
        for msg in session.messages:
            if msg.get("role") == "system" and "metadata" in msg:
                return msg["metadata"]
        
        return {
            "participants": [],
            "decision_mode": "chat",
            "speaking_mode": "free"
        }
    
    def _free_discussion(
        self,
        session: Session,
        user_message: str,
        openclaw_api
    ) -> List[Dict[str, Any]]:
        """Free discussion mode - all participants respond"""
        config = self._get_session_config(session)
        responses = []
        
        for participant in config["participants"]:
            agent_response = self._send_to_agent(
                participant["role_id"],
                user_message,
                openclaw_api
            )
            
            responses.append({
                "role_id": participant["role_id"],
                "role_name": participant.get("role_name", participant["role_id"]),
                "content": agent_response
            })
        
        return responses
    
    def _turn_based(
        self,
        session: Session,
        user_message: str,
        openclaw_api
    ) -> List[Dict[str, Any]]:
        """Turn-based mode - participants respond in order"""
        config = self._get_session_config(session)
        responses = []
        
        message_count = len([m for m in session.messages if m.get("role") == "assistant"])
        participants = config["participants"]
        
        if len(participants) > 0:
            current_index = message_count % len(participants)
            current_participant = participants[current_index]
            
            agent_response = self._send_to_agent(
                current_participant["role_id"],
                user_message,
                openclaw_api
            )
            
            responses.append({
                "role_id": current_participant["role_id"],
                "role_name": current_participant.get("role_name", current_participant["role_id"]),
                "content": agent_response
            })
        
        return responses
    
    def _debate_mode(
        self,
        session: Session,
        user_message: str,
        openclaw_api,
        rounds: int = 3
    ) -> List[Dict[str, Any]]:
        """Debate mode - delegates to DecisionEngine for structured debate"""
        config = self._get_session_config(session)
        
        # Create and execute decision via DecisionEngine
        decision = self.decision_engine.create_decision(
            topic=user_message,
            participants=config["participants"],
            mode="debate",
            session_id=session.id
        )
        
        result = self.decision_engine.debate(decision, rounds=rounds, openclaw_api=openclaw_api)
        self.decision_engine.save_decision(decision)
        
        # Convert debate result to session message format
        responses = []
        
        # Add individual debate messages from each round
        for round_data in decision.debate_history:
            for msg in round_data.get("messages", []):
                responses.append({
                    "role_id": msg["participant"],
                    "role_name": msg.get("role_name", msg["participant"]),
                    "content": msg["message"],
                    "round": round_data["round"],
                    "type": "debate_message",
                    "decision_id": decision.id
                })
        
        # Add summary as final message
        responses.append({
            "type": "debate_result",
            "content": result.get("summary", result.get("decision", "Debate completed")),
            "confidence": result.get("confidence"),
            "decision_id": decision.id,
            "debate_rounds": rounds
        })
        
        return responses
    
    def _vote_mode(
        self,
        session: Session,
        user_message: str,
        openclaw_api
    ) -> List[Dict[str, Any]]:
        """Vote mode - delegates to DecisionEngine for weighted voting"""
        config = self._get_session_config(session)
        
        # Create and execute decision via DecisionEngine
        decision = self.decision_engine.create_decision(
            topic=user_message,
            participants=config["participants"],
            mode="vote",
            session_id=session.id
        )
        
        result = self.decision_engine.vote(decision, openclaw_api)
        self.decision_engine.save_decision(decision)
        
        # Convert to session message format (compatible with existing ChatPanel)
        yes_count = sum(1 for v in decision.votes.values() if v["vote"] == "YES")
        no_count = sum(1 for v in decision.votes.values() if v["vote"] == "NO")
        
        # Build votes dict in the format ChatPanel expects
        votes_for_panel = {}
        for pid, v in decision.votes.items():
            votes_for_panel[pid] = {
                "vote": v["vote"],
                "reason": v.get("reason", ""),
                "weight": v.get("weight", 1.0),
                "role_name": v.get("role_name", pid)
            }
        
        return [{
            "type": "vote_result",
            "result": result["decision"],
            "votes": votes_for_panel,
            "yes_count": yes_count,
            "no_count": no_count,
            "confidence": result.get("confidence"),
            "content": f"Vote result: {result['decision']} (YES: {yes_count}, NO: {no_count}, Confidence: {result.get('confidence', 'N/A')})",
            "decision_id": decision.id
        }]
    
    def _consensus_mode(
        self,
        session: Session,
        user_message: str,
        openclaw_api,
        max_rounds: int = 3
    ) -> List[Dict[str, Any]]:
        """Consensus mode - delegates to DecisionEngine for consensus building"""
        config = self._get_session_config(session)
        
        # Create and execute decision via DecisionEngine
        decision = self.decision_engine.create_decision(
            topic=user_message,
            participants=config["participants"],
            mode="consensus",
            session_id=session.id
        )
        
        result = self.decision_engine.consensus(decision, max_rounds=max_rounds, openclaw_api=openclaw_api)
        self.decision_engine.save_decision(decision)
        
        # Convert to session message format
        if result.get("consensus_reached"):
            return [{
                "type": "consensus_result",
                "result": "CONSENSUS",
                "proposal": result.get("proposal", result.get("final_decision")),
                "rounds": result.get("rounds"),
                "confidence": result.get("confidence"),
                "consensus_reached": True,
                "content": f"Consensus reached after {result['rounds']} rounds: {result.get('proposal', result.get('final_decision'))}",
                "decision_id": decision.id
            }]
        else:
            # Fell back to vote - include vote result
            yes_count = sum(1 for v in decision.votes.values() if v["vote"] == "YES")
            no_count = sum(1 for v in decision.votes.values() if v["vote"] == "NO")
            
            votes_for_panel = {}
            for pid, v in decision.votes.items():
                votes_for_panel[pid] = {
                    "vote": v["vote"],
                    "reason": v.get("reason", ""),
                    "weight": v.get("weight", 1.0),
                    "role_name": v.get("role_name", pid)
                }
            
            return [{
                "type": "consensus_fallback_vote",
                "result": result.get("final_decision"),
                "votes": votes_for_panel,
                "yes_count": yes_count,
                "no_count": no_count,
                "confidence": result.get("confidence"),
                "consensus_reached": False,
                "content": f"Consensus not reached after {result['rounds']} rounds. Fallback vote: {result.get('final_decision')} (YES: {yes_count}, NO: {no_count})",
                "decision_id": decision.id
            }]
    
    def _send_to_agent(
        self,
        agent_id: str,
        message: str,
        openclaw_api
    ) -> str:
        """Send message to an agent via OpenClaw"""
        if openclaw_api is None:
            return f"[⚠️ OpenClaw API not connected. Please configure OpenClaw to enable real agent responses.\n\nAgent {agent_id} received message: {message[:100]}...]"
        
        try:
            response = openclaw_api.send_message(agent_id, message)
            return response
        except Exception as e:
            print(f"Failed to get response from agent {agent_id}: {e}")
            return f"[Error from agent {agent_id}: {str(e)}]"
    
    def _load_session(self, session_id: str) -> Optional[Session]:
        """Load session from disk"""
        import os
        filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            # Backwards compatibility
            if 'participants' not in data:
                participants = [{
                    'role_id': data['role_id'],
                    'role_name': 'Unknown',
                    'tier': data['mode']
                }]
            else:
                participants = data.get('participants', [])
            
            return Session(
                id=data["id"],
                name=data.get("name", f"Session {data['id']}"),
                participants=participants,
                speaking_mode=data.get("speaking_mode", "free"),
                decision_mode=data.get("decision_mode", "chat"),
                mode=Tier(data["mode"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                messages=data.get("messages", []),
                active=data.get("active", True)
            )
        except Exception as e:
            print(f"Failed to load session: {e}")
            return None
    
    def _save_session(self, session: Session):
        """Save session to disk"""
        import os
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        filepath = os.path.join(self.sessions_dir, f"{session.id}.json")
        
        session.updated_at = datetime.now()
        
        with open(filepath, "w") as f:
            json.dump(session.to_dict(), f, indent=2)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Session engine CLI")
    parser.add_argument("--test", action="store_true", help="Test session engine")
    
    args = parser.parse_args()
    
    if args.test:
        config = {"sessions_dir": "data/sessions"}
        engine = SessionEngine(config)
        
        session = engine.create_session(
            name="Test Session",
            participants=[
                {"role_id": "test-001", "tier": "philosopher"},
                {"role_id": "test-002", "tier": "worker"}
            ],
            decision_mode="chat",
            speaking_mode="free"
        )
        
        print(f"Created session: {session.id}")
        print(f"Config: {engine._get_session_config(session)}")


if __name__ == "__main__":
    main()
