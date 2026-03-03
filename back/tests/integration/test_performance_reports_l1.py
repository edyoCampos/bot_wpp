"""
Testes de integração para Sprint 12 - L1: Relatório de Performance de Atendimento

Testa os novos endpoints e métodos implementados.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from robbot.infra.persistence.repositories.analytics_repository import AnalyticsRepository


class TestPerformanceReportsL1:
    """Testes para os novos métodos de performance reports"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock da sessão do banco"""
        return MagicMock()

    @pytest.fixture
    def analytics_repo(self, mock_db_session):
        """Instância do repository com mock"""
        return AnalyticsRepository(mock_db_session)

    @pytest.fixture
    def date_range(self):
        """Range de datas padrão para testes"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return start_date, end_date

    def test_bot_response_time_stats_query_structure(self, analytics_repo, date_range):
        """Testa se a query de bot response time está bem estruturada"""
        start_date, end_date = date_range

        # Mock do resultado vazio
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.avg_ms = None
        mock_result.fetchone.return_value = mock_row
        analytics_repo.db.execute = MagicMock(return_value=mock_result)

        result = analytics_repo.get_bot_llm_latency_stats(start_date, end_date)

        # Verifica estrutura do response quando vazio
        assert "avg_ms" in result
        assert "median_ms" in result
        assert "p95_ms" in result
        assert "p99_ms" in result
        assert "min_ms" in result
        assert "max_ms" in result
        assert "total_interactions" in result
        assert result["avg_ms"] == 0.0

    def test_handoff_rate_stats_query_structure(self, analytics_repo, date_range):
        """Testa se a query de handoff rate está bem estruturada"""
        start_date, end_date = date_range

        # Mock do resultado vazio
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.total_conversations = 0
        mock_result.fetchone.return_value = mock_row
        analytics_repo.db.execute = MagicMock(return_value=mock_result)

        result = analytics_repo.get_handoff_rate_stats(start_date, end_date)

        # Verifica estrutura do response
        assert "total_conversations" in result
        assert "bot_resolved" in result
        assert "handoff_required" in result
        assert "handoff_rate" in result
        assert "auto_resolution_rate" in result

    def test_peak_hours_stats_query_structure(self, analytics_repo, date_range):
        """Testa se a query de peak hours está bem estruturada"""
        start_date, end_date = date_range

        # Mock do resultado com dados fictícios
        mock_result = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.hour = 9
        mock_row1.message_count = 100
        mock_row1.conversation_count = 20

        mock_row2 = MagicMock()
        mock_row2.hour = 14
        mock_row2.message_count = 150
        mock_row2.conversation_count = 30

        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        analytics_repo.db.execute = MagicMock(return_value=mock_result)

        result = analytics_repo.get_peak_hours_stats(start_date, end_date)

        # Verifica estrutura do response
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["hour"] == 9
        assert result[0]["message_count"] == 100
        assert result[0]["conversation_count"] == 20

    def test_conversations_by_status_query_structure(self, analytics_repo, date_range):
        """Testa se a query de conversations by status está bem estruturada"""
        start_date, end_date = date_range

        # Mock do resultado com dados fictícios
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.status = "ACTIVE_BOT"
        mock_row.count = 100
        mock_row.percentage = 50.0

        mock_result.fetchall.return_value = [mock_row]
        analytics_repo.db.execute = MagicMock(return_value=mock_result)

        result = analytics_repo.get_conversations_by_status(start_date, end_date)

        # Verifica estrutura do response
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["status"] == "ACTIVE_BOT"
        assert result[0]["count"] == 100
        assert result[0]["percentage"] == 50.0

    def test_handoff_rate_calculation(self, analytics_repo, date_range):
        """Testa cálculo correto das taxas de handoff"""
        start_date, end_date = date_range

        # Mock com dados reais
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.total_conversations = 100
        mock_row.bot_resolved = 70
        mock_row.handoff_required = 30
        mock_result.fetchone.return_value = mock_row
        analytics_repo.db.execute = MagicMock(return_value=mock_result)

        result = analytics_repo.get_handoff_rate_stats(start_date, end_date)

        # Verifica cálculos
        assert result["total_conversations"] == 100
        assert result["bot_resolved"] == 70
        assert result["handoff_required"] == 30
        assert result["handoff_rate"] == 30.0
        assert result["auto_resolution_rate"] == 70.0

