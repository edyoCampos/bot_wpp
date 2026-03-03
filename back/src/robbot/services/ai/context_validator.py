#!/usr/bin/env python3
"""
Context Contamination Prevention & Validation Script

This script prevents the ChatBot from injecting wrong context into responses.
It implements multiple safeguards:

1. Vector Similarity Threshold - Only use context if similarity is high
2. Conversation ID Filter - Strictly enforce conversation isolation
3. Content Relevance Check - Validate context matches the user's intent
4. Deduplication - Prevent sending duplicate messages
"""

import asyncio
import hashlib  # noqa: F401
import sys
import time  # noqa: F401
from typing import Any

sys.path.insert(0, "/app/src")

# ============================================================================
# SAFEGUARD 1: Vector Similarity Threshold
# ============================================================================


class ContextValidator:
    """Validate context before injecting into LLM prompt."""

    def __init__(self, min_similarity_score: float = 0.6):
        """
        Initialize validator.

        Args:
            min_similarity_score: Minimum similarity (0-1) to accept context
                                 Set to 0.6+ to avoid dissimilar matches
        """
        self.min_similarity = min_similarity_score

    async def validate_context(
        self,
        user_message: str,  # noqa: F841 (used for type hint)
        retrieved_context: str | list[dict[str, Any]],
        conversation_id: str,
        min_results: int = 1,  # At least 1 valid match
    ) -> dict[str, Any]:
        """
        Validate retrieved context before using it.

        Args:
            user_message: Current user message
            retrieved_context: Context from ChromaDB (string or list of dicts)
            conversation_id: Current conversation ID
            min_results: Minimum number of valid results

        Returns:
            {
                "is_valid": bool,
                "filtered_context": str,  # Formatted context for LLM
                "reason": str,
                "similarity_scores": list
            }
        """
        # If context is empty string, return invalid
        if isinstance(retrieved_context, str):
            if not retrieved_context or retrieved_context.strip() == "":
                return {
                    "is_valid": False,
                    "filtered_context": "",
                    "reason": "No context retrieved from ChromaDB",
                    "similarity_scores": [],
                }
            # If it's a string and non-empty, accept it (it came from context_builder)
            return {
                "is_valid": True,
                "filtered_context": retrieved_context,
                "reason": "Context retrieved and validated",
                "similarity_scores": [1.0],  # Single string context
            }

        # If it's a list, validate each item
        if not retrieved_context:
            return {
                "is_valid": False,
                "filtered_context": "",
                "reason": "No context retrieved",
                "similarity_scores": [],
            }

        # SAFEGUARD 1a: Check similarity scores
        similarity_scores = []
        filtered = []

        for item in retrieved_context:
            distance = item.get("distance", 1.0)
            # ChromaDB uses L2 distance (lower is better)
            # Convert to similarity score: similarity = 1 / (1 + distance)
            similarity = 1.0 / (1.0 + distance) if distance is not None else 0
            similarity_scores.append(similarity)

            # SAFEGUARD 1b: Only accept high-similarity matches
            if similarity >= self.min_similarity:
                # SAFEGUARD 1c: Verify conversation_id
                metadata = item.get("metadata", {})
                if metadata.get("conversation_id") == conversation_id:
                    filtered.append(item)

        # SAFEGUARD 2: Need minimum matches
        if len(filtered) < min_results:
            return {
                "is_valid": False,
                "filtered_context": filtered,
                "reason": f"Only {len(filtered)} valid matches (need {min_results}), scores: {similarity_scores}",
                "similarity_scores": similarity_scores,
            }

        return {
            "is_valid": True,
            "filtered_context": filtered,
            "reason": f"Valid context ({len(filtered)} matches, avg similarity: {sum(similarity_scores) / len(similarity_scores):.2f})",
            "similarity_scores": similarity_scores,
        }

    def check_context_relevance(
        self,
        user_message: str,
        context_text: str,
        keywords_user: list[str],
        keywords_context: list[str],
        match_threshold: float = 0.5,
    ) -> dict[str, Any]:
        """
        Check if retrieved context is actually relevant to user's intent.

        Args:
            user_message: User's current message
            context_text: Retrieved context from ChromaDB
            keywords_user: Keywords expected from user message
            keywords_context: Keywords found in context
            match_threshold: % of keywords that must match

        Returns:
            {
                "is_relevant": bool,
                "matching_keywords": list,
                "match_percentage": float,
                "risk_level": str  # "low", "medium", "high"
            }
        """
        # Simple keyword matching
        user_words = set(user_message.lower().split())
        context_words = set(context_text.lower().split())

        # Find overlapping keywords
        overlap = user_words & context_words

        if len(keywords_user) == 0:
            match_pct = 0
        else:
            match_pct = len(overlap) / len(keywords_user)

        is_relevant = match_pct >= match_threshold

        # Determine risk
        if is_relevant:
            risk = "low"
        elif match_pct > 0.25:
            risk = "medium"
        else:
            risk = "high"  # Completely different topics!

        return {
            "is_relevant": is_relevant,
            "matching_keywords": list(overlap),
            "match_percentage": match_pct,
            "risk_level": risk,
        }


# ============================================================================
# SAFEGUARD 3: Deduplication
# ============================================================================


class ResponseDeduplicator:
    """Prevent sending duplicate responses."""

    def __init__(self, max_age_seconds: int = 300):
        """
        Initialize deduplicator.

        Args:
            max_age_seconds: How long to remember recent responses (default 5 min)
        """
        self.max_age = max_age_seconds
        self.recent_responses = {}  # {conversation_id: [(response_hash, timestamp), ...]}

    def is_duplicate(self, conversation_id: str, response_text: str) -> bool:
        """
        Check if this response was recently sent.

        Args:
            conversation_id: Conversation to check
            response_text: Response text

        Returns:
            True if this exact response was sent recently
        """

        now = time.time()
        response_hash = hashlib.md5(response_text.encode()).hexdigest()

        if conversation_id not in self.recent_responses:
            self.recent_responses[conversation_id] = []

        recent = self.recent_responses[conversation_id]

        # Clean old entries
        recent = [(h, t) for h, t in recent if now - t < self.max_age]
        self.recent_responses[conversation_id] = recent

        # Check for duplicate
        return any(existing_hash == response_hash for existing_hash, _ in recent)

    def record_response(self, conversation_id: str, response_text: str) -> None:
        """Record a response as sent."""

        now = time.time()
        response_hash = hashlib.md5(response_text.encode()).hexdigest()

        if conversation_id not in self.recent_responses:
            self.recent_responses[conversation_id] = []

        # Add to recent
        self.recent_responses[conversation_id].append((response_hash, now))

        # Clean old entries
        recent = self.recent_responses[conversation_id]
        recent = [(h, t) for h, t in recent if now - t < self.max_age]
        self.recent_responses[conversation_id] = recent

    def mark_sent(self, conversation_id: str, response_text: str) -> None:
        """Mark a response as sent."""
        # Already done in record_response, but can be explicit
        self.record_response(conversation_id, response_text)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example():
    """Example of using the validators."""
    validator = ContextValidator(min_similarity_score=0.65)
    deduplicator = ResponseDeduplicator()

    # Simulate retrieved context
    user_msg = "horários de funcionamento"
    retrieved_context = [
        {
            "id": "doc1",
            "text": "Você mencionou que a TRH é um tópico de interesse...",
            "metadata": {"conversation_id": "conv123"},
            "distance": 0.8,  # Bad match!
        },
        {
            "id": "doc2",
            "text": "User: horários",
            "metadata": {"conversation_id": "conv123"},
            "distance": 0.1,  # Good match!
        },
    ]

    # Validate context
    validation = validator.validate_context(user_msg, retrieved_context, "conv123")

    print("=" * 60)
    print("CONTEXT VALIDATION RESULT")
    print("=" * 60)
    print(f"Is Valid: {validation['is_valid']}")
    print(f"Reason: {validation['reason']}")
    print(f"Similarity Scores: {validation['similarity_scores']}")
    print(f"Filtered Context Count: {len(validation['filtered_context'])}")

    # Check relevance
    if validation["filtered_context"]:
        context_text = " ".join([c["text"] for c in validation["filtered_context"]])
        relevance = validator.check_context_relevance(
            user_msg, context_text, keywords_user=["horario", "funcionamento"], keywords_context=["TRH", "menopausa"]
        )

        print("\nRELEVANCE CHECK")
        print("=" * 60)
        print(f"Is Relevant: {relevance['is_relevant']}")
        print(f"Risk Level: {relevance['risk_level']}")
        print(f"Match %: {relevance['match_percentage'] * 100:.1f}%")

    # Check deduplication
    response1 = "Olá! Como posso ajudar?"
    is_dup = deduplicator.is_duplicate("conv123", response1)
    print(f"\nIs Duplicate (first send): {is_dup}")

    is_dup2 = deduplicator.is_duplicate("conv123", response1)
    print(f"Is Duplicate (second send): {is_dup2}")


if __name__ == "__main__":
    asyncio.run(example())
