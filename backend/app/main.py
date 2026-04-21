import logging

from fastapi import FastAPI

from app.api.routes import router


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    app = FastAPI(
        title="Refactor Trainer",
        description="Initial backend scaffold for Refactor Trainer.",
        version="0.1.0",
    )
    app.include_router(router)
    return app


app = create_app()
