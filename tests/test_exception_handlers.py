from fastapi.testclient import TestClient
from fastapi import APIRouter
from pytest import LogCaptureFixture
import logging
import traceback

from feedreader3.main import app


def test_global_exception_handler(caplog: LogCaptureFixture) -> None:
    router = APIRouter(prefix="/tests")

    error_message = "Error from API"

    @router.get("/exception")
    async def throw_exception() -> None:
        raise RuntimeError(error_message)

    app.include_router(router)
    with TestClient(app, raise_server_exceptions=False) as client:
        with caplog.at_level(
            logging.ERROR, logger="uvicorn.feedreader3.exception_handlers"
        ):
            try:
                response = client.get("/tests/exception")
            finally:
                # Remove /tests/exception endpoint
                app.router.routes.remove(router.routes[0])

    assert response.status_code == 500
    assert response.text == "Internal Server Error"

    rec = next(
        (
            r
            for r in caplog.records
            if (
                r.name == "uvicorn.feedreader3.exception_handlers"
                and r.levelname == "ERROR"
                and r.message == error_message
            )
        ),
        None,
    )
    assert rec is not None
    assert rec.exc_info is not None
    exc_type, exc_value, exc_tb = rec.exc_info
    assert exc_type is RuntimeError
    assert exc_value is not None
    assert str(exc_value) == error_message
    assert exc_tb is not None
    assert any(
        ("test_exception_handlers" in line and "throw_exception" in line)
        for line in traceback.format_exception(None, value=exc_value, tb=exc_tb)
    )
