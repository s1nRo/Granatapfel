from contextlib import asynccontextmanager
import logging
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from mirror.api.router import router
from mirror.api.schemas import AppState
from mirror.config import settings
from mirror.s3.client import S3Repository


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
    logger.info("Application startup complete.")
    app.state.app = AppState(s3_client=S3Repository())
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(lifespan=lifespan)
app.include_router(router)


def main() -> None:
    import uvicorn

    uvicorn.run("mirror.api.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
