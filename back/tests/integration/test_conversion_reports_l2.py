"""
Testes de integração para Sprint 12 - L2: Relatório de Conversão de Leads

Testa os novos endpoints e métodos implementados.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from robbot.infra.persistence.repositories.analytics_repository import AnalyticsRepository


class TestConversionReportsL2:
    """Testes para os novos métodos de conversion reports L2"""

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

    def test_time_to_conversion_extended_structure(self, analytics_repo, date_range):
        """Testa se a query estendida tem p75 e p90"""
        start_date, end_date = date_range

        # Mock do resultado vazio
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.avg_hours = None
        mock_result.fetchone.return_value = mock_row
        analytics_repo.db.execute = MagicMock(return_value=mock_result)

        result = analytics_repo.get_time_to_conversion_extended(start_date, end_date)

        # Verifica estrutura do response
        assert "avg_hours" in result
        assert "median_hours" in result
        assert "p75_hours" in result
        assert "p90_hours" in result
        assert "p95_hours" in result
        assert "min_hours" in result
        assert "max_hours" in result

    def test_conversion_by_source_structure(self, analytics_repo, date_range):
        """Testa estrutura de conversão por origem"""
        start_date, end_date = date_range

        # Mock com dados fictícios
        mock_result = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.source = "direct"
        mock_row1.total_leads = 120
        mock_row1.converted_leads = 45
        mock_row1.conversion_rate = 37.5

        mock_row2 = MagicMock()
        mock_row2.source = "group"
        mock_row2.total_leads = 30
        mock_row2.converted_leads = 5
        mock_row2.conversion_rate = 16.67

        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        analytics_repo.db.execute = MagicMock(return_value=mock_result)

        result = analytics_repo.get_conversion_by_source(start_date, end_date)

        # Verifica estrutura
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["source"] == "direct"
        assert result[0]["total_leads"] == 120
        assert result[0]["converted_leads"] == 45
        assert result[0]["conversion_rate"] == 37.5

    def test_lost_leads_analysis_structure(self, analytics_repo, date_range):
        """Testa estrutura de análise de leads perdidos"""
        start_date, end_date = date_range

        # Mock resultado principal
        mock_result1 = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.total_lost = 45
        mock_row1.avg_time_before_lost_hours = 36.5
        mock_result1.fetchone.return_value = mock_row1

        # Mock resultado por maturity
        mock_result2 = MagicMock()
        mock_row2 = MagicMock()
        mock_row2.maturity_range = "0-19 (muito baixo)"
        mock_row2.count = 15
        mock_result2.fetchall.return_value = [mock_row2]

        # Setup de múltiplas chamadas ao execute
        analytics_repo.db.execute = MagicMock(side_effect=[mock_result1, mock_result2])

        result = analytics_repo.get_lost_leads_analysis(start_date, end_date)

        # Verifica estrutura
        assert "total_lost" in result
        assert "lost_by_maturity_range" in result
        assert "avg_time_before_lost_hours" in result
        assert result["total_lost"] == 45
        assert isinstance(result["lost_by_maturity_range"], list)

    def test_conversion_trend_structure(self, analytics_repo, date_range):
        """Testa estrutura de tendência temporal"""
        start_date, end_date = date_range

        # Mock com dados fictícios
        mock_result = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.period = datetime(2026, 1, 1)
        mock_row1.total_leads = 25
        mock_row1.converted_leads = 8
        mock_row1.conversion_rate = 32.0

        mock_result.fetchall.return_value = [mock_row1]
        analytics_repo.db.execute = MagicMock(return_value=mock_result)

        result = analytics_repo.get_conversion_trend(start_date, end_date, "day")

        # Verifica estrutura
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["period"] == "2026-01-01"
        assert result[0]["total_leads"] == 25
        assert result[0]["converted_leads"] == 8
        assert result[0]["conversion_rate"] == 32.0

    def test_conversion_trend_granularity(self, analytics_repo, date_range):
        """Testa diferentes granularidades de tendência"""
        start_date, end_date = date_range

        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        analytics_repo.db.execute = MagicMock(return_value=mock_result)

        # Testa day
        result_day = analytics_repo.get_conversion_trend(start_date, end_date, "day")
        assert isinstance(result_day, list)

        # Testa week
        result_week = analytics_repo.get_conversion_trend(start_date, end_date, "week")
        assert isinstance(result_week, list)

        # Testa month
        result_month = analytics_repo.get_conversion_trend(start_date, end_date, "month")
        assert isinstance(result_month, list)

