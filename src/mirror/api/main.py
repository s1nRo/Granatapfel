from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from mirror.s3.client import s3_repo


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup complete.")
    app.state.repo_s3 = s3_repo
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(lifespan=lifespan)