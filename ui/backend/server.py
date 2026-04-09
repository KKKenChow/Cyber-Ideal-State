"""
Web server for Cyber-Ideal-State UI
"""
import os
import json
import sys
import shutil
from typing import Dict, Any

# Add parent directory to path for imports (must be before importing core modules)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import openclaw - use the global complete function directly
# This avoids dependency issues with cmdop
try:
    import openclaw
except ImportError:
    # If import fails because of cmdop dependencies, we assume openclaw is already
    # loaded in the current environment and complete is available globally
    pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from core.role_manager import RoleManager
from core.session_manager import SessionManager
from core.session_engine import SessionEngine
from core.agent_generator import AgentGenerator
from core.decision_engine import DecisionEngine


app = FastAPI(
    title="Cyber-Ideal-State API",
    description="赛博理想国 - Digital Life Management Framework",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for frontend
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ui", "frontend", "dist")
app.mount("/ui/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

# Load configuration
import yaml
config_path = os.path.join(project_root, "config", "config.yaml")

# Data directories are based on project root (not CWD) so paths work
# regardless of where the server is started from (start.sh does cd ui/backend)
_data_dir = os.path.join(project_root, "data")

config_default = {
    "roles_dir": os.path.join(_data_dir, "roles"),
    "sessions_dir": os.path.join(_data_dir, "sessions"),
    "decisions_dir": os.path.join(_data_dir, "decisions"),
    "workspace": os.path.expanduser("~/.openclaw/workspace")
}

if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config_loaded = yaml.safe_load(f)
    
    # Merge with defaults
    config = {
        "roles_dir": os.path.join(_data_dir, "roles"),
        "sessions_dir": os.path.join(_data_dir, "sessions"),
        "decisions_dir": os.path.join(_data_dir, "decisions"),
        "workspace": os.path.expanduser(config_loaded.get("openclaw", {}).get("workspace", "~/.openclaw/workspace"))
    }
    
    # Update server config
    server_config = config_loaded.get("server", {})
    host = server_config.get("host", "127.0.0.1")
    port = server_config.get("port", 8080)
else:
    config = config_default
    host = "127.0.0.1"
    port = 8080

role_manager = RoleManager(config)
session_manager = SessionManager(config)
session_engine = SessionEngine(config)
agent_generator = AgentGenerator(config)
decision_engine = DecisionEngine(config)


class OpenClAPIImpl:
    """Implementation of the OpenClaw API interface expected by session_engine"""
    
    @staticmethod
    def _clean_response(raw: str) -> str:
        """Clean openclaw CLI output: remove ANSI codes, plugin logs, and other noise"""
        import re
        # Remove ANSI escape sequences (colors, cursor movement, etc.)
        cleaned = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw)
        # Remove openclaw plugin/status log lines like [agents/xxx], [plugins], etc.
        cleaned = re.sub(r'^\s*\[[\w/\-]+\]\s+.*$', '', cleaned, flags=re.MULTILINE)
        # Remove empty lines left after stripping
        lines = [line for line in cleaned.split('\n') if line.strip()]
        return '\n'.join(lines).strip()
    
    def send_message(self, agent_id: str, message: str) -> str:
        """Send message to an agent and get response using openclaw CLI"""
        try:
            import subprocess
            
            # First try: use registered agent id
            result = subprocess.run(
                ["openclaw", "agent", "--agent", agent_id, "--message", message],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return self._clean_response(result.stdout)
            
            # Combine stderr for fallback analysis
            error_output = result.stderr or ""
            
            # Fallback: agent not registered, try using SOUL.md as system prompt
            soul_path = os.path.join(
                agent_generator.agents_dir, agent_id, "SOUL.md"
            )
            if os.path.exists(soul_path):
                with open(soul_path, "r", encoding="utf-8") as f:
                    soul_content = f.read()
                
                # Use openclaw with system prompt
                prompt = f"{soul_content}\n\n---\n\nUser: {message}\n\n请根据你的SOUL.md定义来回复。请使用与用户消息相同的语言回复（如果用户用中文，你就用中文；如果用英文，就用英文）。"
                result = subprocess.run(
                    ["openclaw", "complete", "--prompt", prompt],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    return self._clean_response(result.stdout)
                else:
                    return f"[Agent {agent_id} is not registered with OpenClaw and fallback also failed.]"
            else:
                return f"[Agent {agent_id} has no SOUL.md file. Please regenerate this role.]"
        except FileNotFoundError:
            return "[OpenClaw CLI not found. Please install openclaw first.]"
        except Exception as e:
            print(f"OpenClaw API error: {e}")
            return f"[Error from OpenClaw: {str(e)}]"

# Replace the None with real implementation
openclaw_api_impl = OpenClAPIImpl()

# Update agent_generator to use OpenClaw LLM for analysis
# We need to monkey patch the _get_llm_client method to use our API
from core.agent_generator import AgentGenerator

original_get_llm = AgentGenerator._get_llm_client

def get_openclaw_llm(self):
    class LLMClient:
        def complete(self, prompt: str) -> str:
            return openclaw_api_impl.send_message("system", prompt)
    
    return LLMClient()

AgentGenerator._get_llm_client = get_openclaw_llm


@app.get("/")
async def root():
    """API root"""
    return {
        "name": "Cyber-Ideal-State API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "managers": {
            "role_manager": "active",
            "session_manager": "active",
            "session_engine": "active",
            "agent_generator": "active",
            "decision_engine": "active"
        }
    }


# ==================== Roles API ====================

@app.get("/api/roles")
async def list_roles(
    role_type: str = None,
    tier: str = None,
    active: str = None
):
    """List all roles"""
    # Parse active bool from query string
    active_bool = None
    if active is not None and active != "":
        active_bool = active.lower() in ["true", "1", "yes"]
    
    roles = role_manager.filter_roles(
        role_type=role_type,
        tier=tier,
        active=active_bool
    )
    return {
        "count": len(roles),
        "roles": [role.to_dict() for role in roles]
    }


@app.get("/api/roles/{role_id}")
async def get_role(role_id: str):
    """Get a role by ID"""
    role = role_manager.get_role(role_id)
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return role.to_dict()


@app.post("/api/roles")
async def create_role(data: Dict[str, Any]):
    """Create a new role"""
    try:
        # Create role
        role = role_manager.create_role(
            name=data["name"],
            role_type=data["type"],
            tier=data["tier"],
            description=data.get("description"),
            manual_description=data.get("manual_description")
        )
        
        # Add data sources if provided
        for source in data.get("sources", []):
            role = agent_generator.add_data_source(
                role,
                source["type"],
                source
            )
        
        # Collect data (non-blocking - failures should not prevent role creation)
        try:
            collected_data = agent_generator.collect_data(role)
        except Exception as e:
            print(f"⚠️ Data collection failed (non-fatal): {e}")
            collected_data = {"messages": [], "documents": [], "images": [], "contacts": [], "metadata": {}}
        
        # Analyze data (non-blocking)
        try:
            role = agent_generator.analyze_data(role, collected_data)
        except Exception as e:
            print(f"⚠️ Data analysis failed (non-fatal): {e}")
        
        # Generate agent
        agent_generator.generate_agent(role)
        
        # Save role
        role_manager.save_role(role)
        
        return {
            "status": "success",
            "role_id": role.id,
            "role": role.to_dict()
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/roles/{role_id}")
async def update_role(role_id: str, updates: Dict[str, Any]):
    """Update a role"""
    role = role_manager.update_role(role_id, updates)
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return role.to_dict()


@app.delete("/api/roles/{role_id}")
async def delete_role(role_id: str):
    """Delete a role"""
    # Unregister agent from openclaw.json and clean workspace
    try:
        agent_generator._unregister_agent(role_id)
    except Exception as e:
        print(f"⚠️ Failed to unregister agent: {e}")
    
    # Clean agent workspace directory
    agent_workspace = os.path.join(agent_generator.agents_dir, role_id)
    if os.path.exists(agent_workspace):
        try:
            shutil.rmtree(agent_workspace)
            print(f"   ✓ Cleaned agent workspace: {agent_workspace}")
        except Exception as e:
            print(f"   ⚠️ Failed to clean agent workspace: {e}")
    
    success = role_manager.delete_role(role_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return {"status": "success", "message": "Role deleted"}


@app.post("/api/roles/{role_id}/regenerate")
async def regenerate_role(role_id: str):
    """Regenerate an agent from role"""
    role = role_manager.get_role(role_id)
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    try:
        # Collect data (non-blocking)
        try:
            collected_data = agent_generator.collect_data(role)
        except Exception as e:
            print(f"⚠️ Data collection failed (non-fatal): {e}")
            collected_data = {"messages": [], "documents": [], "images": [], "contacts": [], "metadata": {}}
        
        # Analyze data (non-blocking)
        try:
            role = agent_generator.analyze_data(role, collected_data)
        except Exception as e:
            print(f"⚠️ Data analysis failed (non-fatal): {e}")
        
        # Generate agent
        workspace = agent_generator.generate_agent(role)
        
        # Save role
        role_manager.save_role(role)
        
        return {
            "status": "success",
            "workspace": workspace,
            "role": role.to_dict()
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Sessions API ====================

@app.get("/api/sessions")
async def list_sessions(
    role_id: str = None,
    mode: str = None,
    active: str = None
):
    """List all sessions"""
    # Parse active bool from query string
    active_bool = None
    if active is not None and active != "":
        active_bool = active.lower() in ["true", "1", "yes"]
    
    sessions = session_manager.list_sessions(
        role_id=role_id,
        mode=mode,
        active=active_bool
    )
    return {
        "count": len(sessions),
        "sessions": [session.to_dict() for session in sessions]
    }


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a session by ID"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_dict()


@app.post("/api/sessions")
async def create_session(data: Dict[str, Any]):
    """Create a new session"""
    try:
        # Create session with session engine
        session = session_engine.create_session(
            name=data.get("name", ""),
            participants=data.get("participants", []),
            decision_mode=data.get("decision_mode", "chat"),
            speaking_mode=data.get("speaking_mode", "free")
        )
        
        # Save session
        session_manager.save_session(session)
        
        return session.to_dict()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/messages")
async def send_message(session_id: str, data: Dict[str, Any]):
    """Send a message to a session"""
    from datetime import datetime
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] API: POST /api/sessions/{session_id}/messages")
    print(f"   User message: {data['content'][:200]}{'' if len(data['content']) <= 200 else '...'}")
    
    try:
        # Use session engine to send message with real OpenClaw API
        result = session_engine.send_message(
            session_id=session_id,
            user_message=data["content"],
            openclaw_api=openclaw_api_impl
        )
        
        print(f"   [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Complete: {len(result['responses'])} responses generated")
        for i, resp in enumerate(result['responses']):
            if 'role_id' in resp:
                print(f"      {i+1}. [{resp['role_id']}] {resp['content'][:100]}...")
        
        # Save the updated session
        session = session_manager.get_session(session_id)
        if session:
            session_manager.save_session(session)
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    success = session_manager.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "success", "message": "Session deleted"}


@app.put("/api/sessions/{session_id}/active")
async def toggle_session_active(session_id: str, data: Dict[str, Any]):
    """Toggle session active status"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.active = data.get("active", not session.active)
    session_manager.save_session(session)
    
    return {"status": "success", "active": session.active, "session": session.to_dict()}


@app.delete("/api/sessions/{session_id}/messages")
async def clear_session_messages(session_id: str):
    """Clear all messages in a session (keep system messages)"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Keep only system messages
    session.messages = [m for m in session.messages if m.get("role") == "system"]
    session_manager.save_session(session)
    
    return {"status": "success", "message": "Messages cleared"}


# ==================== Decisions API ====================

@app.get("/api/decisions")
async def list_decisions(session_id: str = None):
    """List all decisions, optionally filtered by session"""
    decisions = decision_engine.list_decisions(session_id=session_id)
    return {
        "count": len(decisions),
        "decisions": decisions
    }


@app.get("/api/decisions/{decision_id}")
async def get_decision(decision_id: str):
    """Get a specific decision by ID"""
    decision = decision_engine.get_decision(decision_id)
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    return decision


# ==================== Stats API ====================

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    from datetime import date
    
    roles = role_manager.list_roles()
    sessions = session_manager.list_sessions()
    decisions = decision_engine.list_decisions()
    
    # Count by tier
    tiers = {}
    for role in roles:
        tier = role.tier.value
        tiers[tier] = tiers.get(tier, 0) + 1
    
    # Count by type
    types = {}
    for role in roles:
        role_type = role.type.value
        types[role_type] = types.get(role_type, 0) + 1
    
    # Today's sessions
    today = date.today().isoformat()
    today_sessions = len([
        s for s in sessions 
        if s.created_at and s.created_at.date().isoformat() == today
    ])
    
    return {
        "roles": {
            "total": len(roles),
            "active": len([r for r in roles if r.active]),
            "by_tier": tiers,
            "by_type": types
        },
        "sessions": {
            "total": len(sessions),
            "active": len([s for s in sessions if s.active]),
            "today": today_sessions
        },
        "decisions": {
            "total": len(decisions),
            "completed": len([d for d in decisions if d.get("completed_at")])
        }
    }


# ==================== Static Files ====================

@app.get("/ui")
async def serve_ui():
    """Serve frontend UI"""
    frontend_dist = os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend",
        "dist"
    )
    
    index_path = os.path.join(frontend_dist, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Frontend not built. Run `npm run build` in ui/frontend")


if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 Starting Cyber-Ideal-State API server...")
    print(f"   http://{host}:{port}")
    print(f"   UI: http://{host}:{port}/ui")
    
    uvicorn.run(app, host=host, port=port)
