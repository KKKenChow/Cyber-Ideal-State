"""
Session manager - manage conversation sessions
"""
import os
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.models import Session, Tier


class SessionManager:
    """Manage conversation sessions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sessions_dir = config.get("sessions_dir", "data/sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def create_session(
        self,
        name: str,
        participants: List[Dict[str, str]],
        speaking_mode: str,
        decision_mode: str
    ) -> Session:
        """Create a new session"""
        session_id = str(uuid.uuid4())[:8]
        
        # Use first participant's tier as mode for backwards compatibility
        first_tier = participants[0].get('tier', 'worker') if participants else 'worker'
        
        session = Session(
            id=session_id,
            name=name,
            participants=participants,
            speaking_mode=speaking_mode,
            decision_mode=decision_mode,
            mode=Tier(first_tier)
        )
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if os.path.exists(filepath):
            return self._load_session(filepath)
        
        return None
    
    def save_session(self, session: Session):
        """Save session to disk"""
        filepath = os.path.join(self.sessions_dir, f"{session.id}.json")
        
        session.updated_at = datetime.now()
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        
        return False
    
    def list_sessions(
        self,
        role_id: Optional[str] = None,
        mode: Optional[str] = None,
        active: Optional[bool] = None
    ) -> List[Session]:
        """List sessions with filters"""
        sessions = []
        
        if not os.path.exists(self.sessions_dir):
            return sessions
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.sessions_dir, filename)
                session = self._load_session(filepath)
                
                if session:
                    # Apply filters
                    if role_id:
                        # Check if role_id is in any participant
                        has_role = any(p.get('role_id') == role_id for p in session.participants)
                        if not has_role:
                            continue
                    if mode and session.mode.value != mode:
                        continue
                    if active is not None and session.active != active:
                        continue
                    
                    sessions.append(session)
        
        return sessions
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Session]:
        """Add a message to a session"""
        session = self.get_session(session_id)
        
        if not session:
            return None
        
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        session.messages.append(message)
        self.save_session(session)
        
        return session
    
    def _load_session(self, filepath: str) -> Optional[Session]:
        """Load session from file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Backwards compatibility: old format has role_id, new format has name + participants
            if 'participants' not in data:
                # Convert old format to new format
                participants = [{
                    'role_id': data['role_id'],
                    'role_name': 'Unknown',
                    'tier': data['mode']
                }]
                name = data.get('name', f'Session {data["id"]}')
                speaking_mode = data.get('speaking_mode', 'free')
                decision_mode = data.get('decision_mode', 'chat')
            else:
                participants = data.get('participants', [])
                name = data.get('name', f'Session {data["id"]}')
                speaking_mode = data.get('speaking_mode', 'free')
                decision_mode = data.get('decision_mode', 'chat')
            
            return Session(
                id=data["id"],
                name=name,
                participants=participants,
                speaking_mode=speaking_mode,
                decision_mode=decision_mode,
                mode=Tier(data["mode"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                messages=data.get("messages", []),
                active=data.get("active", True)
            )
        except Exception as e:
            print(f"Failed to load session from {filepath}: {e}")
            return None


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage conversation sessions")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List sessions")
    list_parser.add_argument("--role-id", help="Filter by role ID")
    list_parser.add_argument("--mode", help="Filter by mode")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a session")
    get_parser.add_argument("session_id", help="Session ID")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a session")
    create_parser.add_argument("role_id", help="Role ID")
    create_parser.add_argument("mode", choices=["philosopher", "guardian", "worker"])
    
    args = parser.parse_args()
    
    # Initialize manager
    config = {
        "sessions_dir": "data/sessions"
    }
    
    manager = SessionManager(config)
    
    if args.command == "list":
        sessions = manager.list_sessions(
            role_id=getattr(args, 'role_id', None),
            mode=getattr(args, 'mode', None)
        )
        
        print(f"Found {len(sessions)} sessions:")
        for session in sessions:
            print(f"  {session.id}: {session.role_id} ({session.mode.value}) - {len(session.messages)} messages")
    
    elif args.command == "get":
        session = manager.get_session(args.session_id)
        
        if session:
            print(json.dumps(session.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(f"Session not found: {args.session_id}")
    
    elif args.command == "create":
        session = manager.create_session(args.role_id, args.mode)
        manager.save_session(session)
        
        print(f"Created session: {session.id}")
        print(json.dumps(session.to_dict(), indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
