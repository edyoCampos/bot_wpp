"""__init__.py for prompts package."""

from robbot.config.prompts.templates import (
    PromptTemplates,
    get_prompt_templates,
)

__all__ = [
    "PromptTemplates",
    "get_prompt_templates",
]
