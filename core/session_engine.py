"""
Session Engine - manage conversations with one or multiple agents
"""
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.models import Session, Tier, Role


class SessionEngine:
    """Engine for managing conversations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sessions_dir = config.get("sessions_dir", "data/sessions")
    
    def create_session(
        self,
        name: str,
        participants: List[Dict[str, Any]],  # List of {role_id, tier}
        decision_mode: str = "chat",
        speaking_mode: str = "free"  # free | turn_based | debate | vote | consensus
    ) -> Session:
        """Create a new session with multiple participants"""
        session_id = str(uuid.uuid4())[:8]
        
        # Determine session mode based on participants
        if len(participants) == 1:
            # Single participant session
            session_tier = Tier(participants[0]["tier"])
        else:
            # Multi-participant session
            # Check if we have all three tiers
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
        # Load session
        session = self._load_session(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        # Get session config
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
                    "role_name": response["role_name"]
                }
            
            # Add other metadata fields (like vote result)
            for key in ["type", "result", "votes", "yes_count", "no_count", "round"]:
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
        # Find system message with config
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
            # Send message to each agent
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
        
        # Determine whose turn it is
        message_count = len([m for m in session.messages if m.get("role") == "assistant"])
        participants = config["participants"]
        
        # Get next participant
        if len(participants) > 0:
            current_index = message_count % len(participants)
            current_participant = participants[current_index]
            
            # Get response
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
        rounds: int = 2
    ) -> List[Dict[str, Any]]:
        """Debate mode - multiple rounds of discussion"""
        config = self._get_session_config(session)
        all_responses = []
        
        for round_num in range(rounds):
            responses = self._free_discussion(session, user_message, openclaw_api)
            
            # Add round info
            for resp in responses:
                resp["round"] = round_num + 1
            
            all_responses.extend(responses)
            
            # For debate, update user_message to include previous responses
            # This creates a chain of responses
            if round_num < rounds - 1:
                user_message = f"Previous responses: {[r['content'] for r in responses]}"
        
        return all_responses
    
    def _vote_mode(
        self,
        session: Session,
        user_message: str,
        openclaw_api
    ) -> List[Dict[str, Any]]:
        """Vote mode - participants vote on the issue"""
        config = self._get_session_config(session)
        votes = {}
        
        # Collect votes from all participants
        for participant in config["participants"]:
            # Ask agent to vote
            vote_prompt = f"The question is: {user_message}\n\nPlease respond with your vote (YES/NO/ABSTAIN) and a brief reason."
            
            response = self._send_to_agent(
                participant["role_id"],
                vote_prompt,
                openclaw_api
            )
            
            # Extract vote
            vote = "ABSTAIN"
            if "YES" in response.upper():
                vote = "YES"
            elif "NO" in response.upper():
                vote = "NO"
            
            votes[participant["role_id"]] = {
                "vote": vote,
                "reason": response,
                "role_name": participant.get("role_name", participant["role_id"])
            }
        
        # Calculate result
        yes_count = sum(1 for v in votes.values() if v["vote"] == "YES")
        no_count = sum(1 for v in votes.values() if v["vote"] == "NO")
        
        if yes_count > no_count:
            result = "YES"
        elif no_count > yes_count:
            result = "NO"
        else:
            result = "TIE"
        
        return [{
            "type": "vote_result",
            "result": result,
            "votes": votes,
            "yes_count": yes_count,
            "no_count": no_count,
            "content": f"Vote result: {result} (YES: {yes_count}, NO: {no_count})"
        }]
    
    def _consensus_mode(
        self,
        session: Session,
        user_message: str,
        openclaw_api,
        max_rounds: int = 3
    ) -> List[Dict[str, Any]]:
        """Consensus mode - try to reach consensus, fall back to vote"""
        config = self._get_session_config(session)
        
        # Start with a proposal
        current_proposal = self._generate_initial_proposal(user_message, openclaw_api)
        
        for round_num in range(max_rounds):
            # Get feedback from all participants
            feedback = []
            for participant in config["participants"]:
                prompt = f"The current proposal is: {current_proposal}\n\nThe original question was: {user_message}\n\nDo you agree? (YES/NO) and why?"
                
                response = self._send_to_agent(
                    participant["role_id"],
                    prompt,
                    openclaw_api
                )
                
                agrees = "YES" in response.upper()
                feedback.append({
                    "role_id": participant["role_id"],
                    "role_name": participant.get("role_name", participant["role_id"]),
                    "agrees": agrees,
                    "response": response
                })
            
            # Check if consensus reached
            if all(f["agrees"] for f in feedback):
                return [{
                    "type": "consensus_result",
                    "result": "CONSENSUS",
                    "proposal": current_proposal,
                    "rounds": round_num + 1,
                    "content": f"Consensus reached after {round_num + 1} rounds: {current_proposal}"
                }]
            
            # Update proposal based on feedback
            current_proposal = self._update_proposal(current_proposal, feedback, openclaw_api)
        
        # No consensus, fall back to vote
        return self._vote_mode(session, user_message, openclaw_api)
    
    def _send_to_agent(
        self,
        agent_id: str,
        message: str,
        openclaw_api
    ) -> str:
        """Send message to an agent via OpenClaw"""
        if openclaw_api is None:
            # No OpenClaw API connected, return placeholder
            return f"[⚠️ OpenClaw API not connected. Please configure OpenClaw to enable real agent responses.\n\nAgent {agent_id} received message: {message[:100]}...]"
        
        try:
            # Call OpenClaw API to get response from agent
            # OpenClaw API format: openclaw_api.send_message(agent_id, message)
            response = openclaw_api.send_message(agent_id, message)
            return response
        except Exception as e:
            print(f"Failed to get response from agent {agent_id}: {e}")
            return f"[Error from agent {agent_id}: {str(e)}]"
    
    def _generate_initial_proposal(
        self,
        question: str,
        openclaw_api
    ) -> str:
        """Generate initial proposal for consensus"""
        if openclaw_api is None:
            return f"Initial proposal for: {question}"
        
        prompt = f"""The question for consensus is: {question}

Please generate an initial proposal based on the question.
Keep it clear and concise."""
        
        try:
            return openclaw_api.send_message("system", prompt)
        except:
            return f"Initial proposal for: {question}"
    
    def _update_proposal(
        self,
        current_proposal: str,
        feedback: List[Dict[str, Any]],
        openclaw_api
    ) -> str:
        """Update proposal based on feedback"""
        if openclaw_api is None:
            return current_proposal
        
        feedback_text = "\n".join([
            f"- {f['role_name']}: {'agrees' if f['agrees'] else 'disagrees'} - {f['response']}"
            for f in feedback
        ])
        
        prompt = f"""Current proposal: {current_proposal}

Feedback from participants:
{feedback_text}

Please update the proposal incorporating the feedback.
Provide the revised complete proposal."""
        
        try:
            return openclaw_api.send_message("system", prompt)
        except:
            return current_proposal
    
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
        
        # Create a test session
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
