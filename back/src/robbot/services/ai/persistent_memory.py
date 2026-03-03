"""
Persistent Memory - Redis-based memory for conversation tracking.

Tracks:
- Questions already asked to prevent repetition
- Key facts about the conversation
- Handoff triggers and reasons
"""

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from robbot.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PersistentMemory:
    """Redis-based persistent memory for conversations."""

    def __init__(self):
        self.redis_client: aioredis.Redis | None = None

    async def _get_client(self) -> aioredis.Redis:
        """Get or create Redis client."""
        if self.redis_client is None:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        return self.redis_client

    async def add_question(self, conversation_id: str, question: str) -> None:
        """
        Add a question to the memory (prevent re-asking).

        Args:
            conversation_id: Conversation ID
            question: Normalized question text
        """
        try:
            client = await self._get_client()
            key = f"questions:{conversation_id}"
            
            # Normalize question (lowercase, strip)
            normalized = question.lower().strip()
            
            # Add to set (automatically deduplicates)
            await client.sadd(key, normalized)
            
            # Expire after 7 days
            await client.expire(key, 60 * 60 * 24 * 7)
            
            logger.debug("[MEMORY] Added question: %s", normalized)

        except Exception as e:
            logger.warning("[MEMORY] Failed to add question: %s", e)

    async def was_asked(self, conversation_id: str, question: str) -> bool:
        """
        Check if question was already asked.

        Args:
            conversation_id: Conversation ID
            question: Question to check

        Returns:
            True if already asked
        """
        try:
            client = await self._get_client()
            key = f"questions:{conversation_id}"
            
            normalized = question.lower().strip()
            
            result = await client.sismember(key, normalized)
            
            if result:
                logger.warning("[MEMORY] Question already asked: %s", normalized)
            
            return bool(result)

        except Exception as e:
            logger.warning("[MEMORY] Failed to check question: %s", e)
            return False

    async def get_all_questions(self, conversation_id: str) -> list[str]:
        """Get all questions asked in this conversation."""
        try:
            client = await self._get_client()
            key = f"questions:{conversation_id}"
            
            questions = await client.smembers(key)
            
            return list(questions) if questions else []

        except Exception as e:
            logger.warning("[MEMORY] Failed to get questions: %s", e)
            return []

    async def save_fact(self, conversation_id: str, fact_key: str, fact_value: Any) -> None:
        """
        Save a fact about the conversation.

        Args:
            conversation_id: Conversation ID
            fact_key: Fact identifier (e.g., "patient_name", "has_done_procedure_before")
            fact_value: Fact value
        """
        try:
            client = await self._get_client()
            key = f"facts:{conversation_id}"
            
            # Store as JSON
            await client.hset(key, fact_key, json.dumps(fact_value))
            
            # Expire after 7 days
            await client.expire(key, 60 * 60 * 24 * 7)
            
            logger.debug("[MEMORY] Saved fact: %s = %s", fact_key, fact_value)

        except Exception as e:
            logger.warning("[MEMORY] Failed to save fact: %s", e)

    async def get_fact(self, conversation_id: str, fact_key: str) -> Any | None:
        """Get a fact about the conversation."""
        try:
            client = await self._get_client()
            key = f"facts:{conversation_id}"
            
            value = await client.hget(key, fact_key)
            
            if value:
                return json.loads(value)
            
            return None

        except Exception as e:
            logger.warning("[MEMORY] Failed to get fact: %s", e)
            return None

    async def get_all_facts(self, conversation_id: str) -> dict[str, Any]:
        """Get all facts about the conversation."""
        try:
            client = await self._get_client()
            key = f"facts:{conversation_id}"
            
            facts = await client.hgetall(key)
            
            if facts:
                return {k: json.loads(v) for k, v in facts.items()}
            
            return {}

        except Exception as e:
            logger.warning("[MEMORY] Failed to get all facts: %s", e)
            return {}

    async def should_handoff(self, conversation_id: str, reason: str) -> bool:
        """
        Check if handoff should be triggered.

        Args:
            conversation_id: Conversation ID
            reason: Handoff reason (e.g., "scheduling_ready", "unknown_question", "payment_question")

        Returns:
            True if handoff should be triggered
        """
        try:
            # Trigger handoff for these reasons
            handoff_triggers = {
                "scheduling_ready",      # Patient wants to schedule
                "unknown_question",      # Bot doesn't know the answer
                "payment_question",      # Payment methods, installments
                "calendar_access",       # Needs to check availability
                "high_score",           # Maturity score > 75
                "bot_confused",         # Bot is unsure how to respond
            }
            
            if reason in handoff_triggers:
                logger.info("[HANDOFF] Trigger activated: %s", reason)
                
                # Save handoff reason
                await self.save_fact(conversation_id, "handoff_reason", reason)
                
                return True
            
            return False

        except Exception as e:
            logger.warning("[HANDOFF] Failed to check handoff: %s", e)
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.aclose()
            self.redis_client = None

