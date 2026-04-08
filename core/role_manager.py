"""
Role manager - manage digital roles/lives
"""
import os
import json
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.models import Role, RoleType, Tier


class RoleManager:
    """Manage digital roles"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.roles_dir = config.get("roles_dir", "data/roles")
        os.makedirs(self.roles_dir, exist_ok=True)

    def list_roles(self) -> List[Role]:
        """List all roles"""
        roles = []

        if not os.path.exists(self.roles_dir):
            return roles

        for filename in os.listdir(self.roles_dir):
            if filename.endswith('.yaml') or filename.endswith('.json'):
                filepath = os.path.join(self.roles_dir, filename)
                role = self._load_role(filepath)
                if role:
                    roles.append(role)

        return roles

    def get_role(self, role_id: str) -> Optional[Role]:
        """Get a role by ID"""
        filepath = os.path.join(self.roles_dir, f"{role_id}.yaml")

        if not os.path.exists(filepath):
            filepath = os.path.join(self.roles_dir, f"{role_id}.json")

        if os.path.exists(filepath):
            return self._load_role(filepath)

        return None

    def save_role(self, role: Role):
        """Save role to disk"""
        filepath = os.path.join(self.roles_dir, f"{role.id}.yaml")

        role.updated_at = datetime.now()

        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(role.to_dict(), f, allow_unicode=True, default_flow_style=False)

    def delete_role(self, role_id: str) -> bool:
        """Delete a role"""
        filepath = os.path.join(self.roles_dir, f"{role_id}.yaml")

        if not os.path.exists(filepath):
            filepath = os.path.join(self.roles_dir, f"{role_id}.json")

        if os.path.exists(filepath):
            os.remove(filepath)
            return True

        return False

    def _load_role(self, filepath: str) -> Optional[Role]:
        """Load role from file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            return Role.from_dict(data)
        except Exception as e:
            print(f"Failed to load role from {filepath}: {e}")
            return None

    def filter_roles(
        self,
        role_type: Optional[str] = None,
        tier: Optional[str] = None,
        active: Optional[bool] = None
    ) -> List[Role]:
        """Filter roles by criteria"""
        roles = self.list_roles()

        if role_type:
            roles = [r for r in roles if r.type.value == role_type]

        if tier:
            roles = [r for r in roles if r.tier.value == tier]

        if active is not None:
            roles = [r for r in roles if r.active == active]

        return roles

    def update_role(self, role_id: str, updates: Dict[str, Any]) -> Optional[Role]:
        """Update role properties"""
        role = self.get_role(role_id)

        if not role:
            return None

        for key, value in updates.items():
            if hasattr(role, key):
                setattr(role, key, value)

        self.save_role(role)
        return role

    def export_role(self, role_id: str, format: str = "json") -> Optional[Dict[str, Any]]:
        """Export role data"""
        role = self.get_role(role_id)

        if not role:
            return None

        return role.to_dict()

    def import_role(self, role_data: Dict[str, Any]) -> Optional[Role]:
        """Import role data"""
        try:
            role = Role.from_dict(role_data)
            self.save_role(role)
            return role
        except Exception as e:
            print(f"Failed to import role: {e}")
            return None

    def create_role(
        self,
        name: str,
        role_type: str,
        tier: str,
        description: Optional[str] = None,
        manual_description: Optional[str] = None
    ) -> Role:
        """Create a new role"""
        import uuid
        from datetime import datetime
        from core.models import Role, RoleType, Tier, Memory

        role_id = f"cyber-{str(uuid.uuid4())[:8]}"

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

        self.save_role(role)
        return role


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Manage digital roles")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # List command
    list_parser = subparsers.add_parser("list", help="List all roles")
    list_parser.add_argument("--type", help="Filter by type")
    list_parser.add_argument("--tier", help="Filter by tier")
    list_parser.add_argument("--active", type=bool, help="Filter by active status")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a role")
    get_parser.add_argument("role_id", help="Role ID")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a role")
    delete_parser.add("role_id", help="Role ID")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export a role")
    export_parser.add_argument("role_id", help="Role ID")
    export_parser.add_argument("--output", help="Output file")

    args = parser.parse_args()

    # Initialize manager
    config = {
        "roles_dir": "data/roles"
    }

    manager = RoleManager(config)

    if args.command == "list":
        roles = manager.filter_roles(
            role_type=args.type,
            tier=args.tier,
            active=args.active
        )

        print(f"Found {len(roles)} roles:")
        for role in roles:
            print(f"  {role.id}: {role.name} ({role.type.value} / {role.tier.value})")

    elif args.command == "get":
        role = manager.get_role(args.role_id)

        if role:
            print(json.dumps(role.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(f"Role not found: {args.role_id}")

    elif args.command == "delete":
        success = manager.delete_role(args.role_id)

        if success:
            print(f"Deleted role: {args.role_id}")
        else:
            print(f"Failed to delete role: {args.role_id}")

    elif args.command == "export":
        role_data = manager.export_role(args.role_id)

        if role_data:
            output_file = args.output or f"{args.role_id}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(role_data, f, indent=2, ensure_ascii=False)

            print(f"Exported role to: {output_file}")
        else:
            print(f"Role not found: {args.role_id}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
