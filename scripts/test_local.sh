#!/bin/bash
# Local test script for py-template development
# Usage: bash scripts/test_local.sh [project_name] [--with-tests]
#
# Arguments:
#   project_name    Name for the generated project (default: test-project)
#   --with-tests    Also run pytest in the generated project

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME=""
RUN_TESTS=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --with-tests)
            RUN_TESTS=true
            ;;
        *)
            if [ -z "$PROJECT_NAME" ]; then
                PROJECT_NAME="$arg"
            fi
            ;;
    esac
done
PROJECT_NAME="${PROJECT_NAME:-test-project}"

# Create temp directory
OUTPUT_DIR=$(mktemp -d -t "py-template-test-XXXXXX")
PROJECT_DIR="$OUTPUT_DIR/$PROJECT_NAME"

echo "=== py-template Local Test ==="
echo "Template directory: $TEMPLATE_DIR"
echo "Output directory: $OUTPUT_DIR"
echo "Project name: $PROJECT_NAME"
echo ""

# Configure git via env vars
export GIT_AUTHOR_NAME="Test User"
export GIT_AUTHOR_EMAIL="test@example.com"
export GIT_COMMITTER_NAME="Test User"
export GIT_COMMITTER_EMAIL="test@example.com"
export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0="init.defaultBranch"
export GIT_CONFIG_VALUE_0="main"

# Get copier version from copier.yml (single source of truth)
COPIER_VERSION=$(grep '_min_copier_version:' "$TEMPLATE_DIR/copier.yml" | sed 's/.*: *"\(.*\)"/\1/')

# Generate project
echo "[1/4] Generating project..."
uvx --from "copier==$COPIER_VERSION" copier copy --trust --force "$TEMPLATE_DIR" "$PROJECT_DIR" \
    -d project_name="$PROJECT_NAME" \
    -d description="A test project generated locally" \
    -d remote_url="" \
    -d use_precommit=true \
    -d env_init=true \
    -d "extra_dependencies=[]" \
    -d license="MIT"

PACKAGE_NAME=$(echo "$PROJECT_NAME" | tr '[:upper:] -' '[:lower:]__')

echo "[2/4] Verifying project structure..."
if [ ! -d "$PROJECT_DIR/src/$PACKAGE_NAME" ]; then
    echo "ERROR: Package directory not found at src/$PACKAGE_NAME"
    exit 1
fi
if [ ! -f "$PROJECT_DIR/pyproject.toml" ]; then
    echo "ERROR: pyproject.toml not found"
    exit 1
fi
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "ERROR: Git not initialized"
    exit 1
fi
echo "  - Package directory exists"
echo "  - pyproject.toml exists"
echo "  - Git initialized"

echo "[3/4] Checking for common bugs..."
# Check for undefined variables in README
if grep -q "{{ project_name }}" "$PROJECT_DIR/README.md" 2>/dev/null; then
    echo "ERROR: README.md contains undefined project_name variable"
    exit 1
fi
echo "  - No undefined variables in README"

# Check for self-referential dependency
if grep -q "\"$PROJECT_NAME\"" "$PROJECT_DIR/pyproject.toml" 2>/dev/null; then
    # Check if it's in dependencies section (not just name field)
    if awk '/dependencies = \[/,/\]/' "$PROJECT_DIR/pyproject.toml" | grep -q "\"$PROJECT_NAME\""; then
        echo "ERROR: Package has self-referential dependency"
        exit 1
    fi
fi
echo "  - No self-referential dependency"

# Check pre-commit setup
if [ ! -f "$PROJECT_DIR/.pre-commit-config.yaml" ]; then
    echo "ERROR: .pre-commit-config.yaml not found"
    exit 1
fi
if ! grep -q "repos:" "$PROJECT_DIR/.pre-commit-config.yaml"; then
    echo "ERROR: .pre-commit-config.yaml has no repos defined"
    exit 1
fi
if [ ! -f "$PROJECT_DIR/.git/hooks/pre-commit" ]; then
    echo "ERROR: pre-commit hooks not installed"
    exit 1
fi
echo "  - Pre-commit config exists with hooks installed"

if [ "$RUN_TESTS" = true ]; then
    echo "[4/4] Running tests in generated project..."
    cd "$PROJECT_DIR"
    uv run pytest tests -v
else
    echo "[4/4] Skipping tests (use --with-tests to run)"
fi

echo ""
echo "=== Test Complete ==="
echo "Generated project at: $PROJECT_DIR"
echo ""
echo "To explore the generated project:"
echo "  cd $PROJECT_DIR"
echo ""
echo "To run tests:"
echo "  cd $PROJECT_DIR && uv run pytest tests -v"
echo ""
echo "To clean up:"
echo "  rm -rf $OUTPUT_DIR"
