"""FastAPI application factory and global exception handling."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from robbot.api.v1.routers.api import api_router
from robbot.core.logging_setup import configure_logging
from robbot.infra.db.base import SessionLocal
from robbot.services.alert_service import AlertService


def create_app() -> FastAPI:
    """
    Application factory that creates and configures the FastAPI app.
    Registers routers and exception handlers and configures logging.
    """
    configure_logging()
    application = FastAPI(title="Robbot API", version="0.1.0")
    application.include_router(api_router, prefix="/api/v1")

    @application.exception_handler(Exception)
    async def global_exception_handler(_request: Request, exc: Exception):
        """
        Handler global que registra exceções e persiste um alerta crítico.
        Evita expor detalhes internos na resposta HTTP.
        """
        logger = logging.getLogger("robbot.global")
        logger.exception("Unhandled exception: %s", exc)

        # Tenta persistir um alerta no banco; não deve impedir resposta ao cliente.
        try:
            with SessionLocal() as db:
                alert_svc = AlertService(db)
                alert_svc.create_alert(
                    level="critical",
                    message="Unhandled exception",
                    metadata={"error": str(exc)},
                )
        except Exception:  # pylint: disable=broad-exception-caught
            # se falhar ao persistir alerta, apenas loga
            logger.exception("Failed to persist alert for unhandled exception")

        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    return application


app = create_app()
