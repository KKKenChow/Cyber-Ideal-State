#!/bin/bash
# CyberRepublic Installation Script

set -e

echo "🏛️ Welcome to Cyber-Ideal-State Installation"
echo "========================================="

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $python_version"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check Node.js
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "✓ Node.js version: $node_version"
else
    echo "⚠️  Node.js not found. Frontend UI will be skipped."
    echo "   Install Node.js 18+ from https://nodejs.org"
fi

# Create data directories (project root)
echo "📁 Creating data directories..."
mkdir -p data/roles
mkdir -p data/sessions
mkdir -p data/decisions
mkdir -p data/cache

# Create config directories
mkdir -p config

# Generate default config files
if [ ! -f "config/config.yaml" ]; then
    echo "📝 Generating default config..."
    cp config/config.yaml.example config/config.yaml 2>/dev/null || cat > config/config.yaml << 'EOF'
# CyberRepublic Configuration

openclaw:
  workspace: ~/.openclaw/workspace
  agents_config: ~/.openclaw/openclaw.json

server:
  host: "127.0.0.1"
  port: 8080
  debug: true

agent:
  default_model: "gpt-4"
  default_temperature: 0.7
  default_max_tokens: 2000
  default_timeout: 300

redis:
  enabled: false
  host: "127.0.0.1"
  port: 6379
  db: 0

logging:
  level: "INFO"
  file: "logs/cyber-republic.log"
EOF
fi

if [ ! -f "config/permissions.yaml" ]; then
    cat > config/permissions.yaml << 'EOF'
# Permission Matrix
# Define which tiers can interact with each other

philosopher:
  can_chat_with:
    - guardian
    - worker
  can_mention:
    - all
  can_vote: true

guardian:
  can_chat_with:
    - philosopher
    - worker
  can_mention:
    - philosopher
    - guardian
    - worker
  can_vote: true

worker:
  can_chat_with:
    - philosopher
    - guardian
    - worker
  can_mention:
    - all
  can_vote: false
EOF
fi

# Sync OpenClaw configuration
echo "🔗 Syncing OpenClaw configuration..."
python3 scripts/sync_openclaw.py || echo "⚠️  OpenClaw sync failed (may need manual setup)"

# Build frontend if Node.js is available
if command -v npm &> /dev/null; then
    echo "🎨 Building frontend..."
    cd ui/frontend
    npm install
    npx vite build  # Skip TypeScript type checking for faster build
    cd ../
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Configure OpenClaw API key (if needed)"
echo "  2. Run: ./start.sh"
echo "  3. Open: http://localhost:8080"
echo ""
echo "🏛️ Welcome to Cyber-Ideal-State!"
