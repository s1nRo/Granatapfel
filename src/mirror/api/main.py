from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from mirror.api.router import router
from mirror.api.schemas import AppState
from mirror.s3.client import s3_repo


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    logger.info("Application startup complete.")
    app.state.app = AppState(s3_client=s3_repo)
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(lifespan=lifespan)
app.include_router(router)
