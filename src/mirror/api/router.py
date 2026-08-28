from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from mirror.api.repository import (
    directory_page,
    download_page,
    get_current_username,
    get_home_page,
    version_page,
)
from mirror.api.schemas import AppState
from fastapi.responses import StreamingResponse
from starlette.concurrency import iterate_in_threadpool

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/auth")
def read_current_user(
    username: Annotated[str, Depends(get_current_username)],
) -> dict[str, Annotated[str, Depends(get_current_username)]]:
    return {"username": username}


@router.get("/")
async def get_directory_home() -> HTMLResponse:
    html = await get_home_page()

    return HTMLResponse(content=html)


@router.get("/{owner}/{repo}")
async def get_directory_url(request: Request, owner: str, repo: str) -> HTMLResponse:
    state: AppState = request.app.state.app
    html = await version_page(state, owner, repo)

    return HTMLResponse(content=html)


@router.get("/{owner}/{repo}/{version}")
async def get_directory_url_version(
    request: Request, owner: str, repo: str, version: str
) -> HTMLResponse:
    state: AppState = request.app.state.app
    html = await directory_page(state, owner, repo, version)

    return HTMLResponse(content=html)


@router.get("/{owner}/{repo}/{version}/{key}")
async def get_directory_download(
    request: Request, owner: str, repo: str, version: str, key: str
) -> StreamingResponse:
    state: AppState = request.app.state.app
    res = await download_page(state, owner, repo, version, key)

    if res is None:
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(
        iterate_in_threadpool(res["Body"].iter_chunks(1024 * 1024)),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{key}"',
            "Content-Length": str(res["ContentLength"]),
        },
    )
