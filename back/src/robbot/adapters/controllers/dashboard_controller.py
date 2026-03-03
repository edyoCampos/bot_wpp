"""
Dashboard Controller - Refatorado .1

Endpoints de analytics com autenticação, cache configurável e validação.

Melhorias críticas:
- WebSocket com autenticação via token
- Rate limiting para evitar DoS
- Validação de datas (start <= end)
- Dependency injection para todos os services
"""
# pylint: disable=unused-argument
# Justification: FastAPI Depends() requires current_user parameter for authentication
# even when not used in function body. This is the standard FastAPI security pattern.

import asyncio
import contextlib
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.responses import Response
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.analytics_repository import AnalyticsRepository
from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.config.settings import get_settings
from robbot.domain.shared.enums import Role
from robbot.infra.persistence.models.user_model import UserModel
from robbot.infra.redis.client import get_redis_client
from robbot.infra.redis.queue import get_queue_manager
from robbot.schemas.metrics_schemas import (
    BotAutonomyResponse,
    BotResponseTimeResponse,
    ConversationAnalysisReportSchema,
    ConversationsByStatusResponse,
    ConversionBySourceResponse,
    ConversionFunnelResponse,
    ConversionReportExtendedSchema,
    ConversionTrendResponse,
    DashboardSummaryResponse,
    HandoffRateResponse,
    LostLeadsAnalysisResponse,
    PeakHoursResponse,
    PerformanceReportSchema,
    RealtimeDashboardSchema,
    TimeToConversionExtendedResponse,
)
from robbot.services.analytics.metrics_service import MetricsService
from robbot.services.infrastructure.export_service import ExportService

settings = get_settings()
router = APIRouter()

# WebSocket connection tracking (in-memory, consider Redis for multi-instance)
_ws_connections: defaultdict[str, list[WebSocket]] = defaultdict(list)
_ws_rate_limit: defaultdict[str, list[float]] = defaultdict(list)


def get_metrics_service(db_session: Session = Depends(get_db)) -> MetricsService:
    """
    Injeta MetricsService com todas as dependências.

    Agora inclui QueueManager via DI (não mais import interno).
    """
    return MetricsService(
        analytics_repo=AnalyticsRepository(db_session),
        redis_client=get_redis_client(),
        queue_manager=get_queue_manager(),  # Dependency Injection
    )


def check_admin(current_user: UserModel = Depends(get_current_user)):
    """Apenas admin"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas admin")
    return current_user


def parse_dates(start_date: str | None, end_date: str | None, period: str) -> tuple[datetime, datetime]:
    """
    Parse e valida datas para queries.

    Valida que start_date <= end_date.

    Args:
        start_date: Data inicial ISO format (opcional)
        end_date: Data final ISO format (opcional)
        period: Período padrão se datas não fornecidas ("7d", "30d", "90d")

    Returns:
        Tupla (start_datetime, end_datetime)

    Raises:
        HTTPException: Se start_date > end_date
    """
    if start_date and end_date:
        start = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0)
        end = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59)

        # Validação: start <= end
        if start > end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date range: start_date ({start_date}) must be <= end_date ({end_date})",
            )

        return start, end

    # Default: período relativo
    end = datetime.now().replace(hour=23, minute=59, second=59)
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    return end - timedelta(days=days), end


async def verify_websocket_token(token: str) -> UserModel:
    """
    Verifica token JWT para autenticação WebSocket.

    Args:
        token: JWT token string

    Returns:
        UserModel autenticado

    Raises:
        HTTPException: Se token inválido ou expirado
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing user ID")

        # Buscar usuário no DB (requer session - será passada por contexto)
        # Para simplificar, apenas validamos o token aqui
        # TODO: Buscar user completo se precisar validar role
        return user_id

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials: {str(e)}"
        )


@router.get("/dashboard", response_model=DashboardSummaryResponse)
async def dashboard(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """KPIs: conversão, mensagens, tempo resposta. Cache 5min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_dashboard_summary(start, end)


@router.get("/conversion-funnel", response_model=ConversionFunnelResponse)
async def funnel(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Funil 5 etapas + drop-off. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_conversion_funnel(start, end)


@router.get("/bot-autonomy", response_model=BotAutonomyResponse)
async def bot_autonomy(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(check_admin),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Taxa autonomia bot. Admin only. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_bot_autonomy_rate(start, end)


# =============================================================================
# PERFORMANCE REPORTS ( - L1)
# =============================================================================


@router.get("/performance/bot-response-time", response_model=BotResponseTimeResponse)
async def bot_response_time_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Tempo de resposta do bot via LLM latency. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_bot_response_time(start, end)


@router.get("/performance/handoff-rate", response_model=HandoffRateResponse)
async def handoff_rate_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Taxa de resolução automática vs handoff. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_handoff_rate(start, end)


@router.get("/performance/peak-hours", response_model=PeakHoursResponse)
async def peak_hours_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Horários de pico de atendimento. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_peak_hours(start, end)


@router.get("/performance/conversations-by-status", response_model=ConversationsByStatusResponse)
async def conversations_by_status_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Distribuição de conversas por status. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_conversations_by_status(start, end)


@router.get("/performance/report", response_model=PerformanceReportSchema)
async def performance_full_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Relatório completo de performance (L1): bot response time, handoff rate, peak hours, status distribution. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_performance_report(start, end)


@router.get("/performance/report/export/pdf")
async def performance_report_export_pdf(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Exporta relatório de performance em PDF."""
    start, end = parse_dates(start_date, end_date, period)
    report_data = await svc.get_performance_report(start, end)

    # Gerar PDF
    pdf_bytes = ExportService.export_performance_report_pdf(report_data)

    # Filename com timestamp
    filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/performance/report/export/excel")
async def performance_report_export_excel(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Exporta relatório de performance em Excel."""
    start, end = parse_dates(start_date, end_date, period)
    report_data = await svc.get_performance_report(start, end)

    # Gerar Excel
    excel_bytes = ExportService.export_performance_report_excel(report_data)

    # Filename com timestamp
    filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# =============================================================================
# CONVERSION REPORTS EXTENDED ( - L2)
# =============================================================================


@router.get("/conversion/time-to-conversion-extended", response_model=TimeToConversionExtendedResponse)
async def time_to_conversion_extended_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Tempo até conversão com p75, p90. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_time_to_conversion_extended(start, end)


@router.get("/conversion/by-source", response_model=ConversionBySourceResponse)
async def conversion_by_source_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Taxa de conversão por origem (direct, group). Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_conversion_by_source(start, end)


@router.get("/conversion/lost-leads", response_model=LostLeadsAnalysisResponse)
async def lost_leads_analysis_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Análise de leads perdidos (status LOST). Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_lost_leads_analysis(start, end)


@router.get("/conversion/trend", response_model=ConversionTrendResponse)
async def conversion_trend_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Tendência temporal de conversão (day/week/month). Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_conversion_trend(start, end, granularity)


@router.get("/conversion/report-extended", response_model=ConversionReportExtendedSchema)
async def conversion_report_extended(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Relatório COMPLETO de conversão (L2): time to conversion extended, by source, lost leads, trend. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_conversion_report_extended(start, end)


# =====================================================================
# L3: CONVERSATION ANALYSIS ENDPOINTS
# =====================================================================


@router.get("/conversation/activity-heatmap", response_model=dict)
async def conversation_activity_heatmap(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Heatmap de atividade: mensagens por dia da semana e hora. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_activity_heatmap(start, end)


@router.get("/conversation/keywords", response_model=dict)
async def conversation_keywords(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    limit: int = Query(50, ge=1, le=200),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Palavras-chave mais frequentes nas mensagens INBOUND. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_keyword_frequency(start, end, limit)


@router.get("/conversation/sentiment", response_model=dict)
async def conversation_sentiment(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Análise de sentimento nas mensagens INBOUND. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_sentiment_distribution(start, end)


@router.get("/conversation/topics", response_model=dict)
async def conversation_topics(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Topics mais discutidos nas mensagens INBOUND. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_topic_distribution(start, end)


@router.get("/conversation/report", response_model=ConversationAnalysisReportSchema)
async def conversation_analysis_report(
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = Query("30d"),
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Relatório COMPLETO de análise de conversas (L3): heatmap, keywords, sentiment, topics. Cache 15min."""
    start, end = parse_dates(start_date, end_date, period)
    return await svc.get_conversation_analysis_report(start, end)


# =====================================================================
# L4: REAL-TIME DASHBOARD ENDPOINTS
# =====================================================================


@router.get("/realtime/dashboard", response_model=RealtimeDashboardSchema)
async def realtime_dashboard(
    current_user: UserModel = Depends(get_current_user),
    svc: MetricsService = Depends(get_metrics_service),
):
    """Dashboard completo em tempo real: summary, active conversations, queue stats, alerts. Cache 30s."""
    return await svc.get_realtime_dashboard()


@router.websocket("/ws/realtime")
async def websocket_realtime_metrics(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token para autenticação"),
    svc: MetricsService = Depends(get_metrics_service),
):
    """
    WebSocket para streaming de métricas em tempo real COM AUTENTICAÇÃO.

    SEGURANÇA:
    - Requer JWT token via query param: /ws/realtime?token=<your_jwt>
    - Rate limiting: máx 3 conexões por usuário
    - Idle timeout: desconecta após 30 minutos sem atividade
    - Valida token antes de accept()

    Envia atualizações a cada 5 segundos com:
    - Conversas ativas
    - Sumário de métricas
    - Queue stats
    - Alertas de performance

    Exemplo de uso (JavaScript):
    ```javascript
    const token = localStorage.getItem('access_token');
    const ws = new WebSocket(`ws://localhost:8000/api/v1/metrics/ws/realtime?token=${token}`);
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Realtime metrics:', data);
    };
    ```
    """
    # 1. Autenticar ANTES de aceitar conexão
    try:
        user_id = await verify_websocket_token(token)
    except HTTPException as e:
        await websocket.close(code=1008, reason=e.detail)  # 1008 = Policy Violation
        return

    # 2. Rate limiting: máx N conexões por usuário
    if len(_ws_connections[user_id]) >= settings.WEBSOCKET_MAX_CONNECTIONS_PER_USER:
        await websocket.close(
            code=1008, reason=f"Too many connections (max {settings.WEBSOCKET_MAX_CONNECTIONS_PER_USER} per user)"
        )
        return

    # 3. Aceitar conexão APÓS validação
    await websocket.accept()
    _ws_connections[user_id].append(websocket)

    last_activity = time.time()
    idle_timeout_seconds = settings.WEBSOCKET_IDLE_TIMEOUT_MINUTES * 60

    try:
        while True:
            # Check idle timeout
            if time.time() - last_activity > idle_timeout_seconds:
                await websocket.close(code=1000, reason="Idle timeout")
                break

            # Buscar métricas (sempre fresh - não usar cache aqui)
            try:
                data = svc.get_realtime_dashboard()

                # Enviar para cliente
                await websocket.send_text(json.dumps(data, default=str))
                last_activity = time.time()

            except Exception as e:
                # Log error mas não fechar conexão (pode ser erro temporário)
                await websocket.send_text(json.dumps({"error": str(e), "timestamp": datetime.now().isoformat()}))

            # Aguardar 5 segundos antes de próximo update
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        # Erro inesperado - fechar com código de erro
        with contextlib.suppress(BaseException):
            await websocket.close(code=1011, reason=str(e))
    finally:
        # Cleanup: remover da lista de conexões
        if websocket in _ws_connections[user_id]:
            _ws_connections[user_id].remove(websocket)
        if not _ws_connections[user_id]:
            del _ws_connections[user_id]

