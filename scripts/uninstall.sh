#!/bin/bash
# HolySpiritOS uninstaller — removes the skill from every supported agent.
# https://github.com/MaxSikorski/HolySpiritOS

set -uo pipefail

SKILL_NAME="holy-spirit-os"
echo "🕊️ Removing HolySpiritOS..."

remove_dir() { # remove_dir <label> <dir>
    if [ -d "$2" ]; then
        rm -rf "$2"
        echo "✅ $1: removed $2"
    fi
}

remove_dir "Claude Code"  "$HOME/.claude/skills/$SKILL_NAME"
remove_dir "Codex CLI"    "$HOME/.codex/skills/$SKILL_NAME"
remove_dir "Antigravity"  "$HOME/.gemini/antigravity-cli/skills/$SKILL_NAME"
remove_dir "Project"      "$PWD/.agents/skills/$SKILL_NAME"

# --- OpenClaw ---
OPENCLAW_ROOT="$HOME/.openclaw"
if [ -d "$OPENCLAW_ROOT" ]; then
    remove_dir "OpenClaw foundation" "$OPENCLAW_ROOT/workspace/foundation"
    rm -f "$OPENCLAW_ROOT/workspace/scripts/lookup.py"
    # legacy location used by older installers
    remove_dir "OpenClaw foundation (legacy)" "$OPENCLAW_ROOT/foundation"

    for soul in "$OPENCLAW_ROOT/workspace/SOUL.md" "$OPENCLAW_ROOT/workspace/soul.md" \
                "$OPENCLAW_ROOT/config/soul.md" "$OPENCLAW_ROOT/soul.md"; do
        [ -f "$soul" ] || continue
        if grep -q "HolySpiritOS:BEGIN" "$soul"; then
            # Surgical removal: delete only the marked block, keep everything else.
            sed -i.hsos-uninstall.bak '/HolySpiritOS:BEGIN/,/HolySpiritOS:END/d' "$soul"
            echo "✅ OpenClaw: removed HolySpiritOS block from $soul"
            echo "   (pre-removal copy kept at $soul.hsos-uninstall.bak)"
        elif grep -q "HolySpiritOS" "$soul"; then
            # Patched by an older installer without markers.
            if [ -f "$soul.bak" ]; then
                cp "$soul" "$soul.hsos-uninstall.bak"
                mv "$soul.bak" "$soul"
                echo "✅ OpenClaw: restored $soul from backup"
            else
                echo "⚠️ OpenClaw: $soul mentions HolySpiritOS but has no markers or backup."
                echo "   Please remove the HolySpiritOS lines from it manually."
            fi
        fi
    done
fi

echo "🕊️ HolySpiritOS uninstalled. Restart your agent to complete removal."
