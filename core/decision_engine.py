"""
Decision engine for multi-agent voting and debate

This module provides the core decision-making logic (vote/debate/consensus).
It is designed to be called by SessionEngine when a session uses one of
the decision speaking modes, keeping decision algorithms separate from
session lifecycle management.
"""
import json
import uuid
import os
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.models import Decision, Tier


class DecisionEngine:
    """Multi-agent decision engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.decisions_dir = config.get("decisions_dir", "data/decisions")
        # Load permissions for weight calculation
        self.permissions = self._load_permissions()
    
    def _load_permissions(self) -> Dict[str, Any]:
        """Load permissions.yaml for tier-based weight calculation"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        perm_path = os.path.join(project_root, "config", "permissions.yaml")
        if os.path.exists(perm_path):
            try:
                with open(perm_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                return {}
        return {}
    
    def _get_weight_for_tier(self, tier: str) -> float:
        """Get voting weight based on tier from permissions.yaml"""
        tier_perms = self.permissions.get(tier, {})
        can_vote = tier_perms.get("can_vote", True)
        if not can_vote:
            return 0.0
        # Philosopher gets higher weight
        weight_map = {
            "philosopher": 2.0,
            "guardian": 1.0,
            "worker": 0.0  # Workers can discuss but not vote (per permissions.yaml)
        }
        return weight_map.get(tier, 1.0)
    
    def _normalize_weights_for_diversity(
        self,
        weights: Dict[str, float],
        participants: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Normalize weights when tier diversity is insufficient.
        
        Scenarios where equal weights (1.0 each) are used instead of tier weights:
        1. Only one tier is present among participants (no diversity)
        2. All participants have the same effective weight (e.g. all guardians)
        3. All participants have zero weight (e.g. all workers)
        
        In these cases, tier-based weighting adds no discriminative value,
        so we fall back to equal-weight democratic voting.
        """
        # Gather the distinct tiers present
        present_tiers = set()
        for p in participants:
            tier = p.get("tier", "worker")
            # Only count tiers that have a non-zero weight
            if weights.get(p["role_id"], 0.0) > 0:
                present_tiers.add(tier)
        
        # Gather distinct non-zero weight values
        nonzero_weights = set()
        for w in weights.values():
            if w > 0:
                nonzero_weights.add(w)
        
        # Condition 1: no voters with non-zero weight at all (e.g. all workers)
        # Condition 2: only one tier has voting power
        # Condition 3: all non-zero weights are the same value
        use_equal_weights = (
            len(present_tiers) == 0 or    # all workers / all weight=0
            len(present_tiers) == 1 or    # only one tier voting
            len(nonzero_weights) == 1      # all same weight (e.g. all guardians)
        )
        
        if use_equal_weights:
            equal_weights = {pid: 1.0 for pid in weights}
            print(f"   ℹ️  Tier diversity insufficient for weighted voting, using equal weights (1.0 each)")
            return equal_weights
        
        return weights
    
    def create_decision(
        self,
        topic: str,
        participants: List[Dict[str, Any]],  # [{role_id, role_name, tier}]
        mode: str = "vote",
        weights: Optional[Dict[str, float]] = None,
        session_id: Optional[str] = None
    ) -> Decision:
        """Create a new decision process
        
        Args:
            topic: The question/issue to decide on
            participants: List of participant dicts with role_id, role_name, tier
            mode: vote | debate | consensus
            weights: Optional custom weights {role_id: weight}. If not provided,
                     weights are derived from permissions.yaml tier rules.
                     When participants lack tier diversity (only one tier present,
                     or all tiers have the same effective weight), the system
                     automatically switches to equal-weight mode (1.0 each).
            session_id: Optional session ID to link this decision back to
        """
        decision_id = str(uuid.uuid4())[:8]
        
        participant_ids = [p["role_id"] for p in participants]
        
        # Auto-derive weights from tier permissions if not explicitly provided
        if weights is None:
            weights = {}
            for p in participants:
                weights[p["role_id"]] = self._get_weight_for_tier(p.get("tier", "worker"))
            
            # Check tier diversity: if insufficient diversity, use equal weights
            weights = self._normalize_weights_for_diversity(weights, participants)
        
        decision = Decision(
            id=decision_id,
            topic=topic,
            participants=participant_ids,
            mode=mode,
            weights=weights
        )
        
        # Store participant metadata for richer output
        decision._participant_meta = {
            p["role_id"]: {"role_name": p.get("role_name", p["role_id"]), "tier": p.get("tier", "worker")}
            for p in participants
        }
        
        # Store session reference
        decision._session_id = session_id
        
        return decision
    
    def vote(self, decision: Decision, openclaw_api=None) -> Dict[str, Any]:
        """Execute voting decision mode
        
        Returns a structured result with per-participant votes, weighted counts,
        and the final decision.
        """
        print(f"🗳️ Starting vote on: {decision.topic}")
        
        votes = {}
        total_weight = 0
        
        # Collect votes from all participants
        for participant_id in decision.participants:
            participant_meta = getattr(decision, '_participant_meta', {}).get(participant_id, {})
            role_name = participant_meta.get("role_name", participant_id)
            
            print(f"   Collecting vote from {role_name} ({participant_id})...")
            
            vote_text = self._get_vote_from_agent(participant_id, decision.topic, openclaw_api)
            weight = decision.weights.get(participant_id, 1.0)
            
            # Extract vote from response
            vote = "ABSTAIN"
            if "YES" in vote_text.upper():
                vote = "YES"
            elif "NO" in vote_text.upper():
                vote = "NO"
            
            votes[participant_id] = {
                "vote": vote,
                "reason": vote_text,
                "weight": weight,
                "role_name": role_name
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
        """Execute debate decision mode
        
        Each participant speaks in order for N rounds, building on previous
        arguments. A summary is generated at the end.
        """
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
                participant_meta = getattr(decision, '_participant_meta', {}).get(participant_id, {})
                role_name = participant_meta.get("role_name", participant_id)
                
                message = self._get_debate_message(
                    participant_id,
                    decision.topic,
                    debate_history,
                    round_num,
                    openclaw_api
                )
                
                round_debate["messages"].append({
                    "participant": participant_id,
                    "role_name": role_name,
                    "message": message
                })
                
                print(f"      {role_name}: {message[:50]}...")
            
            debate_history.append(round_debate)
        
        decision.debate_history = debate_history
        
        # Generate summary and final decision
        summary = self._generate_debate_summary(debate_history, openclaw_api)
        decision.final_decision = summary["decision"]
        decision.confidence = summary["confidence"]
        decision.completed_at = datetime.now()
        
        return summary
    
    def consensus(self, decision: Decision, max_rounds: int = 5, openclaw_api=None) -> Dict[str, Any]:
        """Execute consensus decision mode
        
        Iteratively generates/refines proposals and collects feedback until
        all participants agree or max_rounds is reached (falls back to vote).
        """
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
                participant_meta = getattr(decision, '_participant_meta', {}).get(participant_id, {})
                role_name = participant_meta.get("role_name", participant_id)
                
                response = self._get_consensus_feedback(participant_id, current_proposal, openclaw_api)
                feedback[participant_id] = {
                    **response,
                    "role_name": role_name
                }
                
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
            "confidence": decision.confidence,
            "proposal": current_proposal if consensus_reached else None
        }
    
    def execute(self, decision: Decision, openclaw_api=None, rounds: int = 3) -> Dict[str, Any]:
        """Execute a decision based on its mode (convenience method)
        
        This is the main entry point called by SessionEngine.
        """
        if decision.mode == "vote":
            return self.vote(decision, openclaw_api)
        elif decision.mode == "debate":
            return self.debate(decision, rounds=rounds, openclaw_api=openclaw_api)
        elif decision.mode == "consensus":
            return self.consensus(decision, max_rounds=rounds, openclaw_api=openclaw_api)
        else:
            raise ValueError(f"Unknown decision mode: {decision.mode}")
    
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
                    role_name = msg.get("role_name", msg["participant"])
                    context += f"{role_name}: {msg['message'][:200]}...\n\n"
        
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
                role_name = resp.get("role_name", agent_id)
                agrees = "agrees" if resp.get("agrees") else "disagrees"
                feedback_text += f"- {role_name} ({agrees}): {resp.get('response', '')}\n"
        
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
        vote_counts = {"YES": 0.0, "NO": 0.0, "ABSTAIN": 0.0}
        total_weight = 0.0
        
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
        
        # Determine winner (handle zero total_weight gracefully)
        if total_weight == 0:
            # All voters have weight 0, fall back to simple count
            yes_count = sum(1 for v in votes.values() if v["vote"] == "YES")
            no_count = sum(1 for v in votes.values() if v["vote"] == "NO")
            if yes_count > no_count:
                decision = "YES"
                confidence = yes_count / len(votes) if votes else 0
            elif no_count > yes_count:
                decision = "NO"
                confidence = no_count / len(votes) if votes else 0
            else:
                decision = "TIE"
                confidence = 0.5
        elif vote_counts["YES"] > vote_counts["NO"]:
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
            "confidence": round(confidence, 3),
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
                role_name = msg.get("role_name", msg["participant"])
                debate_text += f"{role_name}: {msg['message']}\n\n"
        
        prompt = f"""Please summarize the following debate and give a final decision/conclusion:

{debate_text}

Provide:
1. A summary of the main arguments
2. A final conclusion/decision
3. Your confidence in this conclusion (0-1)"""
        
        try:
            response = openclaw_api.send_message("system", prompt)
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
        os.makedirs(self.decisions_dir, exist_ok=True)
        
        decision_path = os.path.join(self.decisions_dir, f"{decision.id}.json")
        
        # Prepare save data with extra metadata
        data = decision.to_dict()
        if hasattr(decision, '_session_id'):
            data["session_id"] = decision._session_id
        if hasattr(decision, '_participant_meta'):
            data["participant_meta"] = decision._participant_meta
        
        with open(decision_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Decision saved to {decision_path}")
    
    def list_decisions(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all decisions, optionally filtered by session_id"""
        decisions = []
        
        if not os.path.exists(self.decisions_dir):
            return decisions
        
        for filename in os.listdir(self.decisions_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.decisions_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if session_id and data.get("session_id") != session_id:
                        continue
                    decisions.append(data)
                except Exception:
                    continue
        
        # Sort by created_at descending
        decisions.sort(key=lambda d: d.get("created_at", ""), reverse=True)
        return decisions
    
    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific decision by ID"""
        filepath = os.path.join(self.decisions_dir, f"{decision_id}.json")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None


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
    participant_ids = [p.strip() for p in args.participants.split(",")]
    
    # Build participant dicts (CLI mode: no tier info available)
    participants = [{"role_id": pid, "role_name": pid, "tier": "worker"} for pid in participant_ids]
    
    # Parse weights
    weights = None
    if args.weights:
        weight_list = [float(w.strip()) for w in args.weights.split(",")]
        weights = {p: w for p, w in zip(participant_ids, weight_list)}
    
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
    result = engine.execute(decision, rounds=args.rounds)
    
    # Save
    engine.save_decision(decision)
    
    print(f"\n✅ Decision complete!")
    print(f"   Result: {result}")
    print(f"   Final decision: {decision.final_decision}")
    print(f"   Confidence: {decision.confidence}")


if __name__ == "__main__":
    main()
