from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse

from mirror.api.repository import directory_page, download_page, get_home_page
from mirror.api.schemas import AppState


router = APIRouter()


@router.get("/")
async def get_directory_home() -> HTMLResponse:
    html = await get_home_page()

    return HTMLResponse(content=html)


@router.get("/{owner}/{repo}")
async def get_directory_url(request: Request, owner: str, repo: str) -> HTMLResponse:
    state: AppState = request.app.state.app
    html = await directory_page(state, owner, repo)

    return HTMLResponse(content=html)


@router.get("/{owner}/{repo}/{key}")
async def get_directory_download(request: Request, key: str) -> None:
    state: AppState = request.app.state.app
    res = await download_page(state, key)

    return Response(
        content=res,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={key}"},
    )
