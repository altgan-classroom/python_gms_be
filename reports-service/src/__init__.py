"""FastAPI app for the reports service (migrated from Flask/flask-openapi3)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gmsshared.src.web.fastapi_glue import (
    install_session_middleware,
    install_exception_handlers,
)


def create_app() -> FastAPI:
    app = FastAPI(title="Reports API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_session_middleware(app)
    install_exception_handlers(app)

    from reports_service import reports_api

    app.include_router(reports_api)
    return app


app = create_app()
