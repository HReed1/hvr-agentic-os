#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXT_ROOT="$HOME/.copilot/extensions"
TARGET_LINK="$EXT_ROOT/project-bootstrap"

echo "============================================================"
echo "  Installing project-bootstrap GitHub Copilot CLI Extension"
echo "============================================================"

# 1. Ensure ~/.copilot/extensions exists
mkdir -p "$EXT_ROOT"

# 2. Symlink the extension directory
ln -sfn "$SCRIPT_DIR" "$TARGET_LINK"

echo "✅ Symlink created:"
echo "   Target: $TARGET_LINK"
echo "   Source: $SCRIPT_DIR"
echo ""
echo "Installation complete! To use with Copilot CLI:"
echo "  1. Navigate to any project directory"
echo "  2. Run 'copilot'"
echo "  3. Ask Copilot: 'Bootstrap this repo as a software engineering workspace'"
echo "============================================================"
