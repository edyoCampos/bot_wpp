"""
AnsweredQuestionsMemory: Simple in-memory tracker for answered user questions in a conversation.
- Stores hashes or normalized forms of user questions.
- Allows checking if a question was already answered.
- Can be extended to persistent storage if needed.
"""


class AnsweredQuestionsMemory:
    def __init__(self):
        self.answered: set[str] = set()

    def normalize(self, question: str) -> str:
        # Lowercase, strip, remove punctuation for basic normalization
        import re

        return re.sub(r"[^\w\s]", "", question.strip().lower())

    def add(self, question: str):
        self.answered.add(self.normalize(question))

    def was_answered(self, question: str) -> bool:
        return self.normalize(question) in self.answered

    def reset(self):
        self.answered.clear()
