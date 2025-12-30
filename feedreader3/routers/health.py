from fastapi import APIRouter


router = APIRouter(prefix="/health")


@router.get("")
async def check_health() -> dict[str, str]:
    return {"status": "healthy"}
