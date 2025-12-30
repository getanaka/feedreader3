import logging
from fastapi import Request, Response


logger = logging.getLogger("uvicorn." + __name__)


async def global_exception_handler(request: Request, exc: Exception) -> Response:
    logger.exception(exc)
    return Response(status_code=500, content="Internal Server Error")
