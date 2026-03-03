"""
Abstract Repository interfaces for domain entities.
Follows the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from robbot.domain.leads.lead import Lead, Conversation


class LeadRepository(ABC):
    @abstractmethod
    def save(self, lead: Lead) -> None:
        pass

    @abstractmethod
    def get_by_id(self, lead_id: str) -> Optional[Lead]:
        pass

    @abstractmethod
    def get_by_phone(self, phone: str) -> Optional[Lead]:
        pass

    @abstractmethod
    def list_active(self) -> List[Lead]:
        pass


class ConversationRepositoryInterface(ABC):
    @abstractmethod
    def save(self, conversation: Conversation) -> None:
        pass

    @abstractmethod
    def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        pass

    @abstractmethod
    def get_by_chat_id(self, chat_id: str) -> Optional[Conversation]:
        pass

