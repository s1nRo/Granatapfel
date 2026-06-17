from contextlib import asynccontextmanager
import logging
from typing import Any, AsyncGenerator

from fastapi import FastAPI
import uvicorn

from mirror.api.router import router
from mirror.api.schemas import AppState
from mirror.s3.client import s3_repo


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    logging.basicConfig(level=logging.INFO)
    logger.info("Application startup complete.")
    app.state.app = AppState(s3_client=s3_repo)
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "mirror.api.main:app",
        host="localhost",
        port=8000,
    )
