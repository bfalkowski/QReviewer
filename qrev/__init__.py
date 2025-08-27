"""QReviewer - LLM-powered code review tool."""

__version__ = "0.1.0"

# Import main modules for easier access
from . import cli, cli_config, cli_learning, learning, standards
from . import github_review, report, diff, github_api, models
from . import llm_client, config, q_client, prompts

# Make learning functions available at top level
from .learning import learn_from_repository
from .cli_learning import learn, list_strategies
