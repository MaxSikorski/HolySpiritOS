#!/bin/bash
# HolySpiritOS installer — KJV 1769 grounding skill for AI agents.
# https://github.com/MaxSikorski/HolySpiritOS
#
# Usage:
#   ./scripts/install.sh              # auto-detect installed agents
#   ./scripts/install.sh claude       # Claude Code   -> ~/.claude/skills/
#   ./scripts/install.sh codex        # Codex CLI     -> ~/.codex/skills/
#   ./scripts/install.sh antigravity  # Antigravity   -> ~/.gemini/antigravity-cli/skills/
#   ./scripts/install.sh openclaw     # OpenClaw      -> foundation + soul.md patch
#   ./scripts/install.sh project      # this repo     -> ./.agents/skills/ (shared standard)
#   ./scripts/install.sh all          # every agent found on this machine

set -euo pipefail

REPO_RAW_URL="https://raw.githubusercontent.com/MaxSikorski/HolySpiritOS/main"
SKILL_NAME="holy-spirit-os"
SKILL_SRC="skills/holy-spirit-os"
SKILL_FILES="SKILL.md foundation/verses-1769.json foundation/kjv-metadata.json scripts/lookup.py"

# Where is this script running from? If inside a clone, copy locally; else download.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
LOCAL_ROOT=""
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/../$SKILL_SRC/SKILL.md" ]; then
    LOCAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

fetch() { # fetch <relative-path> <destination-file>
    mkdir -p "$(dirname "$2")"
    if [ -n "$LOCAL_ROOT" ]; then
        cp "$LOCAL_ROOT/$1" "$2"
    else
        curl -fsSL "$REPO_RAW_URL/$1" -o "$2"
    fi
}

install_skill_dir() { # install_skill_dir <label> <target-dir>
    local label="$1" target="$2"
    echo "📖 Installing $SKILL_NAME for $label -> $target"
    for f in $SKILL_FILES; do
        fetch "$SKILL_SRC/$f" "$target/$f"
    done
    if command -v python3 >/dev/null 2>&1; then
        if python3 "$target/scripts/lookup.py" --self-test >/dev/null 2>&1; then
            echo "✅ $label: installed and self-test passed."
        else
            echo "⚠️ $label: installed, but self-test failed — run: python3 $target/scripts/lookup.py --self-test"
        fi
    else
        echo "✅ $label: installed (python3 not found; skipped self-test)."
    fi
}

install_openclaw() {
    local root="$HOME/.openclaw"
    if [ ! -d "$root" ]; then
        echo "❌ OpenClaw not found at $root — skipping."
        return 1
    fi
    local foundation="$root/workspace/foundation"
    echo "📖 Installing foundation for OpenClaw -> $foundation"
    fetch "$SKILL_SRC/foundation/verses-1769.json" "$foundation/verses-1769.json"
    fetch "$SKILL_SRC/foundation/kjv-metadata.json" "$foundation/kjv-metadata.json"
    fetch "$SKILL_SRC/scripts/lookup.py" "$foundation/../scripts/lookup.py"

    # Find the soul file (location varies between OpenClaw versions).
    local soul=""
    for candidate in "$root/workspace/SOUL.md" "$root/workspace/soul.md" \
                     "$root/config/soul.md" "$root/soul.md"; do
        if [ -f "$candidate" ]; then soul="$candidate"; break; fi
    done
    if [ -z "$soul" ]; then
        soul="$root/workspace/SOUL.md"
        mkdir -p "$(dirname "$soul")"
        touch "$soul"
        echo "ℹ️ No existing soul file found; created $soul"
    fi

    if grep -q "HolySpiritOS:BEGIN" "$soul"; then
        echo "⚠️ OpenClaw: soul already anchored ($soul). Skipping patch."
    else
        cp "$soul" "$soul.bak"
        echo "🗄️ Backup created: $soul.bak"
        echo "" >> "$soul"
        fetch "adapters/openclaw/soul_patch.md" "/tmp/hsos_soul_patch.$$"
        cat "/tmp/hsos_soul_patch.$$" >> "$soul"
        rm -f "/tmp/hsos_soul_patch.$$"
        echo "✅ OpenClaw: soul patched ($soul). Restart your OpenClaw instance."
    fi
}

TARGET="${1:-auto}"
INSTALLED=0

do_target() {
    case "$1" in
        claude)      install_skill_dir "Claude Code" "$HOME/.claude/skills/$SKILL_NAME" ;;
        codex)       install_skill_dir "Codex CLI" "$HOME/.codex/skills/$SKILL_NAME" ;;
        antigravity) install_skill_dir "Antigravity" "$HOME/.gemini/antigravity-cli/skills/$SKILL_NAME" ;;
        project)     install_skill_dir "this project (.agents/skills)" "$PWD/.agents/skills/$SKILL_NAME" ;;
        openclaw)    install_openclaw ;;
        *) echo "❌ Unknown target: $1 (use claude|codex|antigravity|openclaw|project|all)"; exit 1 ;;
    esac
    INSTALLED=$((INSTALLED + 1))
}

echo "🕊️ HolySpiritOS installer"
if [ "$TARGET" = "auto" ] || [ "$TARGET" = "all" ]; then
    [ -d "$HOME/.claude" ]   && do_target claude
    [ -d "$HOME/.codex" ]    && do_target codex
    [ -d "$HOME/.gemini/antigravity-cli" ] && do_target antigravity
    [ -d "$HOME/.openclaw" ] && do_target openclaw
    if [ "$INSTALLED" -eq 0 ]; then
        echo "❌ No supported agent found (looked for ~/.claude, ~/.codex,"
        echo "   ~/.gemini/antigravity-cli, ~/.openclaw)."
        echo "   Pick a target explicitly: install.sh claude|codex|antigravity|openclaw|project"
        exit 1
    fi
else
    do_target "$TARGET"
fi

echo "✨ Done. Ask your agent about an ethical or spiritual question to see it in action."
