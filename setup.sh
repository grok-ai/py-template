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

# Run Copier using UVX (no global install needed)
# To pin a specific version, use: uvx --from "copier==9.12.0" copier copy ...
echo "📦 Running Copier for project '$folder_name'..."
uvx copier copy --trust gh:grok-ai/py-template "$folder_name"

echo "🎉 Done! Your project is ready in '$folder_name'."
