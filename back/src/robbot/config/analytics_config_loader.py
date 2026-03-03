"""Analytics configuration loader and helpers."""

from pathlib import Path
from typing import Any

import yaml


class AnalyticsConfig:
    """
    Gerencia configurações de analytics (stop words, topics, sentiment).

    Carrega de analytics_config.yaml e fornece acesso tipado.
    """

    def __init__(self, config_path: Path | None = None):
        """
        Inicializa configuração de analytics.

        Args:
            config_path: Caminho para analytics_config.yaml. Se None, usa default.
        """
        if config_path is None:
            # Default: mesmo diretório deste arquivo
            config_path = Path(__file__).parent / "analytics_config.yaml"

        with open(config_path, encoding="utf-8") as f:
            self._config: dict[str, Any] = yaml.safe_load(f)

    @property
    def stop_words(self) -> list[str]:
        """Retorna lista de stop words para análise de keywords."""
        return self._config.get("stop_words", [])

    @property
    def sentiment_keywords(self) -> dict[str, list[str]]:
        """
        Retorna dicionário de keywords de sentimento.

        Returns:
            {
                "positive": ["obrigad", "legal", ...],
                "negative": ["ruim", "péssimo", ...],
                "neutral": ["dúvida", ...],
                "negation_modifiers": ["não", "nem", ...]
            }
        """
        return self._config.get("sentiment_keywords", {})

    @property
    def topics(self) -> dict[str, list[str]]:
        """
        Retorna mapeamento de topics para keywords.

        Returns:
            {
                "Agendamento": ["agendar", "consulta", ...],
                "Preços": ["preço", "valor", ...],
                ...
            }
        """
        return self._config.get("topics", {})

    @property
    def performance_thresholds(self) -> dict[str, Any]:
        """
        Retorna thresholds de performance.

        Returns:
            {
                "latency_ms": 5000,
                "error_rate_percent": 5.0,
                ...
            }
        """
        return self._config.get("performance_thresholds", {})

    @property
    def cache_ttl(self) -> dict[str, int]:
        """
        Retorna configurações de TTL de cache.

        Returns:
            {
                "realtime": 30,
                "metrics": 900,
                "historical": 3600,
                "reports": 1800
            }
        """
        return self._config.get("cache_ttl", {})

    def build_stop_words_sql_array(self) -> str:
        """
        Constrói ARRAY['word1', 'word2', ...] para uso em SQL.

        Returns:
            "ARRAY['para', 'com', 'que', ...]"
        """
        words = "', '".join(self.stop_words)
        return f"ARRAY['{words}']"

    def build_sentiment_regex(self, sentiment: str) -> str:
        """
        Constrói regex para detecção de sentimento.

        Args:
            sentiment: 'positive', 'negative', ou 'neutral'

        Returns:
            '(palavra1|palavra2|palavra3|...)' para uso em SQL
        """
        keywords = self.sentiment_keywords.get(sentiment, [])
        if not keywords:
            return ""

        # Escape caracteres especiais de regex
        escaped = [k.replace("(", r"\(").replace(")", r"\)") for k in keywords]
        return "(" + "|".join(escaped) + ")"

    def build_topic_sql_cases(self) -> str:
        """
        Constrói CASE WHEN para classificação de topics em SQL.

        Returns:
            CASE
                WHEN LOWER(body) ~ '(agendar|consulta|...)' THEN 'Agendamento'
                WHEN LOWER(body) ~ '(preço|valor|...)' THEN 'Preços'
                ...
                ELSE 'Outros'
            END
        """
        cases = []
        for topic_name, keywords in self.topics.items():
            if topic_name == "Outros" or not keywords:
                continue

            # Escape e build regex pattern
            escaped = [k.replace("(", r"\(").replace(")", r"\)") for k in keywords]
            pattern = "(" + "|".join(escaped) + ")"
            cases.append(f"WHEN LOWER(body) ~ '{pattern}' THEN '{topic_name}'")

        cases_str = "\n                ".join(cases)
        return f"""CASE
                {cases_str}
                ELSE 'Outros'
            END"""


# Singleton global
_analytics_config: AnalyticsConfig | None = None


def get_analytics_config() -> AnalyticsConfig:
    """
    Retorna singleton de AnalyticsConfig.

    Returns:
        Instância singleton de AnalyticsConfig
    """
    global _analytics_config
    if _analytics_config is None:
        _analytics_config = AnalyticsConfig()
    return _analytics_config
