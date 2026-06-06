from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from mirror.api.repository import directory_page, download_page, get_home_page
from mirror.api.schemas import AppState


router = APIRouter()


@router.get("/")
async def get_directory_home() -> HTMLResponse:
    html = await get_home_page()

    return HTMLResponse(content=html)


@router.get("/{url}")
async def get_directory_url(request: Request, url: str) -> HTMLResponse:
    state: AppState = request.app.state.app
    html = directory_page(state, url)

    return HTMLResponse(content=html)


@router.get("/{url}/download")
async def get_directory_download(request: Request, url: str) -> HTMLResponse:
    state: AppState = request.app.state.app
    html = download_page(state, url)

    return HTMLResponse(content=html)
