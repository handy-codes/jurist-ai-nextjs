from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_templates():
    return {"message": "Templates endpoint"}

