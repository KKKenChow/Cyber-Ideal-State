"""
Decision engine for multi-agent voting and debate
"""
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.models import Decision, Tier


class DecisionEngine:
    """Multi-agent decision engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.decisions_dir = config.get("decisions_dir", "data/decisions")
    
    def create_decision(
        self,
        topic: str,
        participants: List[str],
        mode: str = "vote",
        weights: Optional[Dict[str, float]] = None
    ) -> Decision:
        """Create a new decision process"""
        decision_id = str(uuid.uuid4())[:8]
        
        decision = Decision(
            id=decision_id,
            topic=topic,
            participants=participants,
            mode=mode,
            weights=weights or {p: 1.0 for p in participants}
        )
        
        return decision
    
    def vote(self, decision: Decision, openclaw_api=None) -> Dict[str, Any]:
        """Execute voting decision mode"""
        print(f"🗳️ Starting vote on: {decision.topic}")
        
        votes = {}
        total_weight = 0
        
        # Collect votes from all participants
        for participant_id in decision.participants:
            print(f"   Collecting vote from {participant_id}...")
            
            vote = self._get_vote_from_agent(participant_id, decision.topic, openclaw_api)
            weight = decision.weights.get(participant_id, 1.0)
            
            votes[participant_id] = {
                "vote": vote,
                "weight": weight
            }
            
            total_weight += weight
        
        decision.votes = votes
        
        # Calculate weighted result
        result = self._calculate_weighted_result(votes)
        decision.final_decision = result["decision"]
        decision.confidence = result["confidence"]
        decision.completed_at = datetime.now()
        
        return result
    
    def debate(self, decision: Decision, rounds: int = 3, openclaw_api=None) -> Dict[str, Any]:
        """Execute debate decision mode"""
        print(f"🎭 Starting debate on: {decision.topic}")
        
        debate_history = []
        
        for round_num in range(1, rounds + 1):
            print(f"   Round {round_num}...")
            
            round_debate = {
                "round": round_num,
                "messages": []
            }
            
            # Each participant speaks in order
            for participant_id in decision.participants:
                message = self._get_debate_message(
                    participant_id,
                    decision.topic,
                    debate_history,
                    round_num,
                    openclaw_api
                )
                
                round_debate["messages"].append({
                    "participant": participant_id,
                    "message": message
                })
                
                print(f"      {participant_id}: {message[:50]}...")
            
            debate_history.append(round_debate)
        
        decision.debate_history = debate_history
        
        # Generate summary and final decision
        summary = self._generate_debate_summary(debate_history, openclaw_api)
        decision.final_decision = summary["decision"]
        decision.confidence = summary["confidence"]
        decision.completed_at = datetime.now()
        
        return summary
    
    def consensus(self, decision: Decision, max_rounds: int = 5, openclaw_api=None) -> Dict[str, Any]:
        """Execute consensus decision mode"""
        print(f"🤝 Seeking consensus on: {decision.topic}")
        
        round_num = 0
        consensus_reached = False
        current_proposal = None
        
        while round_num < max_rounds and not consensus_reached:
            round_num += 1
            print(f"   Round {round_num}...")
            
            # Generate or update proposal
            if not current_proposal:
                current_proposal = self._generate_initial_proposal(decision.topic, openclaw_api)
            else:
                current_proposal = self._update_proposal(decision.topic, current_proposal, decision.debate_history, openclaw_api)
            
            # Get feedback from all participants
            feedback = {}
            consensus_votes = 0
            
            for participant_id in decision.participants:
                response = self._get_consensus_feedback(participant_id, current_proposal, openclaw_api)
                feedback[participant_id] = response
                
                if response.get("agrees", False):
                    consensus_votes += 1
            
            # Record in debate history
            decision.debate_history.append({
                "round": round_num,
                "proposal": current_proposal,
                "feedback": feedback,
                "consensus_votes": consensus_votes
            })
            
            # Check if consensus reached
            if consensus_votes == len(decision.participants):
                consensus_reached = True
                break
        
        if consensus_reached:
            decision.final_decision = current_proposal
            decision.confidence = 1.0
            print("   ✓ Consensus reached!")
        else:
            # Fall back to voting
            result = self.vote(decision, openclaw_api)
            decision.final_decision = result["decision"]
            decision.confidence = result["confidence"]
            print("   ⚠️  Consensus not reached, fell back to voting")
        
        decision.completed_at = datetime.now()
        return {
            "mode": "consensus",
            "rounds": round_num,
            "consensus_reached": consensus_reached,
            "final_decision": decision.final_decision,
            "confidence": decision.confidence
        }
    
    def _get_vote_from_agent(self, agent_id: str, topic: str, openclaw_api=None) -> str:
        """Get vote from an agent"""
        if openclaw_api is None:
            return f"{agent_id} votes: YES"
        
        prompt = f"""The topic for vote is: {topic}

Please vote YES or NO and give a brief reason."""
        
        try:
            return openclaw_api.send_message(agent_id, prompt)
        except Exception as e:
            print(f"Failed to get vote from {agent_id}: {e}")
            return f"{agent_id} votes: ABSTAIN (error: {e})"
    
    def _get_debate_message(
        self,
        agent_id: str,
        topic: str,
        debate_history: List[Dict[str, Any]],
        round_num: int,
        openclaw_api=None
    ) -> str:
        """Get debate message from an agent"""
        if openclaw_api is None:
            return f"{agent_id} shares their perspective on {topic}"
        
        # Build context from previous rounds
        context = ""
        if debate_history:
            context = "Previous debate:\n\n"
            for prev_round in debate_history:
                for msg in prev_round["messages"]:
                    context += f"{msg['participant']}: {msg['message'][:200]}...\n\n"
        
        prompt = f"""{context}The debate topic is: {topic}

This is round {round_num}. Please share your perspective."""
        
        try:
            return openclaw_api.send_message(agent_id, prompt)
        except Exception as e:
            print(f"Failed to get debate message from {agent_id}: {e}")
            return f"[{agent_id} error: {e}]"
    
    def _generate_initial_proposal(self, topic: str, openclaw_api=None) -> str:
        """Generate initial proposal for consensus"""
        if openclaw_api is None:
            return f"Proposal for: {topic}"
        
        prompt = f"""Generate an initial proposal for: {topic}

Be specific and practical."""
        
        try:
            return openclaw_api.send_message("system", prompt)
        except Exception as e:
            print(f"Failed to generate initial proposal: {e}")
            return f"Proposal for: {topic}"
    
    def _update_proposal(
        self,
        topic: str,
        current_proposal: str,
        debate_history: List[Dict[str, Any]],
        openclaw_api=None
    ) -> str:
        """Update proposal based on feedback"""
        if openclaw_api is None:
            return current_proposal
        
        # Build feedback context
        feedback_text = ""
        last_round = debate_history[-1] if debate_history else None
        if last_round and "feedback" in last_round:
            feedback_text = "Feedback from participants:\n\n"
            for agent_id, resp in last_round["feedback"].items():
                agrees = "agrees" if resp.get("agrees") else "disagrees"
                feedback_text += f"- {agent_id} ({agrees}): {resp.get('response', '')}\n"
        
        prompt = f"""Topic: {topic}
Current proposal: {current_proposal}

{feedback_text}

Please update the proposal incorporating the feedback.
Provide the complete revised proposal."""
        
        try:
            return openclaw_api.send_message("system", prompt)
        except Exception as e:
            print(f"Failed to update proposal: {e}")
            return current_proposal
    
    def _get_consensus_feedback(self, agent_id: str, proposal: str, openclaw_api=None) -> Dict[str, Any]:
        """Get consensus feedback from an agent"""
        if openclaw_api is None:
            return {
                "agrees": True,
                "response": "Placeholder feedback"
            }
        
        prompt = f"""Current proposal: {proposal}

Do you agree with this proposal? Answer YES or NO, then explain why."""
        
        try:
            response = openclaw_api.send_message(agent_id, prompt)
            agrees = "YES" in response.upper()
            return {
                "agrees": agrees,
                "response": response
            }
        except Exception as e:
            print(f"Failed to get consensus feedback from {agent_id}: {e}")
            return {
                "agrees": False,
                "response": f"Error: {e}"
            }
    
    def _calculate_weighted_result(self, votes: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate weighted voting result"""
        # Count votes by type
        vote_counts = {"YES": 0, "NO": 0, "ABSTAIN": 0}
        total_weight = 0
        
        for participant_id, vote_data in votes.items():
            vote = vote_data["vote"]
            weight = vote_data["weight"]
            
            if "YES" in vote.upper():
                vote_counts["YES"] += weight
            elif "NO" in vote.upper():
                vote_counts["NO"] += weight
            else:
                vote_counts["ABSTAIN"] += weight
            
            total_weight += weight
        
        # Determine winner
        if vote_counts["YES"] > vote_counts["NO"]:
            decision = "YES"
            confidence = vote_counts["YES"] / total_weight
        elif vote_counts["NO"] > vote_counts["YES"]:
            decision = "NO"
            confidence = vote_counts["NO"] / total_weight
        else:
            decision = "TIE"
            confidence = 0.5
        
        return {
            "decision": decision,
            "confidence": confidence,
            "vote_counts": vote_counts,
            "total_weight": total_weight
        }
    
    def _generate_debate_summary(self, debate_history: List[Dict[str, Any]], openclaw_api=None) -> Dict[str, Any]:
        """Generate summary from debate"""
        if openclaw_api is None:
            return {
                "decision": "Summary decision",
                "confidence": 0.7,
                "summary": "Debate summary"
            }
        
        # Build debate context
        debate_text = ""
        for round_data in debate_history:
            debate_text += f"=== Round {round_data['round']} ===\n\n"
            for msg in round_data["messages"]:
                debate_text += f"{msg['participant']}: {msg['message']}\n\n"
        
        prompt = f"""Please summarize the following debate and give a final decision/conclusion:

{debate_text}

Provide:
1. A summary of the main arguments
2. A final conclusion/decision
3. Your confidence in this conclusion (0-1)"""
        
        try:
            response = openclaw_api.send_message("system", prompt)
            # Parse response - this is simplistic, but works
            return {
                "decision": response,
                "confidence": 0.7,
                "summary": response
            }
        except Exception as e:
            print(f"Failed to generate debate summary: {e}")
            return {
                "decision": "Failed to generate summary",
                "confidence": 0.0,
                "summary": str(e)
            }
    
    def save_decision(self, decision: Decision):
        """Save decision to disk"""
        import os
        os.makedirs(self.decisions_dir, exist_ok=True)
        
        decision_path = os.path.join(self.decisions_dir, f"{decision.id}.json")
        
        with open(decision_path, "w", encoding="utf-8") as f:
            json.dump(decision.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"✓ Decision saved to {decision_path}")


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-agent decision engine")
    parser.add_argument("--topic", required=True, help="Decision topic")
    parser.add_argument("--participants", required=True, help="Comma-separated participant IDs")
    parser.add_argument("--mode", choices=["vote", "debate", "consensus"], default="vote")
    parser.add_argument("--weights", help="Comma-separated weights")
    parser.add_argument("--rounds", type=int, default=3, help="Debate/consensus rounds")
    
    args = parser.parse_args()
    
    # Parse participants
    participants = [p.strip() for p in args.participants.split(",")]
    
    # Parse weights
    weights = None
    if args.weights:
        weight_list = [float(w.strip()) for w in args.weights.split(",")]
        weights = {p: w for p, w in zip(participants, weight_list)}
    
    # Initialize engine
    config = {
        "decisions_dir": "data/decisions"
    }
    
    engine = DecisionEngine(config)
    
    # Create decision
    decision = engine.create_decision(
        topic=args.topic,
        participants=participants,
        mode=args.mode,
        weights=weights
    )
    
    # Execute
    result = None
    if args.mode == "vote":
        result = engine.vote(decision)
    elif args.mode == "debate":
        result = engine.debate(decision, rounds=args.rounds)
    elif args.mode == "consensus":
        result = engine.consensus(decision, max_rounds=args.rounds)
    
    # Save
    engine.save_decision(decision)
    
    print(f"\n✅ Decision complete!")
    print(f"   Result: {result}")
    print(f"   Final decision: {decision.final_decision}")
    print(f"   Confidence: {decision.confidence}")


if __name__ == "__main__":
    main()
