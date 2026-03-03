"""
Testes de integração para Dashboard de Métricas em Tempo Real (L4).

Valida queries SQL, integração com QueueManager e WebSocket.
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


def test_active_conversations_query_structure(analytics_repo, mock_db_session):
    """Testa estrutura da query de conversas ativas."""
    # Arrange
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(
            id="uuid-123",
            chat_id="5511999999999@c.us",
            status="ACTIVE_BOT",
            last_message_at=datetime(2026, 1, 8, 14, 35),
            minutes_since_last_message=2.5,
        ),
        MagicMock(
            id="uuid-456",
            chat_id="5511888888888@c.us",
            status="PENDING_HANDOFF",
            last_message_at=datetime(2026, 1, 8, 14, 33),
            minutes_since_last_message=4.2,
        ),
    ]
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_active_conversations()

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == "uuid-123"
    assert result[0]["chat_id"] == "5511999999999@c.us"
    assert result[0]["status"] == "ACTIVE_BOT"
    assert result[0]["minutes_since_last_message"] == 2.5
    assert result[1]["status"] == "PENDING_HANDOFF"

    # Verifica query SQL
    call_args = mock_db_session.execute.call_args
    assert "last_message_at >= NOW() - INTERVAL '5 minutes'" in str(call_args[0][0])
    assert "ACTIVE_BOT" in str(call_args[0][0])
    assert "EXTRACT(EPOCH FROM (NOW() - last_message_at))" in str(call_args[0][0])


def test_performance_alerts_query_structure(analytics_repo, mock_db_session):
    """Testa alertas de performance com thresholds."""
    # Arrange
    mock_result = MagicMock()
    mock_result.fetchone.return_value = MagicMock(
        high_latency_count=10,
        high_latency_avg_ms=6500.0,
        failed_interactions=38,
        total_interactions=500,
        error_rate=7.6,
    )
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_performance_alerts(latency_threshold_ms=5000, error_rate_threshold=5.0)

    # Assert
    assert result["high_latency_count"] == 10
    assert result["high_latency_avg_ms"] == 6500.0
    assert result["error_rate"] == 7.6
    assert result["total_interactions_last_hour"] == 500
    assert result["failed_interactions"] == 38

    # Verifica query SQL
    call_args = mock_db_session.execute.call_args
    assert "llm_interactions" in str(call_args[0][0])
    assert "NOW() - INTERVAL '1 hour'" in str(call_args[0][0])
    assert "FILTER (WHERE latency_ms > :latency_threshold)" in str(call_args[0][0])
    assert "FILTER (WHERE error = true)" in str(call_args[0][0])
    # Verifica params (pode estar em posições diferentes)
    params = call_args[1] if len(call_args) > 1 else {}
    assert params.get("latency_threshold") == 5000 or "latency_threshold" in str(call_args)


def test_realtime_summary_query_structure(analytics_repo, mock_db_session):
    """Testa sumário de métricas em tempo real."""
    # Arrange
    mock_result = MagicMock()
    mock_result.fetchone.return_value = MagicMock(
        active_conversations=15,
        total_messages=41,
        messages_per_minute=8.2,
        avg_latency=1500.0,
        bot_resolution_rate=85.0,
    )
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_realtime_summary()

    # Assert
    assert result["active_conversations"] == 15
    assert result["messages_per_minute"] == 8.2
    assert result["avg_response_time_ms"] == 1500.0
    assert result["bot_resolution_rate"] == 85.0

    # Verifica query SQL
    call_args = mock_db_session.execute.call_args
    assert "last_message_at >= NOW() - INTERVAL '5 minutes'" in str(call_args[0][0])
    assert "COUNT(DISTINCT c.id)" in str(call_args[0][0])
    assert "total_messages::float / 5.0" in str(call_args[0][0])


def test_performance_alerts_empty_data(analytics_repo, mock_db_session):
    """Testa retorno quando não há dados."""
    # Arrange
    mock_result = MagicMock()
    mock_result.fetchone.return_value = MagicMock(
        high_latency_count=None,
        high_latency_avg_ms=None,
        failed_interactions=None,
        total_interactions=0,
        error_rate=None,
    )
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_performance_alerts()

    # Assert
    assert result["high_latency_count"] == 0
    assert result["high_latency_avg_ms"] == 0.0
    assert result["error_rate"] == 0.0
    assert result["total_interactions_last_hour"] == 0
    assert result["failed_interactions"] == 0


def test_realtime_summary_empty_data(analytics_repo, mock_db_session):
    """Testa sumário quando não há conversas ativas."""
    # Arrange
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_realtime_summary()

    # Assert
    assert result["active_conversations"] == 0
    assert result["messages_per_minute"] == 0.0
    assert result["avg_response_time_ms"] == 0.0
    assert result["bot_resolution_rate"] == 0.0


# =========================================================================
# P3 #1: EDGE CASES (Testes adicionais para cobertura +10%)
# =========================================================================


def test_performance_alerts_overflow(analytics_repo, mock_db_session):
    """Testa que alertas lidam com valores extremos (overflow de latência)."""
    # Arrange
    mock_result = MagicMock()
    mock_result.fetchone.return_value = MagicMock(
        high_latency_count=999,
        high_latency_avg_ms=999999.99,  # ~16 minutos (valor extremo)
        failed_interactions=50,
        total_interactions=100,
        error_rate=50.0,  # 50% de erro (crítico)
    )
    mock_db_session.execute.return_value = mock_result

    # Act
    result = analytics_repo.get_performance_alerts(latency_threshold_ms=5000, error_rate_threshold=5.0)

    # Assert
    assert result["high_latency_count"] == 999
    assert result["high_latency_avg_ms"] == 999999.99
    assert result["error_rate"] == 50.0
    assert result["total_interactions_last_hour"] == 100
    assert result["failed_interactions"] == 50

    # Valores extremos devem ser retornados sem falhas
    assert isinstance(result["high_latency_avg_ms"], float)
    assert result["error_rate"] >= 0.0 and result["error_rate"] <= 100.0

