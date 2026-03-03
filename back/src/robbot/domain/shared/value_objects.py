import re
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LeadScore:
    """
    Represents a lead's maturity score from 0 to 100.
    """
    value: int

    def __post_init__(self):
        # Ensure value is clamped between 0 and 100
        if not (0 <= self.value <= 100):
            object.__setattr__(self, 'value', max(0, min(100, self.value)))

    def apply_adjustment(self, amount: int) -> 'LeadScore':
        """Return a new LeadScore with adjusted value."""
        return LeadScore(self.value + amount)

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True)
class PhoneNumber:
    """
    Represents a contact phone number or WhatsApp JID.
    """
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("PhoneNumber cannot be empty")
        
    @property
    def is_whatsapp(self) -> bool:
        return "@s.whatsapp.net" in self.value or "@g.us" in self.value or "@c.us" in self.value

    def clean(self) -> str:
        """Returns only digits if not a JID."""
        if self.is_whatsapp:
            return self.value
        return re.sub(r"\D", "", self.value)


@dataclass(frozen=True)
class SpinPhase:
    """
    Represents the Current SPIN selling phase (Situation, Problem, Implication, Need-payoff).
    """
    phase: str  # 'S', 'P', 'I', 'N'

    def __post_init__(self):
        if self.phase.upper() not in ('S', 'P', 'I', 'N'):
            raise ValueError("SpinPhase must be one of S, P, I, N")
        object.__setattr__(self, 'phase', self.phase.upper())
