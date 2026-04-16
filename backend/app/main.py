from fastapi import FastAPI

from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Refactor Trainer",
        description="Initial backend scaffold for Refactor Trainer.",
        version="0.1.0",
    )
    app.include_router(router)
    return app


app = create_app()

