"""
Load and manage prompt templates from YAML configuration file.

Resolves Issue #6: Hard-Coded Prompt Configuration
"""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("robbot.config.prompt_loader")


class PromptLoader:
    """
    Load and manage prompt templates from YAML configuration file.

    Enables easy customization of prompts without code changes.
    Supports multiple template versions for A/B testing.
    """

    def __init__(self, prompts_path: str | Path):
        """
        Initialize prompt loader.

        Args:
            prompts_path: Path to prompts.yaml configuration file

        Raises:
            FileNotFoundError: If prompts.yaml does not exist
            yaml.YAMLError: If YAML syntax is invalid
        """
        self.prompts_path = Path(prompts_path)

        if not self.prompts_path.exists():
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_path}")

        self._prompts = self._load_prompts()
        logger.info("Loaded %d prompt templates from %s", len(self._prompts), self.prompts_path)

    def _load_prompts(self) -> dict[str, Any]:
        """
        Load prompts from YAML file.

        Returns:
            Dictionary with prompt templates keyed by name
        """
        try:
            with open(self.prompts_path, encoding="utf-8") as f:
                prompts = yaml.safe_load(f)
                return prompts or {}
        except yaml.YAMLError as e:
            logger.error("Failed to parse YAML: %s", e)
            raise

    def get_prompt(self, name: str) -> str:
        """
        Get prompt template by name.

        Args:
            name: Prompt template name (e.g., "intent_detection", "response_generation")

        Returns:
            Prompt template string

        Raises:
            KeyError: If prompt name not found
        """
        if name not in self._prompts:
            available = list(self._prompts.keys())
            raise KeyError(f"Prompt '{name}' not found. Available: {available}")

        return self._prompts[name]

    def format_intent_detection_prompt(self, message: str, context: str = "") -> str:
        """
        Format intent detection prompt with message and context.

        Args:
            message: User message to analyze
            context: Previous conversation context

        Returns:
            Formatted prompt ready for LLM
        """
        template = self.get_prompt("intent_detection")
        return template.format(message=message, context=context)

    def format_response_generation_prompt(
        self,
        user_message: str,
        conversation_history: str,
        patient_info: str = "",
        questions_asked: list[str] | None = None,
        conversation_summary: str = "",
    ) -> str:
        """
        Format response generation prompt.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            patient_info: Patient context (name, status, etc.)
            questions_asked: List of questions already asked
            conversation_summary: Summary of known facts

        Returns:
            Formatted prompt ready for LLM
        """
        template = self.get_prompt("response_generation")
        
        # Format questions_asked as string
        questions_str = ", ".join(questions_asked) if questions_asked else "None"
        
        return template.format(
            user_message=user_message,
            history=conversation_history,
            patient_info=patient_info,
            questions_asked=questions_str,
            conversation_summary=conversation_summary or "No conversation summary yet",
        )

    def format_urgency_detection_prompt(self, message: str) -> str:
        """
        Format urgency detection prompt.

        Args:
            message: User message to analyze

        Returns:
            Formatted prompt ready for LLM
        """
        template = self.get_prompt("urgency_detection")
        return template.format(message=message)

    def reload(self) -> None:
        """Reload prompts from YAML file (for development)."""
        self._prompts = self._load_prompts()
        logger.info("Reloaded %d prompt templates", len(self._prompts))

    @property
    def all_prompts(self) -> dict[str, Any]:
        """Get all loaded prompts (read-only)."""
        return dict(self._prompts)
