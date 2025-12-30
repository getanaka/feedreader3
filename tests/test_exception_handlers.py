from fastapi.testclient import TestClient
from fastapi import APIRouter
from pytest import LogCaptureFixture
import logging
import traceback

from feedreader3.main import app


def test_global_exception_handler(
    client: TestClient, caplog: LogCaptureFixture
) -> None:
    router = APIRouter(prefix="/tests")

    ERROR_MESSAGE = "Error from API"

    @router.get("/exception")
    async def throw_exception() -> None:
        raise RuntimeError(ERROR_MESSAGE)

    app.include_router(router)
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
                and r.message == ERROR_MESSAGE
            )
        ),
        None,
    )
    assert rec is not None
    assert rec.exc_info is not None
    exc_type, exc_value, exc_tb = rec.exc_info
    assert exc_type is RuntimeError
    assert exc_value is not None
    assert str(exc_value) == ERROR_MESSAGE
    assert exc_tb is not None
    assert any(
        ("test_exception_handlers" in line and "throw_exception" in line)
        for line in traceback.format_exception(None, value=exc_value, tb=exc_tb)
    )
