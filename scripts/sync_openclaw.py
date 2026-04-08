#!/usr/bin/env python3
"""
Sync Cyber-Ideal-State configuration with OpenClaw
"""
import os
import json
import yaml


def load_config():
    """Load Cyber-Ideal-State config"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path = os.path.join(project_root, "config", "config.yaml")
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    return {}


def load_openclaw_config():
    """Load OpenClaw configuration"""
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    
    return {}


def get_default_api_key(openclaw_config):
    """Get default API key from OpenClaw config"""
    # First try: Check per-agent models.json (newest OpenClaw versions)
    main_agent_models_path = os.path.expanduser("~/.openclaw/agents/main/agent/models.json")
    if os.path.exists(main_agent_models_path):
        try:
            with open(main_agent_models_path, "r") as f:
                models_config = json.load(f)
            
            # Get first API key from models list
            if isinstance(models_config, list) and len(models_config) > 0:
                for model in models_config:
                    if "apiKey" in model or "api_key" in model:
                        return model.get("apiKey") or model.get("api_key")
        except Exception as e:
            print(f"⚠️  Failed to read main agent models.json: {e}")
    
    # Third try: Check providers for API key (newer OpenClaw versions)
    providers = openclaw_config.get("models", {}).get("providers", {})
    
    for provider_name, provider_config in providers.items():
        if "apiKey" in provider_config:
            return provider_config["apiKey"]
    
    # Fourth try: Check agent-level API key (older versions)
    agents = openclaw_config.get("agents", {})
    
    if "main" in agents and isinstance(agents["main"], dict):
        main_agent = agents["main"]
        if "apiKey" in main_agent or "api_key" in main_agent:
            return main_agent.get("apiKey") or main_agent.get("api_key")
    
    return None


def sync_agents():
    """Sync agents with OpenClaw"""
    # Load roles from project root data/roles/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    roles_dir = os.path.join(project_root, "data", "roles")
    
    if not os.path.exists(roles_dir):
        print("No roles to sync")
        return
    
    openclaw_config = load_openclaw_config()
    
    # Initialize agents list if needed
    if "agents" not in openclaw_config:
        openclaw_config["agents"] = {}
    
    if "list" not in openclaw_config["agents"]:
        openclaw_config["agents"]["list"] = []
    
    agent_list = openclaw_config["agents"]["list"]
    existing_agent_ids = {a["id"] for a in agent_list if "id" in a}
    
    # Iterate through roles
    synced_count = 0
    for filename in os.listdir(roles_dir):
        if filename.endswith('.yaml') or filename.endswith('.json'):
            role_id = filename.rsplit('.', 1)[0]
            
            if role_id in existing_agent_ids:
                continue
                
            with open(os.path.join(roles_dir, filename), "r") as f:
                if filename.endswith('.yaml'):
                    role_data = yaml.safe_load(f)
                else:
                    role_data = json.load(f)
            
            # Add to OpenClaw agents list - only include fields OpenClaw accepts
            agent_config = {
                "id": role_id,
                "name": role_data.get("name", role_id),
                "model": (role_data.get("agent_config", {}) or {}).get("model", "volcengine-plan/glm-4.7")
            }
            
            agent_list.append(agent_config)
            synced_count += 1
    
    # Save OpenClaw config
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    
    with open(config_path, "w") as f:
        json.dump(openclaw_config, f, indent=2)
    
    print(f"✓ Synced {synced_count} new agents to OpenClaw (total {len(agent_list)})")


def sync_api_key():
    """Sync API key configuration"""
    # Get API key from config
    openclaw_config = load_openclaw_config()
    api_key = get_default_api_key(openclaw_config)
    
    if not api_key:
        print("⚠️  No API key found in OpenClaw configuration")
        print("   👉 配置读取路径优先级:")
        print("      1. ~/.openclaw/agents/main/agent/models.json (第一个模型的 apiKey)")
        print("      2. ~/.openclaw/openclaw.json (models.providers.*.apiKey)")
        print("   👉 你可以手动编辑配置文件")
        print("   👉 缺少 API key 不影响基础功能，但无法生成数字 Agent")
        return
    
    print(f"✓ Found API key from OpenClaw configuration")


def restart_gateway():
    """Restart OpenClaw Gateway"""
    try:
        import subprocess
        subprocess.run(
            ["openclaw", "gateway", "restart"],
            check=True,
            capture_output=True
        )
        print("✓ OpenClaw Gateway restarted")
    except Exception as e:
        print(f"⚠️  Failed to restart Gateway: {e}")


def main():
    """Main sync function"""
    print("🔗 Syncing Cyber-Ideal-State with OpenClaw...")
    
    sync_agents()
    sync_api_key()
    restart_gateway()
    
    print("✅ Sync complete!")


if __name__ == "__main__":
    main()
