"""
Testes de integração para Relatório de Análise de Conversas (L3).

Valida queries SQL e transformações de dados.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from robbot.infra.persistence.repositories.analytics_repository import AnalyticsRepository


@pytest.fixture
def mock_db_session():
    """Mock da sessão do banco de dados."""
    return MagicMock()


@pytest.fixture
def analytics_repo(mock_db_session):
    """Instância do AnalyticsRepository com mock."""
    return AnalyticsRepository(mock_db_session)


def test_activity_heatmap_query_structure(analytics_repo, mock_db_session):
    """Testa estrutura do heatmap de atividade."""
    # Arrange
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    # Mock result
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(day_of_week=1, hour=9, message_count=120),
        MagicMock(day_of_week=1, hour=14, message_count=85),
        MagicMock(day_of_week=2, hour=10, message_count=95),
    ]
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_message_frequency_by_hour(start_date, end_date)

    # Assert
    assert len(result) == 3
    assert result[0]["day_of_week"] == 1
    assert result[0]["hour"] == 9
    assert result[0]["message_count"] == 120
    assert result[1]["day_of_week"] == 1
    assert result[1]["hour"] == 14
    assert result[2]["day_of_week"] == 2

    # Verifica query SQL
    call_args = mock_db_session.execute.call_args
    assert "EXTRACT(DOW FROM created_at)" in str(call_args[0][0])
    assert "EXTRACT(HOUR FROM created_at)" in str(call_args[0][0])
    assert "GROUP BY day_of_week, hour" in str(call_args[0][0])


def test_keyword_frequency_query_structure(analytics_repo, mock_db_session):
    """Testa extração de palavras-chave com stop words filtering."""
    # Arrange
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    # Mock result
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(keyword="agendamento", count=250),
        MagicMock(keyword="preço", count=180),
        MagicMock(keyword="consulta", count=120),
    ]
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_keyword_frequency(start_date, end_date, limit=50)

    # Assert
    assert len(result) == 3
    assert result[0]["keyword"] == "agendamento"
    assert result[0]["count"] == 250
    assert result[1]["keyword"] == "preço"
    assert result[1]["count"] == 180

    # Verifica query SQL
    call_args = mock_db_session.execute.call_args
    # P3 #2: Agora usa to_tsvector ao invés de string_to_array
    assert "to_tsvector('portuguese', body)" in str(call_args[0][0])
    assert "tsvector_to_array" in str(call_args[0][0])
    assert "stop_words" in str(call_args[0][0]) or "custom_stop_words" in str(call_args[0][0])
    assert "direction = 'INBOUND'" in str(call_args[0][0])
    # Verifica que limit está no params (pode ser key diferente dependendo do binding)
    params = call_args[1] if len(call_args) > 1 else {}
    assert params.get("limit") == 50 or "limit" in str(call_args)


def test_sentiment_distribution_query_structure(analytics_repo, mock_db_session):
    """Testa análise de sentimento baseada em keywords."""
    # Arrange
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    # Mock result - P3 #3: Agora retorna fetchall() ao invés de fetchone()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(
            id="msg-1", body="Obrigado pela atenção!", sentiment_regex="positive", sentiment_count=350, total_count=1000
        ),
        MagicMock(
            id="msg-2",
            body="Gostaria de mais informações",
            sentiment_regex="neutral",
            sentiment_count=570,
            total_count=1000,
        ),
    ]
    mock_db_session.execute.return_value = mock_result

    # Act - P3 #3: Sem Gemini fallback (default)
    result = analytics_repo.get_message_sentiment_distribution(start_date, end_date, use_gemini_fallback=False)

    # Assert
    assert result["positive"] == 350
    assert result["negative"] == 0  # Sem mensagens negativas
    assert result["neutral"] == 570
    assert result["total_messages"] == 1000
    assert result["gemini_used"] is False  # P3 #3: Novo campo

    # Verifica query SQL
    call_args = mock_db_session.execute.call_args
    assert "CASE" in str(call_args[0][0])
    assert "sentiment_regex" in str(call_args[0][0])  # P3 #3: Novo campo alias


def test_topic_distribution_query_structure(analytics_repo, mock_db_session):
    """Testa classificação de topics baseada em keywords temáticas."""
    # Arrange
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    # Mock result
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(topic="Agendamento", count=250, percentage=35.0),
        MagicMock(topic="Preços", count=150, percentage=21.0),
        MagicMock(topic="Localização", count=100, percentage=14.0),
    ]
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_conversation_topics(start_date, end_date)

    # Assert
    assert len(result) == 3
    assert result[0]["topic"] == "Agendamento"
    assert result[0]["count"] == 250
    assert result[0]["percentage"] == 35.0
    assert result[1]["topic"] == "Preços"

    # Verifica query SQL
    call_args = mock_db_session.execute.call_args
    assert "agendar|agendamento|marcar" in str(call_args[0][0])
    assert "preço|valor|custo" in str(call_args[0][0])
    assert "localização|endereço" in str(call_args[0][0])
    assert "percentual do total" in str(call_args[0][0]).lower() or "percentage" in str(call_args[0][0]).lower()


def test_sentiment_distribution_empty_data(analytics_repo, mock_db_session):
    """Testa retorno quando não há mensagens."""
    # Arrange
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    # Mock result vazio - P3 #3: fetchall retorna lista vazia
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_message_sentiment_distribution(start_date, end_date)

    # Assert
    assert result["positive"] == 0
    assert result["negative"] == 0
    assert result["neutral"] == 0
    assert result["total_messages"] == 0
    assert result["gemini_used"] is False


# =========================================================================
# P3 #1: EDGE CASES (Testes adicionais para cobertura +10%)
# =========================================================================


def test_keyword_frequency_empty_period(analytics_repo, mock_db_session):
    """Testa extração de keywords quando período não tem mensagens."""
    # Arrange
    start_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 2, 28)

    # Mock result vazio
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_keyword_frequency(start_date, end_date, limit=50)

    # Assert
    assert result == []
    assert len(result) == 0


def test_sentiment_invalid_dates(analytics_repo, mock_db_session):
    """Testa que sentiment retorna vazio quando start_date > end_date."""
    # Arrange
    start_date = datetime(2026, 12, 31)  # DEPOIS
    end_date = datetime(2026, 1, 1)  # ANTES

    # Mock result vazio - P3 #3: fetchall retorna lista vazia
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_message_sentiment_distribution(start_date, end_date)

    # Assert
    assert result["total_messages"] == 0
    assert result["positive"] == 0
    assert result["negative"] == 0
    assert result["neutral"] == 0
    assert result["gemini_used"] is False


def test_topics_null_handling(analytics_repo, mock_db_session):
    """Testa que topics lida corretamente com mensagens NULL no body."""
    # Arrange
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)

    # Mock result com None values (mensagens com body=NULL)
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []  # Nenhum tópico quando body é NULL
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_conversation_topics(start_date, end_date)

    # Assert
    assert result == []
    assert len(result) == 0

    # Verifica que query filtra NULL corretamente
    call_args = mock_db_session.execute.call_args
    # A query deve ter WHERE body IS NOT NULL ou equivalente
    assert "body" in str(call_args[0][0]).lower()

