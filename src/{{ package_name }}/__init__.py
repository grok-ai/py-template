import logging

from rich.logging import RichHandler
from rich.traceback import install

from .utils import get_project_root, load_envs

# Enable pretty tracebacks
install(show_locals=True)

# Set up Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

load_envs()

__all__ = ["get_project_root"]
