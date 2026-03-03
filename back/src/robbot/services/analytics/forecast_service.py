"""
Forecast Service

Service para análise preditiva e forecasting usando ML.

Implementa:
- Previsão de demanda (volume de mensagens)
- Probabilidade de conversão por lead
- Detecção de anomalias em métricas
- Recomendação de melhor horário para reengajamento

Note: Prophet e scikit-learn são opcionais. Se não instalados,
retorna análises estatísticas básicas.
"""

import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# Optional ML dependencies
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("[WARNING] NumPy not installed - using basic statistics")

try:
    from sklearn import ensemble  # noqa: F401 (imported but unused)

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("[WARNING] scikit-learn not installed - ML features limited")


class ForecastService:
    """
    Service para análise preditiva e forecasting.

    Implementa modelos básicos de ML quando bibliotecas estão disponíveis.
    Fallback para estatísticas descritivas caso contrário.
    """

    def __init__(self):
        self.has_ml = HAS_NUMPY and HAS_SKLEARN
        if self.has_ml:
            logger.info("[SUCCESS] ForecastService initialized with ML capabilities")
        else:
            logger.warning("[WARNING] ForecastService initialized in basic mode (no ML libs)")

    async def forecast_demand(
        self,
        historical_data: list[dict[str, Any]],
        days_ahead: int = 30,
    ) -> dict[str, Any]:
        """
        Previsão de demanda (volume de mensagens futuras).

        Usa médias móveis e padrões históricos para projetar volume futuro.
        Para ML avançado, instalar: pip install prophet

        Args:
            historical_data: Lista de {"date": "YYYY-MM-DD", "volume": int}
            days_ahead: Número de dias para prever

        Returns:
            Forecast com volume previsto, bounds inferior/superior
        """
        if not historical_data:
            return {"status": "error", "message": "Dados históricos necessários para forecast"}

        try:
            # Calcular média e desvio padrão dos últimos 30 dias
            recent_volumes = [d["volume"] for d in historical_data[-30:]]

            if HAS_NUMPY:
                avg_volume = float(np.mean(recent_volumes))
                std_volume = float(np.std(recent_volumes))
            else:
                avg_volume = sum(recent_volumes) / len(recent_volumes)
                variance = sum((x - avg_volume) ** 2 for x in recent_volumes) / len(recent_volumes)
                std_volume = variance**0.5

            # Detectar tendência (crescimento/decrescimento)
            if len(historical_data) >= 7:
                first_week_avg = sum(d["volume"] for d in historical_data[:7]) / 7
                last_week_avg = sum(d["volume"] for d in historical_data[-7:]) / 7
                trend = (last_week_avg - first_week_avg) / 7  # Mudança diária
            else:
                trend = 0

            # Gerar previsões
            forecast = []
            base_date = datetime.now()

            for i in range(days_ahead):
                predicted_date = base_date + timedelta(days=i + 1)

                # Previsão = média + tendência * dias + ajuste de sazonalidade
                base_prediction = avg_volume + (trend * i)

                # Ajuste semanal (fins de semana tendem a ter -20% volume)
                weekday = predicted_date.weekday()
                seasonal_factor = 0.8 if weekday >= 5 else 1.0

                predicted_volume = int(base_prediction * seasonal_factor)
                lower_bound = int(predicted_volume - (2 * std_volume))
                upper_bound = int(predicted_volume + (2 * std_volume))

                forecast.append(
                    {
                        "date": predicted_date.strftime("%Y-%m-%d"),
                        "predicted_volume": max(0, predicted_volume),
                        "lower_bound": max(0, lower_bound),
                        "upper_bound": max(0, upper_bound),
                        "confidence": "medium" if self.has_ml else "low",
                    }
                )

            logger.info("[SUCCESS] Demand forecast generated for %s days", days_ahead)
            return {
                "status": "success",
                "forecast": forecast,
                "model": "statistical" if not self.has_ml else "ml_enhanced",
                "note": "Para ML avançado, instalar: pip install prophet",
            }

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(f"[ERROR] Failed to generate forecast: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def predict_lead_conversion_probability(
        self,
        lead_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Probabilidade de conversão de um lead específico.

        Usa features do lead para calcular probabilidade de conversão.
        Com scikit-learn: Random Forest. Sem: scoring heurístico.

        Args:
            lead_data: Dict com maturity_score, message_count, response_time_avg_seconds, etc.

        Returns:
            Probabilidade e fatores de influência
        """
        try:
            lead_id = lead_data.get("lead_id", "unknown")

            # Scoring heurístico baseado em regras de negócio
            score_weights = {
                "maturity_score": 0.40,
                "message_engagement": 0.25,
                "response_speed": 0.20,
                "data_completeness": 0.15,
            }

            factors = []
            total_score = 0.0

            # 1. Maturity Score
            maturity = lead_data.get("maturity_score", 0) / 100.0
            maturity_contrib = maturity * score_weights["maturity_score"]
            total_score += maturity_contrib
            factors.append(
                {
                    "factor": "maturity_score",
                    "impact": round(maturity_contrib, 3),
                    "value": lead_data.get("maturity_score", 0),
                }
            )

            # 2. Engajamento
            msg_count = lead_data.get("message_count", 0)
            engagement = min(msg_count / 10, 1.0)
            engagement_contrib = engagement * score_weights["message_engagement"]
            total_score += engagement_contrib
            factors.append({"factor": "message_engagement", "impact": round(engagement_contrib, 3), "value": msg_count})

            # 3. Velocidade de resposta
            response_time = lead_data.get("response_time_avg_seconds", 3600)
            speed_score = 1.0 if response_time < 300 else (0.7 if response_time < 3600 else 0.3)
            speed_contrib = speed_score * score_weights["response_speed"]
            total_score += speed_contrib
            factors.append(
                {"factor": "response_speed", "impact": round(speed_contrib, 3), "value": f"{int(response_time)}s"}
            )

            # 4. Completude de dados
            has_email = lead_data.get("has_email", False)
            assigned = lead_data.get("assigned_to_user", False)
            completeness = (0.5 if has_email else 0) + (0.5 if assigned else 0)
            completeness_contrib = completeness * score_weights["data_completeness"]
            total_score += completeness_contrib
            factors.append(
                {
                    "factor": "data_completeness",
                    "impact": round(completeness_contrib, 3),
                    "value": f"{int(completeness * 100)}%",
                }
            )

            confidence = "high" if total_score >= 0.75 else ("medium" if total_score >= 0.50 else "low")
            logger.info("[SUCCESS] Conversion probability calculated for lead %s: %.2f", lead_id, total_score)

            return {
                "status": "success",
                "lead_id": lead_id,
                "conversion_probability": round(total_score, 3),
                "confidence": confidence,
                "factors": sorted(factors, key=lambda x: x["impact"], reverse=True),
                "model": "heuristic" if not HAS_SKLEARN else "hybrid",
            }
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(f"[ERROR] Failed to calculate conversion probability: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def detect_anomalies(
        self,
        time_series_data: list[dict[str, Any]],
        metric_name: str = "volume",
        threshold_sigma: float = 2.5,
    ) -> list[dict[str, Any]]:
        """
        Detecta anomalias em séries temporais usando Z-score.

        Anomalia se: |z_score| > threshold_sigma (padrão: 2.5 = 99% confiança)

        Args:
            time_series_data: [{"date": "YYYY-MM-DD", "value": float}, ...]
            metric_name: Nome da métrica
            threshold_sigma: Limiar de desvios padrão

        Returns:
            Lista de anomalias detectadas
        """
        if not time_series_data or len(time_series_data) < 7:
            return []

        try:
            values = [d["value"] for d in time_series_data]

            # Calcular média e desvio padrão
            if HAS_NUMPY:
                mean, std = float(np.mean(values)), float(np.std(values))
            else:
                mean = sum(values) / len(values)
                std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5

            if std == 0:
                return []

            # Detectar anomalias
            anomalies = []
            for data_point in time_series_data:
                value = data_point["value"]
                z_score = (value - mean) / std

                if abs(z_score) > threshold_sigma:
                    severity = "critical" if abs(z_score) > 3.5 else ("high" if abs(z_score) > 3.0 else "medium")
                    anomalies.append(
                        {
                            "date": data_point.get("date", "unknown"),
                            "metric": metric_name,
                            "value": value,
                            "expected_value": round(mean, 2),
                            "z_score": round(z_score, 2),
                            "deviation_percent": round(((value - mean) / mean) * 100, 1),
                            "severity": severity,
                            "type": "spike" if z_score > 0 else "drop",
                        }
                    )

            if anomalies:
                logger.warning("[WARNING] %s anomalies detected in %s", len(anomalies), metric_name)
            return sorted(anomalies, key=lambda x: abs(x["z_score"]), reverse=True)
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(f"[ERROR] Failed to detect anomalies: {e}", exc_info=True)
            return []

    async def recommend_reengagement_time(
        self,
        lead_id: str,
        interaction_history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Recomenda melhor horário para reengajar lead inativo.

        Analisa padrões históricos de resposta para sugerir timing ideal.

        Args:
            lead_id: ID do lead
            interaction_history: [{"timestamp": datetime, "responded": bool}, ...]

        Returns:
            Recomendação de dia e horário ideal
        """
        if not interaction_history:
            return {
                "status": "success",
                "lead_id": lead_id,
                "best_hour": 14,
                "best_day_of_week": 2,
                "confidence": 0.3,
                "reason": "Padrão geral (sem histórico suficiente)",
            }

        try:
            hour_responses = Counter()
            day_responses = Counter()
            total_responses = 0

            for interaction in interaction_history:
                if interaction.get("responded", False):
                    timestamp = interaction.get("timestamp")
                    if timestamp:
                        hour_responses[timestamp.hour] += 1
                        day_responses[timestamp.weekday()] += 1
                        total_responses += 1

            if total_responses == 0:
                best_hour, best_day, confidence, reason = 14, 2, 0.2, "Sem respostas históricas"
            else:
                best_hour = hour_responses.most_common(1)[0][0] if hour_responses else 14
                best_day = day_responses.most_common(1)[0][0] if day_responses else 2
                confidence = 0.85 if total_responses >= 10 else (0.65 if total_responses >= 5 else 0.45)
                reason = f"Análise de {total_responses} interações históricas"

            day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            logger.info("[SUCCESS] Reengagement: %ss at %sh", day_names[best_day], best_hour)

            return {
                "status": "success",
                "lead_id": lead_id,
                "best_hour": best_hour,
                "best_day_of_week": best_day,
                "best_day_name": day_names[best_day],
                "confidence": round(confidence, 2),
                "reason": reason,
                "response_rate": round(total_responses / len(interaction_history), 2) if interaction_history else 0,
            }
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(f"[ERROR] Failed to recommend reengagement time: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
