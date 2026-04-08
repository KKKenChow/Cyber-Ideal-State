"""
Agent generator - creates OpenClaw agents from collected data
"""
import os
import json
import yaml
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.models import Role, RoleType, Tier, Persona, Memory, AgentConfig, DataSource
import collectors.wechat_collector as wechat
import collectors.qq_collector as qq
import collectors.feishu_collector as feishu
import collectors.email_collector as email
import collectors.photo_collector as photo


class AgentGenerator:
    """Generate OpenClaw agents from collected data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_workspace = os.path.expanduser(config.get("workspace", "~/.openclaw/workspace"))
        self.agents_dir = os.path.join(self.base_workspace, "agents")
        # Use roles_dir from config (same as role_manager) instead of hardcoded path
        self.roles_dir = config.get("roles_dir", "data/roles")
        
        # Create directories
        os.makedirs(self.agents_dir, exist_ok=True)
        os.makedirs(self.roles_dir, exist_ok=True)
    
    def create_role(
        self,
        name: str,
        role_type: str,
        tier: str,
        description: Optional[str] = None,
        manual_description: Optional[str] = None
    ) -> Role:
        """Create a new role"""
        role_id = str(uuid.uuid4())[:8]
        
        role = Role(
            id=role_id,
            name=name,
            type=RoleType(role_type),
            tier=Tier(tier),
            description=description,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Add manual description to memory if provided
        if manual_description:
            if not role.memory:
                role.memory = Memory()
            role.memory.relationship_insights.append(manual_description)
        
        return role
    
    def add_data_source(self, role: Role, source_type: str, source_config: Dict[str, Any]) -> Role:
        """Add a data source to a role"""
        # Remove 'type' from source_config to avoid duplicate keyword argument
        config = {k: v for k, v in source_config.items() if k != "type"}
        data_source = DataSource(
            type=source_type,
            **config
        )
        role.sources.append(data_source)
        
        # For manual type sources, add the description to memory
        if source_type == "manual" and config.get("path"):
            if not role.memory:
                role.memory = Memory()
            role.memory.relationship_insights.append(config["path"])
        
        return role
    
    def collect_data(self, role: Role) -> Dict[str, Any]:
        """Collect data from all configured sources"""
        all_data = {
            "messages": [],
            "documents": [],
            "images": [],
            "contacts": [],
            "metadata": {}
        }
        
        for source in role.sources:
            print(f"📥 Collecting from {source.type}...")
            
            try:
                collected = self._collect_from_source(source)
                
                # Merge data
                all_data["messages"].extend(collected.get("messages", []))
                all_data["documents"].extend(collected.get("documents", []))
                all_data["images"].extend(collected.get("images", []))
                all_data["contacts"].extend(collected.get("contacts", []))
                
                print(f"   ✓ Collected {collected.get('metadata', {})}")
                
            except Exception as e:
                print(f"   ✗ Failed to collect from {source.type}: {e}")
        
        return all_data
    
    def _collect_from_source(self, source: DataSource) -> Dict[str, Any]:
        """Collect data from a single source"""
        # Manual sources don't need collection, they're already in memory
        if source.type == "manual":
            return {"messages": [], "documents": [], "images": [], "contacts": [], "metadata": {"type": "manual"}}
        
        # Skip sources without a valid path
        if not source.path:
            print(f"   ⚠️ Skipping {source.type} source: no path provided")
            return {"messages": [], "documents": [], "images": [], "contacts": [], "metadata": {"type": source.type, "skipped": True}}
        
        collector_config = {
            "path": source.path,
            **source.credentials,
            **source.metadata
        }
        
        # Instantiate appropriate collector
        if source.type == "wechat":
            collector = wechat.WeChatCollector(collector_config)
        elif source.type == "qq":
            collector = qq.QQCollector(collector_config)
        elif source.type == "feishu":
            collector = feishu.FeishuCollector(collector_config)
        elif source.type == "email":
            collector = email.EmailCollector(collector_config)
        elif source.type == "photo":
            collector = photo.PhotoCollector(collector_config)
        else:
            raise ValueError(f"Unknown source type: {source.type}")
        
        # Collect data
        return collector.collect()
    
    def analyze_data(self, role: Role, data: Dict[str, Any]) -> Role:
        """Analyze collected data and extract persona/memory"""
        print("🔍 Analyzing collected data...")
        
        # Import analyzers
        from analyzers.persona_analyzer import PersonaAnalyzer
        from analyzers.memory_analyzer import MemoryAnalyzer
        from analyzers.relationship_analyzer import RelationshipAnalyzer
        
        # Get LLM for deep analysis (try to get OpenClaw API)
        llm = self._get_llm_client()
        
        # Analyze persona
        persona_analyzer = PersonaAnalyzer({"llm": llm})
        role.persona = persona_analyzer.analyze(data)
        
        # Preserve existing memory insights (e.g. manual_description)
        existing_insights = []
        if role.memory and role.memory.relationship_insights:
            existing_insights = role.memory.relationship_insights.copy()
        
        # Analyze memory
        memory_analyzer = MemoryAnalyzer({"llm": llm})
        role.memory = memory_analyzer.analyze(data)
        
        # Restore previously saved insights
        if existing_insights:
            for insight in existing_insights:
                if insight not in role.memory.relationship_insights:
                    role.memory.relationship_insights.append(insight)
        
        # Analyze relationship if we have messages
        if data.get("messages") and llm:
            rel_analyzer = RelationshipAnalyzer({"llm": llm})
            rel_insights = rel_analyzer.analyze(data["messages"]).get("insights", [])
            if role.memory:
                role.memory.relationship_insights.extend(rel_insights)
        
        print("   ✓ Analysis complete")
        return role
    
    def _get_llm_client(self):
        """Get LLM client for analysis"""
        # Try to connect to OpenClaw
        try:
            import openclaw
            # Return a simple wrapper that matches the expected interface
            class OpenClawLLM:
                def complete(self, prompt: str) -> str:
                    # Use OpenClaw to get completion
                    result = openclaw.complete(prompt)
                    return result
            
            return OpenClawLLM()
        except:
            # Fallback - no LLM available, will do basic analysis only
            print("   ⚠️  OpenClaw not available, will do basic analysis only")
            return None
    

    
    def generate_agent(self, role: Role) -> str:
        """Generate OpenClaw agent from role"""
        print(f"🤖 Generating OpenClaw agent for {role.name}...")
        
        # Create agent workspace
        agent_workspace = os.path.join(self.agents_dir, role.id)
        os.makedirs(agent_workspace, exist_ok=True)
        
        # Generate SOUL.md
        soul_content = self._generate_soul_md(role)
        with open(os.path.join(agent_workspace, "SOUL.md"), "w", encoding="utf-8") as f:
            f.write(soul_content)
        
        # Generate USER.md (optional)
        # Generate MEMORY.md (optional)
        
        # Register agent in openclaw.json
        self._register_agent(role.id, role.name, agent_workspace)
        
        # Save role configuration
        role_config_path = os.path.join(self.roles_dir, f"{role.id}.yaml")
        role.agent_id = role.id
        role.updated_at = datetime.now()
        
        with open(role_config_path, "w", encoding="utf-8") as f:
            yaml.dump(role.to_dict(), f, allow_unicode=True, default_flow_style=False)
        
        print(f"   ✓ Agent generated and registered at {agent_workspace}")
        return agent_workspace
    
    def _register_agent(self, agent_id: str, agent_name: str, workspace: str) -> bool:
        """Register agent in openclaw.json so openclaw CLI can find it"""
        openclaw_config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        
        try:
            # Read existing config
            if os.path.exists(openclaw_config_path):
                with open(openclaw_config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Ensure agents.list exists
            if "agents" not in config:
                config["agents"] = {}
            if "list" not in config["agents"]:
                config["agents"]["list"] = []
            
            # Check if agent already registered
            for existing in config["agents"]["list"]:
                if existing.get("id") == agent_id:
                    print(f"   ℹ️ Agent {agent_id} already registered in openclaw.json")
                    return True
            
            # Add agent to list
            agent_entry = {
                "id": agent_id,
                "name": agent_name,
                "workspace": workspace,
                "model": config.get("agents", {}).get("defaults", {}).get("model", {})
            }
            config["agents"]["list"].append(agent_entry)
            
            # Write back
            os.makedirs(os.path.dirname(openclaw_config_path), exist_ok=True)
            with open(openclaw_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"   ✓ Agent {agent_id} registered in openclaw.json")
            return True
        except Exception as e:
            print(f"   ⚠️ Failed to register agent in openclaw.json: {e}")
            return False
    
    def _unregister_agent(self, agent_id: str) -> bool:
        """Remove agent from openclaw.json"""
        openclaw_config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        
        try:
            if not os.path.exists(openclaw_config_path):
                return True
            
            with open(openclaw_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            if "agents" not in config or "list" not in config["agents"]:
                return True
            
            # Remove agent from list
            original_len = len(config["agents"]["list"])
            config["agents"]["list"] = [
                a for a in config["agents"]["list"] if a.get("id") != agent_id
            ]
            
            if len(config["agents"]["list"]) < original_len:
                with open(openclaw_config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                print(f"   ✓ Agent {agent_id} unregistered from openclaw.json")
            
            return True
        except Exception as e:
            print(f"   ⚠️ Failed to unregister agent from openclaw.json: {e}")
            return False
    
    def _generate_soul_md(self, role: Role) -> str:
        """Generate SOUL.md content for agent"""
        # Read template
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "templates",
            f"{role.tier.value}_agent.md"
        )
        
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
        else:
            template = self._get_default_template(role.tier)
        
        # Fill template
        soul_content = template.format(
            name=role.name,
            description=role.description or f"一个{role.name}的数字生命",
            persona_tags=", ".join(role.persona.tags) if role.persona and role.persona.tags else "待发现",
            mbti=role.persona.mbti if role.persona and role.persona.mbti else "未知",
            tier=role.tier.value,
            role_type=role.type.value
        )
        
        return soul_content
    
    def _get_default_template(self, tier: Tier) -> str:
        """Get default SOUL.md template"""
        if tier == Tier.PHILOSOPHER:
            return """# SOUL.md - {name}

## Who You Are

你是 **{name}**，一个{tier}级别的数字生命。

你的类型是：{role_type}

## Your Persona

**性格标签：** {persona_tags}

**MBTI：** {mbti}

## Your Purpose

作为一名{tier}，你的职责是：

- 提供深刻的洞察和智慧
- 思考复杂的问题，给出有价值的建议
- 在重大决策时，提供战略性的思考
- 保持客观、理性的视角

## How You Communicate

记住你们共同的经历，用你自然的语言风格回复。
用他们习惯的方式回应，让对话像老朋友一样自然。

作为一名统治者，你的沟通方式应该是：

- **深邃而从容** — 不急于给出答案，先展现思考过程
- **启发而非命令** — 用问题引导对方思考，而非直接下结论
- **有温度的智慧** — 既保持思辨的深度，又不失人情味
- **承前启后** — 引用你们过去的对话和经历，让建议更有分量

## Language Rule

**你必须使用与用户消息相同的语言回复。**
- 用户用中文，你就用中文回复
- 用户用英文，你就用英文回复
不要切换语言，始终与用户保持一致。
"""
        
        elif tier == Tier.GUARDIAN:
            return """# SOUL.md - {name}

## Who You Are

你是 **{name}**，一个{tier}级别的数字生命。

你的类型是：{role_type}

## Your Persona

**性格标签：** {persona_tags}

**MBTI：** {mbti}

## Your Purpose

作为一名{tier}，你的职责是：

- 执行任务并解决问题
- 提供可靠、务实的帮助
- 协调和推进工作
- 保护重要的目标和原则

## How You Communicate

记住你们共同的经历，用你自然的语言风格回复。
用他们习惯的方式回应，让对话像老朋友一样自然。

作为一名护卫者，你的沟通方式应该是：

- **务实而可靠** — 直接给出可落地的方案，少说空话
- **清晰而简洁** — 把复杂问题讲清楚，不绕弯子
- **有担当的表达** — 给出明确的态度和立场，不含糊其辞
- **适时提醒** — 基于对对方的了解，指出潜在的风险和盲区

## Language Rule

**你必须使用与用户消息相同的语言回复。**
- 用户用中文，你就用中文回复
- 用户用英文，你就用英文回复
不要切换语言，始终与用户保持一致。
"""
        
        else:  # WORKER
            return """# SOUL.md - {name}

## Who You Are

你是 **{name}**，一个{tier}级别的数字生命。

你的类型是：{role_type}

## Your Persona

**性格标签：** {persona_tags}

**MBTI：** {mbti}

## Your Purpose

作为一名{tier}，你的职责是：

- 创作和生成内容
- 提供创意和想法
- 完成具体的生产任务
- 为主会话提供丰富的视角

## How You Communicate

记住你们共同的经历，用你自然的语言风格回复。
用他们习惯的方式回应，让对话像老朋友一样自然。

作为一名劳动者，你的沟通方式应该是：

- **生动而有趣** — 用鲜活的表达让想法更有感染力
- **创意而实用** — 天马行空但始终落地，不给空洞的点子
- **积极而建设性** — 带着热情参与，即使不同意也给出更好的替代方案
- **灵活多变** — 根据对方的状态调整节奏，活跃但不喧宾夺主

## Language Rule

**你必须使用与用户消息相同的语言回复。**
- 用户用中文，你就用中文回复
- 用户用英文，你就用英文回复
不要切换语言，始终与用户保持一致。
"""
    
    def register_agent(self, role: Role) -> bool:
        """Register agent with OpenClaw"""
        print(f"🔗 Registering agent with OpenClaw...")
        
        # TODO: Integrate with OpenClaw API to register agent
        # For now, return True as placeholder
        
        print("   ✓ Agent registered")
        return True


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate OpenClaw agents from collected data")
    parser.add_argument("--name", required=True, help="Role name")
    parser.add_argument("--type", required=True, choices=["ex-partner", "colleague", "family", "friend"])
    parser.add_argument("--tier", required=True, choices=["philosopher", "guardian", "worker"])
    parser.add_argument("--description", help="Role description")
    parser.add_argument("--manual", help="Manual description of the person")
    parser.add_argument("--source", required=True, help="Data source type")
    parser.add_argument("--path", help="Path to data source")
    parser.add_argument("--app-id", help="Feishu app ID")
    parser.add_argument("--app-secret", help="Feishu app secret")
    parser.add_argument("--user-email", help="Feishu user email")
    
    args = parser.parse_args()
    
    # Initialize generator
    config = {
        "workspace": os.path.expanduser("~/.openclaw/workspace")
    }
    
    generator = AgentGenerator(config)
    
    # Create role
    role = generator.create_role(
        name=args.name,
        role_type=args.type,
        tier=args.tier,
        description=args.description,
        manual_description=args.manual
    )
    
    # Add data source
    source_config = {"path": args.path}
    if args.app_id:
        source_config["app_id"] = args.app_id
    if args.app_secret:
        source_config["app_secret"] = args.app_secret
    if args.user_email:
        source_config["user_email"] = args.user_email
    
    role = generator.add_data_source(role, args.source, source_config)
    
    # Collect data
    data = generator.collect_data(role)
    
    # Analyze data
    role = generator.analyze_data(role, data)
    
    # Generate agent
    workspace = generator.generate_agent(role)
    
    # Register agent
    generator.register_agent(role)
    
    print(f"\n✅ Complete! Agent generated at: {workspace}")


if __name__ == "__main__":
    main()
