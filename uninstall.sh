#!/bin/bash
# Cyber-Ideal-State Uninstall Script
# This script removes:
# 1. Synced agents from openclaw.json (removes only cyber-* agents)
# 2. All local data files (data/, agents/, config/ if empty)

set -e

echo "🏛️  Starting Cyber-Ideal-State uninstallation"
echo "========================================"

# 1. Remove cyber-* agents from openclaw.json
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
if [ -f "$OPENCLAW_CONFIG" ]; then
    echo "📝 Updating OpenClaw configuration..."
    # Use jq to filter out agents with id starting with cyber-
    if command -v jq >/dev/null 2>&1; then
        TMP=$(mktemp)
        jq 'if .agents and .agents.list then .agents.list |= map(select(.id | startswith("cyber-") | not)) else . end' "$OPENCLAW_CONFIG" > "$TMP"
        mv "$TMP" "$OPENCLAW_CONFIG"
        echo "✓ Removed all cyber-* agents from openclaw.json"
    else
        echo "⚠️  jq not found, cannot auto-remove agents from openclaw.json"
        echo "   👉  You need to manually remove cyber-* agents from ~/.openclaw/openclaw.json"
    fi
else
    echo "⚠️  OpenClaw config not found at $OPENCLAW_CONFIG"
fi

# 2. Remove local data
echo "🗑️  Removing local data..."
rm -rf data/*
rm -rf agents/*

# Remove empty directories
rmdir data 2>/dev/null || true
rmdir agents 2>/dev/null || true
rmdir config 2>/dev/null || true

echo ""
echo "✅ Uninstallation complete!"
echo ""
echo "Removed:"
echo "  - All cyber-* agents from your OpenClaw config (if jq was available)"
echo "  - All local role and session data"
echo "  - All generated agents"
echo ""
echo "If you want to completely remove the project, run:"
echo "  cd .. && rm -rf Cyber-Ideal-State"
