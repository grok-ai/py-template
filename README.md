# py-template

A template to bootstrap Python projects following best practices in seconds.

## What It Does

```
┌─────────────────┐         ┌─────────────────────────────────┐
│  py-template    │         │  Your New Project               │
│  (this repo)    │         │                                 │
│                 │  ───►   │  ├── src/your_package/          │
│  Copier         │         │  │   ├── __init__.py            │
│  Template       │         │  │   └── utils.py               │
│                 │         │  ├── tests/                     │
└─────────────────┘         │  ├── pyproject.toml             │
                            │  ├── .pre-commit-config.yaml    │
                            │  └── .venv/ (ready to use)      │
                            └─────────────────────────────────┘
```

**What you get:**
- `get_project_root()` for finding the repo root (cached, lazy)
- `.env` files loaded automatically on import
- Built-in utilities (`get_env()`, `seed_everything()`, `environ()`)
- Pre-configured tooling (ruff, pytest, mypy, pre-commit)
- Git initialized with first commit

## Why Use This Template

| Problem | Solution |
|---------|----------|
| Copy-pasting boilerplate between projects | One command generates everything |
| Inconsistent project structure across teams | Standardized layout every time |
| Manual setup of linting, testing, env management | Best practices baked in |
| "Works on my machine" issues | Reproducible environments with uv |

## Quick Start

```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
uvx copier copy --trust gh:grok-ai/py-template my-project
```

Follow the prompts. That's it.

> **Pinning Copier version:** If you encounter issues, you can pin to a specific version:
> `uvx --from "copier==9.12.0" copier copy --trust gh:grok-ai/py-template my-project`

**What happens:**
```
🎤 Project name: my_project
🎤 Description: My awesome project
🎤 Initialize environment now? Yes
...
[1/5] Installing dependencies with uv...
[2/5] Initializing Git repository...
[3/5] Installing pre-commit hooks...
[4/5] Creating initial commit...
[5/5] Done!
```

## Using Your New Project

```bash
cd my-project

# Run your package
uv run python -m my_project

# Run tests
uv run pytest

# Add dependencies
uv add requests numpy

# Format and lint
uv run ruff check --fix .
uv run ruff format .
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `project_name` | folder name | Project name (can have hyphens/spaces; package name is derived automatically) |
| `description` | — | Short project description |
| `maintainers` | — | List of maintainers (name + email) |
| `remote_url` | `""` (empty) | Git remote URL (leave empty for no remote) |
| `push_to_remote` | `false` | Push initial commit to remote (only asked if remote_url is set) |
| `license` | `MIT` | `MIT` or `Apache-2.0` |
| `use_precommit` | `true` | Install pre-commit hooks |
| `extra_dependencies` | `[]` | Additional pip packages |
| `env_init` | `true` | Create virtualenv and install deps |
| `python_version` | `>=3.9` | Python version constraint |

## Advanced Usage

### Non-interactive Generation

Skip prompts by passing values directly:

```bash
uvx copier copy --trust \
  -d project_name=my_package \
  -d description="My project" \
  -d use_precommit=true \
  -d env_init=true \
  gh:grok-ai/py-template my-project
```

### Custom Dependencies

Add dependencies during generation:

```bash
uvx copier copy --trust \
  -d 'extra_dependencies=["requests", "numpy", "pandas"]' \
  gh:grok-ai/py-template my-project
```

### Remote Setup Options

Git is always initialized. The `remote_url` option controls remote configuration.

**No remote (default):**
```bash
# Git initialized, no remote configured. Add one later manually.
-d remote_url=""
```

**Add remote without pushing:**
```bash
# Remote configured, but doesn't push. You can push when ready.
-d remote_url=git@github.com:user/repo.git -d push_to_remote=false
```

**Add remote and push immediately:**
```bash
# Remote configured and pushes initial commit.
-d remote_url=git@github.com:user/repo.git -d push_to_remote=true
```

### Updating Existing Projects

Pull in template updates without losing your changes:

```bash
cd my-project
uvx copier update --trust
```

## Built-in Utilities

Your generated project includes these utilities in `utils.py`:

### get_project_root()

Returns the git repository root (cached after first call):

```python
from my_project import get_project_root

config_path = get_project_root() / "config.yaml"
```

Falls back to current working directory if not in a git repo.

### get_env()

Safe environment variable reading with defaults:

```python
from my_project.utils import get_env

api_key = get_env("API_KEY")                       # Raises KeyError if missing
debug = get_env("DEBUG", default="false")           # Returns default if missing/empty
```

### seed_everything()

Reproducible randomness for ML workflows:

```python
from my_project.utils import seed_everything

seed_everything(42)  # Seeds random, numpy, and torch (if installed)
```

### environ()

Temporary environment variable context manager:

```python
from my_project.utils import environ

with environ(API_KEY="secret", DEBUG="true"):
    # Variables set only within this block
    ...
# Original environment restored
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes locally:
   ```bash
   uvx copier copy --trust . /tmp/test-project
   ```
4. Submit a pull request

## License

MIT License. See [LICENSE](LICENSE) for details.

## Maintainers

- Valentino Maiorca ([@Flegyas](https://github.com/Flegyas))

---

**Questions or issues?** Open an issue at [github.com/grok-ai/py-template/issues](https://github.com/grok-ai/py-template/issues)
