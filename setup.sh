#!/bin/bash
set -e # Exit on error

# Ask for project name if not provided
if [ -z "$1" ]; then
    read -p "Enter the target folder name: " folder_name
else
    folder_name="$1"
fi

# Validate project name
if [ -z "$folder_name" ]; then
    echo "❌ Folder name cannot be empty!"
    exit 1
fi

echo "🚀 Checking for 'uv' installation..."

# Install 'uv' if missing
if ! command -v uv &>/dev/null; then
    echo "🔧 'uv' not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" # Ensure UV is in PATH
fi

echo "✅ 'uv' is installed!"

# Get copier version from copier.yml (single source of truth)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COPIER_VERSION=$(grep '_min_copier_version:' "$SCRIPT_DIR/copier.yml" | sed 's/.*: *"\(.*\)"/\1/')

# Run Copier using UVX (no global install)
echo "📦 Running Copier for project '$folder_name'..."
uvx --from "copier==$COPIER_VERSION" copier copy --trust gh:grok-ai/py-template "$folder_name"

echo "🎉 Done! Your project is ready in '$folder_name'."
