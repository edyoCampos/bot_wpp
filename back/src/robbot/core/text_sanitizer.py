"""Utilities for sanitizing outbound WhatsApp messages."""

import re


def enforce_whatsapp_style(text: str, max_paragraphs: int = 2) -> str:
    """
    Garante que a resposta tenha no máximo max_paragraphs parágrafos e remove racionalizações/metatextos.
    """
    # Remove racionalizações/metatextos comuns
    patterns = [
        r"\*?RACIONALIZAÇÃO DA RESPOSTA:?\*?",
        r"^Racionalização:?",
        r"^Rationalization:?",
        r"^Explicação:?",
        r"^Explanation:?",
        r"^RESPOSTA:?",
        r"^RESPONSE:?",
        r"^Resposta:?",
        r"^Response:?",
        r"^\*\*RESPOSTA\*\*:?.*",
        r"^\*\*(SITUATION|PROBLEM|IMPLICATION|NEED[_ ]PAYOFF)\*\*:?.*",
        r"^(SITUATION|PROBLEM|IMPLICATION|NEED[_ ]PAYOFF)\b.*",
        r"^#+\s*(SITUATION|PROBLEM|IMPLICATION|NEED[_ ]PAYOFF)\b.*",
        r"^\*\s*(SITUATION|PROBLEM|IMPLICATION|NEED[_ ]PAYOFF)\b.*",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE | re.MULTILINE).strip()

    # Remover variáveis de template vazadas (ex: {user_message})
    template_tokens = [
        "{message}",
        "{context}",
        "{history}",
        "{patient_info}",
        "{user_message}",
        "{response}",
        "{intent}",
        "{spin_phase}",
        "{maturity_score}",
        "{lead_status}",
        "{last_interaction}",
    ]
    for token in template_tokens:
        text = text.replace(token, "")

    # Limita a quantidade de parágrafos
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) > max_paragraphs:
        text = "\n\n".join(paragraphs[:max_paragraphs])
    return text
